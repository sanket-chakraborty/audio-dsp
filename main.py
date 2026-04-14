import tkinter as tk
from tkinter import filedialog
import sounddevice as sd
import os
import numpy as np
import matplotlib.pyplot as plt
import librosa
import librosa.display

from processor import process_audio, save_audio

file_path = None
processed_audio = None
original_audio = None
sr = None


def load_file():
    global file_path
    file_path = filedialog.askopenfilename(filetypes=[("WAV files", "*.wav")])
    print("Loaded:", file_path)


def process():
    global processed_audio, sr, original_audio, file_path

    if file_path is None:
        print("Load a file first!")
        return

    pitch = float(pitch_slider.get())
    speed = float(speed_slider.get())

    low = float(low_slider.get())
    mid = float(mid_slider.get())
    high = float(high_slider.get())

    noise = noise_var.get()
    echo = echo_var.get()

    processed_audio, sr, original_audio = process_audio(
        file_path,
        pitch_shift=pitch,
        speed=speed,
        noise_reduce=noise,
        low_gain=low,
        mid_gain=mid,
        high_gain=high,
        echo_on=echo
    )

    print("Processing done!")


def play_audio():
    if processed_audio is None:
        print("Process first!")
        return

    sd.play(processed_audio, sr)
    sd.wait()


def save():
    if processed_audio is None:
        print("Nothing to save!")
        return

    os.makedirs("outputs", exist_ok=True)
    save_audio("outputs/output.wav", processed_audio, sr)
    print("Saved to outputs/output.wav")


# VISUALIZATION FUNCTIONS
def show_waveforms():
    if processed_audio is None:
        print("Process first!")
        return

    plt.figure(figsize=(10, 6))

    plt.subplot(2, 1, 1)
    plt.title("Original Signal")
    plt.plot(original_audio)

    plt.subplot(2, 1, 2)
    plt.title("Processed Signal")
    plt.plot(processed_audio)

    plt.tight_layout()
    plt.show()


def show_spectrograms():
    if processed_audio is None:
        print("Process first!")
        return

    plt.figure(figsize=(10, 6))

    # Original
    plt.subplot(2, 1, 1)
    D1 = librosa.amplitude_to_db(
        abs(librosa.stft(original_audio)),
        ref=np.max
    )
    librosa.display.specshow(D1, sr=sr, x_axis='time', y_axis='log')
    plt.title("Original Spectrogram")
    plt.colorbar()

    # Processed
    plt.subplot(2, 1, 2)
    D2 = librosa.amplitude_to_db(
        abs(librosa.stft(processed_audio)),
        ref=np.max
    )
    librosa.display.specshow(D2, sr=sr, x_axis='time', y_axis='log')
    plt.title("Processed Spectrogram")
    plt.colorbar()

    plt.tight_layout()
    plt.show()


# GUI
root = tk.Tk()
root.title("DSP Voice Changer")

tk.Button(root, text="Load Audio", command=load_file).pack()

# Pitch
tk.Label(root, text="Pitch (-12 to +12)").pack()
pitch_slider = tk.Scale(root, from_=-12, to=12, orient=tk.HORIZONTAL)
pitch_slider.pack()

# Speed
tk.Label(root, text="Speed (0.5 to 2)").pack()
speed_slider = tk.Scale(root, from_=0.5, to=2, resolution=0.1, orient=tk.HORIZONTAL)
speed_slider.set(1)
speed_slider.pack()

# Equalizer
tk.Label(root, text="Low Gain").pack()
low_slider = tk.Scale(root, from_=0, to=2, resolution=0.1, orient=tk.HORIZONTAL)
low_slider.set(1)
low_slider.pack()

tk.Label(root, text="Mid Gain").pack()
mid_slider = tk.Scale(root, from_=0, to=2, resolution=0.1, orient=tk.HORIZONTAL)
mid_slider.set(1)
mid_slider.pack()

tk.Label(root, text="High Gain").pack()
high_slider = tk.Scale(root, from_=0, to=2, resolution=0.1, orient=tk.HORIZONTAL)
high_slider.set(1)
high_slider.pack()

# Checkboxes
noise_var = tk.BooleanVar(value=True)
echo_var = tk.BooleanVar(value=False)

tk.Checkbutton(root, text="Noise Reduction", variable=noise_var).pack()
tk.Checkbutton(root, text="Echo Effect", variable=echo_var).pack()

# Buttons
tk.Button(root, text="Process", command=process).pack()
tk.Button(root, text="Play", command=play_audio).pack()
tk.Button(root, text="Save", command=save).pack()

# NEW BUTTONS
tk.Button(root, text="Show Waveforms", command=show_waveforms).pack()
tk.Button(root, text="Show Spectrograms", command=show_spectrograms).pack()

root.mainloop()