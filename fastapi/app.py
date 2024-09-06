from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
import os
from collections import defaultdict
from fastapi.templating import Jinja2Templates
from fastapi import Request
from pyzbar.pyzbar import decode, ZBarSymbol
import struct
import base64
import binascii
from pydub import AudioSegment
from io import BytesIO
from PIL import Image

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

UPLOAD_FOLDER = 'uploaded_pages'
OUTPUT_FOLDER = 'output_files'
TO_MERGE_FOLDER = 'tomerge'

# Создание необходимых директорий, если их не существует
for folder in [UPLOAD_FOLDER, OUTPUT_FOLDER, TO_MERGE_FOLDER]:
    if not os.path.exists(folder):
        os.makedirs(folder)

def fix_base64_padding(qr_data):
    while len(qr_data) % 4 != 0:
        qr_data += '='
    return qr_data

def remove_header(chunk_with_header):
    header_size = struct.calcsize('>IIB')
    chunk_number, total_chunks, file_name_length = struct.unpack('>IIB', chunk_with_header[:header_size])
    file_name = chunk_with_header[header_size:header_size+file_name_length].decode('ascii')
    file_ext_offset = header_size + file_name_length
    file_ext_size = struct.calcsize('3s')
    file_ext = chunk_with_header[file_ext_offset:file_ext_offset+file_ext_size].decode('ascii')
    chunk_offset = file_ext_offset + file_ext_size
    chunk = chunk_with_header[chunk_offset:]
    return chunk, chunk_number, total_chunks, file_name.strip(), file_ext.strip()

def read_qr_codes_from_image(image_data):
    image = Image.open(BytesIO(image_data))
    decoded_objects = decode(image, symbols=[ZBarSymbol.QRCODE])
    return [obj.data.decode('utf-8') for obj in decoded_objects]

def merge_audio_files():
    files = [f for f in os.listdir(TO_MERGE_FOLDER) if f.endswith('.m4a')]
    file_groups = defaultdict(list)
    for file in files:
        prefix = file[:2]
        file_groups[prefix].append(file)

    for prefix, group_files in file_groups.items():
        group_files.sort(key=lambda x: int(x[2:6]))
        combined = AudioSegment.empty()
        crossfade_duration = 240
        for i, file in enumerate(group_files):
            file_path = os.path.join(TO_MERGE_FOLDER, file)
            audio = AudioSegment.from_file(file_path, format='m4a')
            if i == 0:
                combined = audio
            else:
                combined = combined.append(audio, crossfade=crossfade_duration)

        temp_output_file = f"{prefix}_temp.mp4"
        temp_output_path = os.path.join(TO_MERGE_FOLDER, temp_output_file)
        combined.export(temp_output_path, format='mp4')

        final_output_file = f"{prefix}.aac"
        final_output_path = os.path.join(TO_MERGE_FOLDER, final_output_file)

        if os.path.exists(final_output_path):
            os.remove(final_output_path)

        os.system(f"ffmpeg -y -i {temp_output_path} -acodec aac {final_output_path}")
        os.remove(temp_output_path)

    for file in group_files:
        os.remove(os.path.join(TO_MERGE_FOLDER, file))

    return final_output_file

@app.get("/")
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/upload")
async def upload_files(files: list[UploadFile] = File(...)):
    total_files = len(files)
    processed_files = 0

    files_data = defaultdict(lambda: {
        "decoded_chunks": defaultdict(lambda: None),
        "total_chunks": None,
        "file_name": "",
        "file_ext": "",
    })

    for file in files:
        file_path = os.path.join(UPLOAD_FOLDER, file.filename)
        with open(file_path, 'wb') as f:
            f.write(await file.read())

        with open(file_path, 'rb') as f:
            image_data = f.read()

        qr_data_list = read_qr_codes_from_image(image_data)
        for qr_data in qr_data_list:
            try:
                qr_data = fix_base64_padding(qr_data)
                chunk_with_header = base64.b64decode(qr_data)
                chunk, chunk_number, total_chunks, file_name, file_ext = remove_header(chunk_with_header)

                file_key = (file_name, file_ext)
                if files_data[file_key]["total_chunks"] is None:
                    files_data[file_key]["total_chunks"] = total_chunks
                    files_data[file_key]["file_name"] = file_name
                    files_data[file_key]["file_ext"] = file_ext

                if files_data[file_key]["decoded_chunks"][chunk_number] is None:
                    files_data[file_key]["decoded_chunks"][chunk_number] = chunk

            except (binascii.Error, struct.error) as e:
                raise HTTPException(status_code=400, detail=f"Ошибка при обработке QR-кода: {e}")

        processed_files += 1

    for file_key, data in files_data.items():
        if data["total_chunks"] is not None and all(data["decoded_chunks"][i] is not None for i in range(data["total_chunks"])):
            sorted_chunks = [data["decoded_chunks"][i] for i in range(data["total_chunks"])]
            output_file_name = f"{data['file_name']}.{data['file_ext']}"
            output_file_path = os.path.join(TO_MERGE_FOLDER, output_file_name)

            if os.path.exists(output_file_path):
                os.remove(output_file_path)

            try:
                with open(output_file_path, 'wb') as output_file:
                    for chunk in sorted_chunks:
                        output_file.write(chunk)
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"Ошибка при записи файла: {e}")

    final_output_file = merge_audio_files()
    return {"success": True, "message": f"Файлы успешно загружены и обработаны. Обработано страниц: {processed_files} из {total_files}", "download_url": f'/download/{os.path.basename(final_output_file)}'}

@app.get("/download/{filename}")
async def download_file(filename: str):
    file_path = os.path.join(TO_MERGE_FOLDER, filename)
    if os.path.exists(file_path):
        return FileResponse(path=file_path, filename=filename, media_type='application/octet-stream')
    raise HTTPException(status_code=404, detail="Файл не найден")