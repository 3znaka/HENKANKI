import os
from pydub import AudioSegment

# Путь к папке с аудиофайлами
folder_path = "tomerge"

# Получение всех файлов из папки
files = [f for f in os.listdir(folder_path) if f.endswith('.m4a')]

# Словарь для хранения аудиофайлов по их префиксу
file_groups = {}

# Группировка файлов по префиксу
for file in files:
    prefix = file[:2]
    if prefix not in file_groups:
        file_groups[prefix] = []
    file_groups[prefix].append(file)

# Перебор всех групп и их объединение
for prefix, group_files in file_groups.items():
    # Сортировка файлов в группе по их порядковому номеру
    group_files.sort(key=lambda x: int(x[2:6]))
    
    # Объединение аудиофайлов в один с использованием crossfade
    combined = AudioSegment.empty()
    crossfade_duration = 240  # Длительность перекрёстного перехода (fading) в миллисекундах
    
    for i, file in enumerate(group_files):
        file_path = os.path.join(folder_path, file)
        audio = AudioSegment.from_file(file_path, format='m4a')
        
        if i == 0:
            combined = audio
        else:
            combined = combined.append(audio, crossfade=crossfade_duration)

    # Экспорт временного объединенного файла в формате mp4
    temp_output_file = f"{prefix}_temp.mp4"
    temp_output_path = os.path.join(folder_path, temp_output_file)
    combined.export(temp_output_path, format='mp4')

    # Конвертация временного mp4 файла в aac
    final_output_file = f"{prefix}.aac"
    final_output_path = os.path.join(folder_path, final_output_file)
    os.system(f"ffmpeg -i {temp_output_path} -acodec aac {final_output_path}")

    # Удаление временного mp4 файла
    os.remove(temp_output_path)

    # Удаление исходных файлов
    for file in group_files:
        os.remove(os.path.join(folder_path, file))

print("Объединение и удаление исходных файлов завершено.")