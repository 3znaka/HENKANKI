import uvicorn
from fastapi import FastAPI, Request, UploadFile, File
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from pyzbar.pyzbar import decode, ZBarSymbol
import cv2
import base64
import struct
from collections import defaultdict, namedtuple
import numpy as np
import os
from fastapi.staticfiles import StaticFiles

FileChunk = namedtuple("FileChunk", ["chunks", "total_chunks", "file_name", "file_ext"])

app = FastAPI()
templates = Jinja2Templates(directory="templates")

files_data = defaultdict(lambda: FileChunk(defaultdict(lambda: None), None, "", ""))

def fix_base64_padding(qr_data):
    while len(qr_data) % 4 != 0:
        qr_data += '='
    return qr_data

def remove_header(chunk_with_header):
    header_size = struct.calcsize('>IIB')
    chunk_number, total_chunks, file_name_length = struct.unpack('>IIB', chunk_with_header[:header_size])
    header = chunk_with_header[:header_size + file_name_length + 3]
    chunk = chunk_with_header[header_size + file_name_length + 3:]

    file_name = struct.unpack(f'{file_name_length}s', header[9:9 + file_name_length])[0].decode('ascii').strip()
    file_ext = struct.unpack('3s', header[9 + file_name_length:9 + file_name_length + 3])[0].decode('ascii').strip()

    return chunk, chunk_number, total_chunks, file_name.strip(), file_ext.strip()

def assemble_file(file_chunks):
    sorted_chunks = [file_chunks.chunks[i] for i in range(file_chunks.total_chunks)]
    file_name_with_ext = f"{file_chunks.file_name}.{file_chunks.file_ext}"
    directory = 'tomerge'
    file_path = os.path.join(directory, file_name_with_ext)

    try:
        if not os.path.exists(directory):
            os.makedirs(directory)

        with open(file_path, 'wb') as output_file:
            for chunk in sorted_chunks:
                output_file.write(chunk)
        print(f"Файл успешно восстановлен: {file_path}")
        return file_path
    except Exception as e:
        print(f"Ошибка при записи файла: {e}")
        return None

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/upload/")
async def upload_qr(file: UploadFile = File(...)):
    try:
        img = cv2.imdecode(np.frombuffer(await file.read(), np.uint8), cv2.IMREAD_COLOR)
        qr_data = decode(img, symbols=[ZBarSymbol.QRCODE])

        if qr_data:
            qr_content = qr_data[0].data.decode('utf-8')
            qr_content = fix_base64_padding(qr_content)
            chunk_with_header = base64.b64decode(qr_content)
            chunk, chunk_number, total_chunks, file_name, file_ext = remove_header(chunk_with_header)
            file_key = (file_name, file_ext)

            if files_data[file_key].chunks[chunk_number] is None:
                files_data[file_key].chunks[chunk_number] = chunk
                files_data[file_key] = files_data[file_key]._replace(total_chunks=total_chunks, file_name=file_name, file_ext=file_ext)
                
                remaining_chunks = total_chunks - sum(1 for v in files_data[file_key].chunks.values() if v is not None)
                response_content = {'status': 'success', 'remaining_chunks': remaining_chunks}
                if all(files_data[file_key].chunks[i] is not None for i in range(total_chunks)):
                    file_path = assemble_file(files_data[file_key])
                    if file_path:
                        response_content['file_url'] = f"/download/{os.path.basename(file_path)}"
                    del files_data[file_key]

                return JSONResponse(content=response_content)

    except Exception as e:
        return JSONResponse(content={'status': 'error', 'message': str(e)})

app.mount("/download", StaticFiles(directory="tomerge"), name="download")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)