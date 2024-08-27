import tkinter as tk
from tkinter import ttk, filedialog
import subprocess
from ttkbootstrap import Style
import configparser
import os

# Функция для выбора файла и обновления config.txt
def select_audio_file():
    # Открытие диалогового окна выбора файла
    file_path = filedialog.askopenfilename(
        filetypes=[("WAV files", "*.wav")],
        title="Выберите аудиофайл WAV"
    )
    
    if file_path:
        # Обновление текстового поля с путём к файлу
        audio_file_entry.config(state='normal')
        audio_file_entry.delete(0, tk.END)
        audio_file_entry.insert(0, file_path)
        audio_file_entry.config(state='readonly')
        
        # Обновление пути к аудиофайлу в config.txt
        config = configparser.ConfigParser()

        # Если файл существует, проверяем его содержимое
        if os.path.exists("config.txt"):
            with open("config.txt", "r") as config_file:
                first_line = config_file.readline().strip()
                # Проверяем, есть ли хедер, если нет, добавляем его
                if not first_line.startswith("["):
                    content = config_file.read()
                    with open("config.txt", "w") as config_file:
                        config_file.write("[DEFAULT]\n")
                        config_file.write(f"INPUTAUDIO={file_path}\n")
                        config_file.write(content)
                else:
                    # Читаем и обновляем конфиг
                    config.read("config.txt")
                    if "DEFAULT" not in config:
                        config["DEFAULT"] = {}
                    config["DEFAULT"]["INPUTAUDIO"] = file_path
                    with open("config.txt", "w") as config_file:
                        config.write(config_file)
        else:
            # Создаём новый конфиг файл с нужной секцией
            config["DEFAULT"] = {"INPUTAUDIO": file_path}
            with open("config.txt", "w") as config_file:
                config.write(config_file)

# Функции для запуска скриптов
def run_merge():
    subprocess.call(["python", "merge.py"])

def run_pagegen():
    subprocess.call(["python", "pagegen.py"])

def run_qrcamera():
    subprocess.call(["python", "qrcamera.py"])

def run_qrdecode():
    subprocess.call(["python", "qrdecode.py"])

def run_qrencode():
    subprocess.call(["python", "qrencode.py"])

def run_qrpagedecode():
    subprocess.call(["python", "qrpagedecode.py"])

def run_convert():
    subprocess.call(["python", "fdkaac/convert.py"])

# Создание основного окна
root = tk.Tk()
root.title("QR2AUDIO")

# Настройка стиля/темы
style = Style(theme="superhero")

# Создание фрейма для расположения кнопок
mainframe = ttk.Frame(root, padding="10 10 10 10")
mainframe.grid(column=0, row=0, sticky=(tk.W, tk.E, tk.N, tk.S))

# Устанавливаем сетку для авто-выравнивания
root.columnconfigure(0, weight=1)
root.rowconfigure(0, weight=1)

# Создание и размещение кнопок с улучшенным стилем
ttk.Button(mainframe, text="1. AUDIO TO FILES", command=run_convert, style="Accent.TButton").grid(column=0, row=0, pady=10, padx=10, sticky=(tk.W, tk.E))

# Создаём кнопку для выбора файла
ttk.Button(mainframe, text="Выбрать WAV файл", command=select_audio_file, style="Accent.TButton").grid(column=1, row=0, pady=10, padx=10, sticky=(tk.W, tk.E))

# Создаём текстовое поле для отображения пути к выбранному аудиофайлу
audio_file_entry = ttk.Entry(mainframe, width=50, state='readonly')
audio_file_entry.grid(column=2, row=0, pady=10, padx=10, sticky=(tk.W, tk.E))

ttk.Button(mainframe, text="2. FILES to QR CHUNKS", command=run_qrencode, style="Accent.TButton").grid(column=0, row=1, pady=10, padx=10, sticky=(tk.W, tk.E))
ttk.Button(mainframe, text="3. QR CHUNKS to PAGES", command=run_pagegen, style="Accent.TButton").grid(column=0, row=2, pady=10, padx=10, sticky=(tk.W, tk.E))
ttk.Button(mainframe, text="4. PAGES to FILES", command=run_qrpagedecode, style="Accent.TButton").grid(column=0, row=3, pady=10, padx=10, sticky=(tk.W, tk.E))
ttk.Button(mainframe, text="5. FILES TO AUDIO", command=run_merge, style="Accent.TButton").grid(column=0, row=4, pady=10, padx=10, sticky=(tk.W, tk.E))
ttk.Button(mainframe, text="CAMERA", command=run_qrcamera, style="Accent.TButton").grid(column=0, row=5, pady=10, padx=10, sticky=(tk.W, tk.E))
ttk.Button(mainframe, text="QR CHUNKS to FILES", command=run_qrdecode, style="Accent.TButton").grid(column=0, row=6, pady=10, padx=10, sticky=(tk.W, tk.E))

# Запуск главного цикла обработки событий
root.mainloop()