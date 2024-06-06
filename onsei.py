import tkinter as tk
from tkinter import ttk, filedialog
import pyaudio
import wave
import threading
import os


class VoiceRecorderApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Voice Recorder")
        self.text_index = 0
        self.sentences = self.load_sentences()

        self.is_recording = False
        self.frames = []
        self.save_folder = ""

        self.p = pyaudio.PyAudio()
        self.stream = None

        self.create_widgets()

    def create_widgets(self):
        self.label_frame = tk.Frame(self.root)
        self.label_frame.pack(pady=20)

        self.line_label = tk.Label(
            self.label_frame, text=f"{self.text_index + 1}番目: ", font=("Arial", 12)
        )
        self.line_label.pack(side=tk.LEFT)

        self.text_label = tk.Label(
            self.label_frame,
            text=self.sentences[self.text_index],
            wraplength=400,
            font=("Arial", 12),
        )
        self.text_label.pack(side=tk.LEFT)

        self.device_frame = tk.Frame(self.root)
        self.device_frame.pack(pady=10)

        self.device_label = tk.Label(
            self.device_frame, text="録音デバイス:", font=("Arial", 12)
        )
        self.device_label.pack(side=tk.LEFT, padx=5)

        self.device_combobox = ttk.Combobox(
            self.device_frame, state="readonly", font=("Arial", 12)
        )
        self.device_combobox.pack(side=tk.LEFT, padx=5)
        self.populate_devices()

        self.folder_button = tk.Button(
            self.device_frame,
            text="フォルダ選択",
            command=self.select_folder,
            font=("Arial", 12),
        )
        self.folder_button.pack(side=tk.LEFT, padx=5)

        self.button_frame = tk.Frame(self.root)
        self.button_frame.pack(pady=20)

        self.prev_button = tk.Button(
            self.button_frame,
            text="戻る",
            command=self.prev_sentence,
            font=("Arial", 12),
        )
        self.prev_button.pack(side=tk.LEFT, padx=10)

        self.start_button = tk.Button(
            self.button_frame,
            text="スタート",
            command=self.toggle_recording,
            font=("Arial", 12),
        )
        self.start_button.pack(side=tk.LEFT, padx=10)

        self.next_button = tk.Button(
            self.button_frame,
            text="次へ",
            command=self.next_sentence,
            font=("Arial", 12),
        )
        self.next_button.pack(side=tk.LEFT, padx=10)

    def load_sentences(self):
        with open(
            "C:/開発/音声文/extracted_sentences.txt", "r", encoding="utf-8"
        ) as file:
            sentences = file.readlines()
        return [sentence.strip() for sentence in sentences]

    def populate_devices(self):
        info = self.p.get_host_api_info_by_index(0)
        numdevices = info.get("deviceCount")
        devices = []
        for i in range(0, numdevices):
            if (
                self.p.get_device_info_by_host_api_device_index(0, i).get(
                    "maxInputChannels"
                )
            ) > 0:
                devices.append(
                    self.p.get_device_info_by_host_api_device_index(0, i).get("name")
                )
        self.device_combobox["values"] = devices
        if devices:
            self.device_combobox.current(0)

    def select_folder(self):
        self.save_folder = filedialog.askdirectory()
        if self.save_folder:
            print(f"Selected folder: {self.save_folder}")

    def toggle_recording(self):
        if self.is_recording:
            self.stop_recording()
            self.start_button.config(text="スタート")
        else:
            self.start_recording()
            self.start_button.config(text="ストップ")

    def start_recording(self):
        device_index = self.device_combobox.current()
        self.is_recording = True
        self.frames = []
        self.stream = self.p.open(
            format=pyaudio.paInt16,
            channels=1,
            rate=16000,  # Higher sampling rate
            input=True,
            input_device_index=device_index,
            frames_per_buffer=1024,
        )
        self.record_audio()

    def record_audio(self):
        if self.is_recording:
            data = self.stream.read(1024)
            self.frames.append(data)
            self.root.after(1, self.record_audio)

    def stop_recording(self):
        self.is_recording = False
        self.stream.stop_stream()
        self.stream.close()
        if not self.save_folder:
            self.save_folder = (
                os.getcwd()
            )  # Default to current working directory if no folder is selected
        filename = os.path.join(self.save_folder, f"output_{self.text_index + 1}.wav")
        wf = wave.open(filename, "wb")
        wf.setnchannels(1)
        wf.setsampwidth(self.p.get_sample_size(pyaudio.paInt16))
        wf.setframerate(16000)
        wf.writeframes(b"".join(self.frames))
        wf.close()

    def prev_sentence(self):
        if self.text_index > 0:
            self.text_index -= 1
            self.update_sentence()

    def next_sentence(self):
        if self.text_index < len(self.sentences) - 1:
            self.text_index += 1
            self.update_sentence()

    def update_sentence(self):
        self.line_label.config(text=f"{self.text_index + 1}番目: ")
        self.text_label.config(text=self.sentences[self.text_index])

    def on_closing(self):
        if self.is_recording:
            self.stop_recording()
        self.p.terminate()
        self.root.destroy()


root = tk.Tk()
app = VoiceRecorderApp(root)
root.protocol("WM_DELETE_WINDOW", app.on_closing)
root.mainloop()
