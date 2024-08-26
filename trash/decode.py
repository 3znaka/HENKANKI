import os
import struct
import base64
from pyzxing import BarCodeReader

def read_aztec_code(image_path):
    """Считывает Aztec код с изображения."""
    reader = BarCodeReader()
    barcode = reader.decode(image_path)
    if barcode:
        return barcode[0].get('raw', '')
    return None

def remove_header(chunk_with_header):
    """Удаляет хедер из чанка."""
    header_size = struct.calcsize('>IIB6s3s')
    header = chunk_with_header[:header_size]
    chunk = chunk_with_header[header_size:]
    
    chunk_number, total_chunks, file_name_length = struct.unpack('>IIB', header[:9])
    file_name = struct.unpack(f'{file_name_length}s', header[9:9+file_name_length])[0].decode('ascii').strip()
    file_ext = header[9+file_name_length:].decode('ascii').strip()
    
    return chunk, chunk_number, total_chunks, file_name.strip(), file_ext.strip()

def main():
    input_dir = "aztec_codes"
    decoded_chunks = {}

    # Получаем список файлов в директории
    aztec_files = sorted(os.listdir(input_dir))

    # Расшифровываем все чанк-коды и сохраняем их
    for aztec_file in aztec_files:
        aztec_file_path = os.path.join(input_dir, aztec_file)
        encoded_data = read_aztec_code(aztec_file_path)
        if encoded_data:
            chunk_with_header = base64.b64decode(encoded_data)
            chunk, chunk_number, total_chunks, file_name, file_ext = remove_header(chunk_with_header)
            decoded_chunks[chunk_number] = chunk
            print(f"Дешифровано {chunk_number + 1} из {total_chunks}.")

    # Сортируем чанки по порядковым номерам и собираем файл
    sorted_chunks = [decoded_chunks[i] for i in sorted(decoded_chunks.keys())]

    output_file_name = f"{file_name}.{file_ext}"
    with open(output_file_name, 'wb') as output_file:
        for chunk in sorted_chunks:
            output_file.write(chunk)

    print(f"Файл успешно восстановлен: {output_file_name}")

if __name__ == "__main__":
    main()