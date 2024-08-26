import sys
import os
import cv2
import struct
import base64
from collections import defaultdict, namedtuple
from pyzbar.pyzbar import decode, ZBarSymbol
import binascii

FileChunk = namedtuple("FileChunk", ["chunks", "total_chunks", "file_name", "file_ext"])

def fix_base64_padding(qr_data):
    """Исправляет недостающий padding для base64 строки."""
    while len(qr_data) % 4 != 0:
        qr_data += '='
    return qr_data

def remove_header(chunk_with_header):
    """Удаляет хедер из чанка."""
    header_size = struct.calcsize('>IIB')
    chunk_number, total_chunks, file_name_length = struct.unpack('>IIB', chunk_with_header[:header_size])
    header = chunk_with_header[:header_size + file_name_length + 3]
    chunk = chunk_with_header[header_size + file_name_length + 3:]
    
    file_name = struct.unpack(f'{file_name_length}s', header[9:9 + file_name_length])[0].decode('ascii').strip()
    file_ext = struct.unpack('3s', header[9 + file_name_length:9 + file_name_length + 3])[0].decode('ascii').strip()

    return chunk, chunk_number, total_chunks, file_name.strip(), file_ext.strip()

def read_qr_code(frame):
    """Считывает QR код с изображения."""
    decoded_objects = decode(frame, symbols=[ZBarSymbol.QRCODE])
    if decoded_objects:
        return decoded_objects[0].data.decode('utf-8')
    return None

def assemble_file(file_chunks):
    sorted_chunks = [file_chunks.chunks[i] for i in range(file_chunks.total_chunks)]
    file_name_with_ext = f"{file_chunks.file_name}.{file_chunks.file_ext}"
    try:
        with open(file_name_with_ext, 'wb') as output_file:
            for chunk in sorted_chunks:
                output_file.write(chunk)
        print(f"Файл успешно восстановлен: {file_name_with_ext}")
    except Exception as e:
        print(f"Ошибка при записи файла: {e}")

def main():
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Не удалось открыть камеру.")
        return

    files_data = defaultdict(lambda: FileChunk(defaultdict(lambda: None), None, "", ""))
    
    while True:
        ret, frame = cap.read()
        if not ret:
            print("Не удалось получить кадр.")
            break

        qr_data = read_qr_code(frame)
        if qr_data:
            try:
                qr_data = fix_base64_padding(qr_data)
                chunk_with_header = base64.b64decode(qr_data)
                chunk, chunk_number, total_chunks, file_name, file_ext = remove_header(chunk_with_header)
                file_key = (file_name, file_ext)
                
                if files_data[file_key].chunks[chunk_number] is None:
                    files_data[file_key].chunks[chunk_number] = chunk
                    files_data[file_key] = files_data[file_key]._replace(total_chunks=total_chunks, file_name=file_name, file_ext=file_ext)
                    print(f"Файл: {file_name}.{file_ext} - Дешифрован чанк {chunk_number} из {total_chunks}.")
                
                    remaining_chunks = total_chunks - sum(1 for v in files_data[file_key].chunks.values() if v is not None)
                    if remaining_chunks < 10:
                        remaining_chunk_numbers = [i for i in range(total_chunks) if files_data[file_key].chunks[i] is None]
                        print(f"{file_name}.{file_ext} - Осталось отсканировать: {remaining_chunks}, Чанки: {remaining_chunk_numbers}")
                    else:
                        print(f"{file_name}.{file_ext} - Осталось отсканировать: {remaining_chunks}")
                    
                    # Проверяем, все ли чанки готовы
                    if all(files_data[file_key].chunks[i] is not None for i in range(total_chunks)):
                        assemble_file(files_data[file_key])
                        del files_data[file_key]
            except (binascii.Error, struct.error) as e:
                print(f"Ошибка при обработке QR-кода: {e}")
        
        cv2.imshow('Камера', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()