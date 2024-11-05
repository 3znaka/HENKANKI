import configparser
from pydub import AudioSegment
import subprocess
import os

# Загрузка конфигурации из файла config.txt
config = configparser.ConfigParser()
config.read('./config.txt')

# Получение входного файла из переменной INPUTAUDIO
input_file = config['DEFAULT']['INPUTAUDIO']

# Длительность отрезка в миллисекундах (15 секунд) и дополнительно 200 мс для перекрытия
segment_duration = 5 * 1000
overlap_duration = 200  # 200 миллисекунд
total_segment_duration = segment_duration + overlap_duration

# Ввод первых двух символов от пользователя
prefix = config['DEFAULT']['SONGNAME']

# Загрузка аудиофайла
try:
    audio = AudioSegment.from_wav(input_file)
except Exception as e:
    print(f"Error loading audio file: {e}")
    exit(1)

# Директория для выходных файлов
output_dir = "inputfiles"
os.makedirs(output_dir, exist_ok=True)

# Путь к fdkaac исполнителю
fdkaac_path = config['DEFAULT']['FDKAAC']  # Замените на актуальный путь

# Проверка наличия файла fdkaac
if not os.path.isfile(fdkaac_path):
    print(f"fdkaac not found at {fdkaac_path}")
    exit(1)

if len(audio) <= segment_duration:
    # Если файл короче 15 секунд, конвертируем его целиком
    output_file = os.path.join(output_dir, f"{prefix}0000.m4a")
    temp_wav = f"{prefix}0000.wav"
    
    # Сохранение полного аудиофайла
    audio.export(temp_wav, format="wav")
    
    # Команда для кодировки
    command = [
        fdkaac_path, 
        '-S', 
        '-p', '29',
        '-b', '16k',
        '--bandwidth', '8000',
        '-o', output_file,
        temp_wav
    ]
    
    # Выполнение команды
    result = subprocess.run(command, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Error encoding file: {result.stderr}")
    
    # Удаление временного файла
    os.remove(temp_wav)
else:
    # Количество сегментов
    num_segments = len(audio) // segment_duration + (1 if len(audio) % segment_duration else 0)
    
    # Директория для временных отрезков
    temp_dir = "temp_segments"
    os.makedirs(temp_dir, exist_ok=True)
    
    # Создание и кодирование сегментов
    for i in range(num_segments):
        start_time = i * segment_duration
        end_time = start_time + total_segment_duration
        
        # Защита от выхода за пределы длины аудиофайла
        if end_time > len(audio):
            end_time = len(audio)
        
        segment = audio[start_time:end_time]
        segment_name = f"{prefix}{str(i).zfill(4)}.wav"
        segment_path = os.path.join(temp_dir, segment_name)
        
        # Сохранение сегмента
        segment.export(segment_path, format="wav")
        
        # Обновленный путь для итогового файла
        output_file = os.path.join(output_dir, f"{prefix}{str(i).zfill(4)}.m4a")
        
        # Команда для кодировки
        command = [
            fdkaac_path, 
            '-S', 
            '-p', '29',
            '-b', '16k',
            '--bandwidth', '8000',
            '-o', output_file,
            segment_path
        ]
        
        # Выполнение команды
        result = subprocess.run(command, capture_output=True, text=True)
        if result.returncode != 0:
            print(f"Error encoding segment {i + 1}: {result.stderr}")
        else:
            print(f"Segment {i + 1}/{num_segments} encoded successfully.")
    
    # Очистка временных сегментных файлов
    for file in os.listdir(temp_dir):
        os.remove(os.path.join(temp_dir, file))
    
    # Удаление временной директории
    os.rmdir(temp_dir)

print("Процесс завершен!")