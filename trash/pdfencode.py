import os
import struct
import base64
import pdf417

def split_file(file_path, chunk_size=600):
    """Разбивает файл на блоки размером chunk_size байт."""
    with open(file_path, 'rb') as f:
        chunks = []
        while (chunk := f.read(chunk_size)):
            chunks.append(chunk)
    return chunks

def create_pdf417_code(data, output_path):
    """Создает PDF417 код из данных и сохраняет его в output_path."""
    codes = pdf417.encode(data, columns=10)
    image = pdf417.render_image(codes)  # Создаем изображение
    image.save(output_path)

def add_header(chunk, chunk_number, total_chunks, file_name, file_ext):
    """Добавляет хедер к каждому чанку."""
    header = struct.pack('>IIB6s3s', chunk_number, total_chunks, len(file_name), file_name.encode('ascii'), file_ext.encode('ascii'))
    return header + chunk

def main(file_path):
    output_dir = "pdf417_codes"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Получаем основную информацию о файле
    file_name, file_ext = os.path.splitext(os.path.basename(file_path))
    file_ext = file_ext[1:]  # Убираем точку из расширения

    # Ограничения формата
    file_name = (file_name[:6]).ljust(6)  # Название до 6 символов, дополняем пробелами если меньше
    file_ext = (file_ext[:3]).ljust(3)  # Расширение до 3 символов

    # Читаем и разбиваем файл на чанки
    chunks = split_file(file_path)
    total_chunks = len(chunks)

    for chunk_number, chunk in enumerate(chunks):
        chunk_with_header = add_header(chunk, chunk_number, total_chunks, file_name, file_ext)
        chunk_base64 = base64.b64encode(chunk_with_header).decode('ascii')
        output_path = os.path.join(output_dir, f"pdf417_code_{chunk_number}.png")
        create_pdf417_code(chunk_base64, output_path)
        print(f'Чанк {chunk_number} создан и сохранен в {output_path}.')

if __name__ == "__main__":
    file_path = "track1.aac"  # Укажите путь к файлу
    main(file_path)