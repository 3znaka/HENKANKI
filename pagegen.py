import os
from PIL import Image, ImageDraw

# Путь к папке с изображениями
input_folder = 'qr_codes'
output_folder = 'output_pages'

# Создаем выходную папку, если она не существует
os.makedirs(output_folder, exist_ok=True)

# Задайте максимальное количество столбцов и рядов
cols = 3
rows = 4
images_per_page = cols * rows

# Получение списка изображений
image_files = [f for f in os.listdir(input_folder) if f.lower().endswith(('png', 'jpg', 'jpeg'))]

# Функция для создания новой пустой страницы
def create_empty_page(image_width, image_height):
    page_width = image_width * cols
    page_height = image_height * rows
    new_page = Image.new('RGB', (page_width, page_height), 'white')
    return new_page

# Обработка изображений
page_number = 0
for i in range(0, len(image_files), images_per_page):
    images_chunk = image_files[i:i+images_per_page]
    
    # Открываем одно изображение, чтобы узнать его размеры
    sample_image = Image.open(os.path.join(input_folder, images_chunk[0]))
    image_width, image_height = sample_image.size

    # Создаем пустую страницу
    new_page = create_empty_page(image_width, image_height)

    # Добавляем изображения на страницу
    for index, image_file in enumerate(images_chunk):
        img = Image.open(os.path.join(input_folder, image_file))
        col = index % cols
        row = index // cols
        # Координаты для вставки изображения
        x = col * image_width
        y = row * image_height
        new_page.paste(img, (x, y))

    # Сохраняем текущую страницу
    page_filename = os.path.join(output_folder, f'page_{page_number}.png')
    new_page.save(page_filename)
    
    # Выводим информацию о созданной странице в консоль
    print(f'Страница {page_number} создана и сохранена как {page_filename}')
    
    page_number += 1

print("Процесс завершен. Страницы сохранены в папке 'output_pages'.")