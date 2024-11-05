import tkinter as tk
from tkinter import ttk, filedialog
import subprocess
from ttkbootstrap import Style
import configparser
import os

def select_audio_file():
    file_path = filedialog.askopenfilename(
        filetypes=[("WAV files", "*.wav")],
        title="Choose WAV"
    )
    
    if file_path:
        audio_file_entry.config(state='normal')
        audio_file_entry.delete(0, tk.END)
        audio_file_entry.insert(0, file_path)
        audio_file_entry.config(state='readonly')
        update_config_file(audio_file=file_path)


def select_fdkaac_file():
    file_path = filedialog.askopenfilename(
        filetypes=[("Executable files", "*.exe")],
        title="Choose fdkaac Executable"
    )
    
    if file_path:
       
        file_path = file_path.replace("/", "\\\\")
        fdkaac_file_entry.config(state='normal')
        fdkaac_file_entry.delete(0, tk.END)
        fdkaac_file_entry.insert(0, file_path)
        fdkaac_file_entry.config(state='readonly')
        update_config_file(fdkaac=file_path)


def update_config_file(audio_file=None, fdkaac=None, song_name=None):
    config = configparser.ConfigParser()

    if os.path.exists("config.txt"):
        with open("config.txt", "r") as config_file:
            first_line = config_file.readline().strip()
            if not first_line.startswith("["):
                content = config_file.read()
                with open("config.txt", "w") as config_file:
                    config_file.write("[DEFAULT]\n")
                    if audio_file:
                        config_file.write(f"INPUTAUDIO={audio_file}\n")
                    if fdkaac:
                        config_file.write(f"FDKAAC={fdkaac}\n")
                    if song_name:
                        config_file.write(f"SONGNAME={song_name}\n")
                    config_file.write(content)
            else:
                config.read("config.txt")
                if "DEFAULT" not in config:
                    config["DEFAULT"] = {}
                if audio_file:
                    config["DEFAULT"]["INPUTAUDIO"] = audio_file
                if fdkaac:
                    config["DEFAULT"]["FDKAAC"] = fdkaac
                if song_name:
                    config["DEFAULT"]["SONGNAME"] = song_name
                with open("config.txt", "w") as config_file:
                    config.write(config_file)
    else:
        config["DEFAULT"] = {}
        if audio_file:
            config["DEFAULT"]["INPUTAUDIO"] = audio_file
        if fdkaac:
            config["DEFAULT"]["FDKAAC"] = fdkaac
        if song_name:
            config["DEFAULT"]["SONGNAME"] = song_name
        with open("config.txt", "w") as config_file:
            config.write(config_file)

def run_script(script_name):
    if os.path.exists(f"{script_name}.py"):
        subprocess.call(["python", f"{script_name}.py"])
    elif os.path.exists(f"{script_name}.exe"):
        subprocess.call([f"{script_name}.exe"])
    else:
        print(f"Ни {script_name}.py, ни {script_name}.exe не найдены.")

def run_merge():
    run_script("merge")

def run_pagegen():
    run_script("pagegen")

def run_qrcamera():
    run_script("qrcamera")

def run_qrdecode():
    run_script("qrdecode")

def run_qrencode():
    run_script("qrencode")

def run_qrpagedecode():
    run_script("qrpagedecode")

def run_convert():
    run_script("fdkaac/convert")

def run_convert8k():
    run_script("fdkaac/convert8k")

def update_song_name(*args):
    song_name = song_name_var.get()[:2]
    song_name_var.set(song_name)
    update_config_file(song_name=song_name)

root = tk.Tk()
root.title("HENKANKI ENCODER")

style = Style(theme="sandstone")

mainframe = ttk.Frame(root, padding="10 10 10 10")
mainframe.grid(column=0, row=0, sticky=(tk.W, tk.E, tk.N, tk.S))

root.columnconfigure(0, weight=1)
root.rowconfigure(0, weight=1)

ttk.Button(mainframe, text="CHOOSE INPUT WAV", command=select_audio_file, style="Accent.TButton").grid(column=1, row=0, pady=10, padx=10, sticky=(tk.W, tk.E))

audio_file_entry = ttk.Entry(mainframe, width=50, state='readonly')
audio_file_entry.grid(column=2, row=0, pady=10, padx=10, sticky=(tk.W, tk.E))

ttk.Button(mainframe, text="CHOOSE FDKAAC EXE", command=select_fdkaac_file, style="Accent.TButton").grid(column=1, row=1, pady=10, padx=10, sticky=(tk.W, tk.E))

fdkaac_file_entry = ttk.Entry(mainframe, width=50, state='readonly')
fdkaac_file_entry.grid(column=2, row=1, pady=10, padx=10, sticky=(tk.W, tk.E))

song_name_var = tk.StringVar()
song_name_var.trace("w", update_song_name)

ttk.Label(mainframe, text="SONG NAME (2 CHARS)").grid(column=1, row=2, pady=10, padx=10, sticky=tk.W)
song_name_entry = ttk.Entry(mainframe, width=5, textvariable=song_name_var)
song_name_entry.grid(column=2, row=2, pady=10, padx=10, sticky=tk.W)

ttk.Button(mainframe, text="1. AUDIO TO FILES (16 kbps)", command=run_convert, style="Accent.TButton").grid(column=0, row=0, pady=10, padx=10, sticky=(tk.W, tk.E))

ttk.Button(mainframe, text="1. AUDIO TO FILES (8 kbps)", command=run_convert8k, style="Accent.TButton").grid(column=0, row=1, pady=10, padx=10, sticky=(tk.W, tk.E))

ttk.Button(mainframe, text="2. FILES to QR CHUNKS", command=run_qrencode, style="Accent.TButton").grid(column=0, row=2, pady=10, padx=10, sticky=(tk.W, tk.E))
ttk.Button(mainframe, text="3. QR CHUNKS to PAGES", command=run_pagegen, style="Accent.TButton").grid(column=0, row=3, pady=10, padx=10, sticky=(tk.W, tk.E))
ttk.Button(mainframe, text="4. PAGES to FILES", command=run_qrpagedecode, style="Accent.TButton").grid(column=0, row=4, pady=10, padx=10, sticky=(tk.W, tk.E))
ttk.Button(mainframe, text="5. FILES TO AUDIO", command=run_merge, style="Accent.TButton").grid(column=0, row=5, pady=10, padx=10, sticky=(tk.W, tk.E))
ttk.Button(mainframe, text="CAMERA", command=run_qrcamera, style="Accent.TButton").grid(column=0, row=6, pady=10, padx=10, sticky=(tk.W, tk.E))
ttk.Button(mainframe, text="QR CHUNKS to FILES", command=run_qrdecode, style="Accent.TButton").grid(column=0, row=7, pady=10, padx=10, sticky=(tk.W, tk.E))

root.mainloop()