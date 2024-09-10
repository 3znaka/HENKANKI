import os
import struct
import base64
import qrcode
from PIL import Image, ImageDraw, ImageFont

def split_file(file_path, chunk_size=1060):
    """Разбивает файл на блоки размером chunk_size байт."""
    with open(file_path, 'rb') as f:
        chunks = []
        while (chunk := f.read(chunk_size)):
            chunks.append(chunk)
    return chunks

def create_qr_code(data, output_path, chunk_number, file_name, total_chunks):
    """Создает QR код из данных и сохраняет его с номером чанка."""
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=10,
        border=3,
    )
    qr.add_data(data)
    qr.make(fit=True)
    img = qr.make_image(fill='black', back_color='white')

    # Создаем изображение с дополнительным пространством для номера чанка
    img_width, img_height = img.size
    total_height = img_height + 30  # 30 пикселей для номеров чанков
    result_img = Image.new('RGB', (img_width, total_height), 'white')
    result_img.paste(img, (0, 0))

    # Рендерим номер чанка под QR кодом
    draw = ImageDraw.Draw(result_img)
    try:
        font = ImageFont.truetype("arial.ttf", 42)
    except IOError:
        font = ImageFont.load_default()
    text = f"{file_name} {chunk_number}/{total_chunks}"  
    text_width = draw.textlength(text, font=font)
    text_position = ((img_width - text_width) // 2, img_height - 20)
    draw.text(text_position, text, font=font, fill="black")

    result_img.save(output_path)

def add_header(chunk, chunk_number, total_chunks, file_name, file_ext):
    """Добавляет хедер к каждому чанку."""
    header = struct.pack('>IIB6s3s', chunk_number, total_chunks, len(file_name), file_name.encode('ascii'), file_ext.encode('ascii'))
    return header + chunk

def process_files(input_dir, output_dir):
    # Убедитесь, что директория для выходных файлов существует
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # Получаем список всех файлов в директории inputfiles
    for file_name in os.listdir(input_dir):
        file_path = os.path.join(input_dir, file_name)
        if os.path.isfile(file_path):
            file_name_no_ext, file_ext = os.path.splitext(file_name)
            file_ext = file_ext[1:]  # Убираем точку из расширения

            # Ограничения формата
            file_name_trunc = (file_name_no_ext[:6]).ljust(6)  # Название до 6 символов, дополняем пробелами если меньше
            file_ext_trunc = (file_ext[:3]).ljust(3)  # Расширение до 3 символов

            # Читаем и разбиваем файл на чанки
            chunks = split_file(file_path)
            total_chunks = len(chunks)

            for chunk_number, chunk in enumerate(chunks):
                chunk_with_header = add_header(chunk, chunk_number, total_chunks, file_name_trunc, file_ext_trunc)
                chunk_base64 = base64.b64encode(chunk_with_header).decode('ascii')
                output_path = os.path.join(output_dir, f"{file_name_no_ext}_qr_code_{chunk_number}.png")
                create_qr_code(chunk_base64, output_path, chunk_number, f"{file_name_trunc}.{file_ext_trunc}".strip(), total_chunks)
                
                print(f'QR-код для чанка {chunk_number} файла {file_name_no_ext} создан и сохранён в {output_path}.')

def main():
    input_dir = "inputfiles"
    output_dir = "qr_codes"
    process_files(input_dir, output_dir)

if __name__ == "__main__":
    main()