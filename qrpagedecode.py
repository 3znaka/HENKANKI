import os
import cv2
import struct
import base64
from collections import defaultdict
from pyzbar.pyzbar import decode, ZBarSymbol
import binascii

def fix_base64_padding(qr_data):
    """Исправляет недостающий padding для base64 строки."""
    while len(qr_data) % 4 != 0:
        qr_data += '='
    return qr_data

def remove_header(chunk_with_header):
    """Удаляет хедер из чанка."""
    header_size = struct.calcsize('>IIB')
    chunk_number, total_chunks, file_name_length = struct.unpack('>IIB', chunk_with_header[:header_size])
    file_name = chunk_with_header[header_size:header_size+file_name_length].decode('ascii')
    file_ext_offset = header_size + file_name_length
    file_ext_size = struct.calcsize('3s')
    file_ext = chunk_with_header[file_ext_offset:file_ext_offset+file_ext_size].decode('ascii')
    chunk_offset = file_ext_offset + file_ext_size
    chunk = chunk_with_header[chunk_offset:]
    
    return chunk, chunk_number, total_chunks, file_name.strip(), file_ext.strip()

def read_qr_codes_from_image(image):
    """Считывает все QR коды с изображения."""
    decoded_objects = decode(image, symbols=[ZBarSymbol.QRCODE])
    return [obj.data.decode('utf-8') for obj in decoded_objects]

def main():
    image_folder = 'output_pages'
    output_folder = 'tomerge'
    
    if not os.path.exists(image_folder):
        print(f"Папка {image_folder} не существует.")
        return

    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    
    files_data = defaultdict(lambda: {
        "decoded_chunks": defaultdict(lambda: None),
        "total_chunks": None,
        "file_name": "",
        "file_ext": "",
    })
    
    for filename in os.listdir(image_folder):
        image_path = os.path.join(image_folder, filename)
        image = cv2.imread(image_path)
        if image is None:
            print(f"Не удалось загрузить изображение {image_path}.")
            continue

        qr_data_list = read_qr_codes_from_image(image)
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
                    print(f"Дешифровано {chunk_number} из {total_chunks} для файла {file_name}.{file_ext}")

                remaining_chunks = total_chunks - sum(1 for v in files_data[file_key]["decoded_chunks"].values() if v is not None)
                if remaining_chunks < 10:
                    remaining_chunk_numbers = [i for i in range(total_chunks) if files_data[file_key]["decoded_chunks"][i] is None]
                    print(f"Осталось отсканировать: {remaining_chunks} для файла {file_name}.{file_ext}, Чанки: {remaining_chunk_numbers}")
                else:
                    print(f"Осталось отсканировать: {remaining_chunks} для файла {file_name}.{file_ext}")

            except (binascii.Error, struct.error) as e:
                print(f"Ошибка при обработке QR-кода: {e}")

    for file_key, data in files_data.items():
        if data["total_chunks"] is not None and all(data["decoded_chunks"][i] is not None for i in range(data["total_chunks"])):
            # Обработали все чанки, собираем файл
            sorted_chunks = [data["decoded_chunks"][i] for i in range(data["total_chunks"])]
            
            output_file_name = f"{data['file_name']}.{data['file_ext']}"
            output_file_path = os.path.join(output_folder, output_file_name)
            try:
                with open(output_file_path, 'wb') as output_file:
                    for chunk in sorted_chunks:
                        output_file.write(chunk)
                print(f"Файл успешно восстановлен: {output_file_path}")
            except Exception as e:
                print(f"Ошибка при записи файла: {e}")

if __name__ == "__main__":
    main()