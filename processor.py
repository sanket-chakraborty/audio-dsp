import numpy as np
import librosa
import soundfile as sf
from scipy.signal import butter, lfilter, fftconvolve

# 1. NOISE REDUCTION (Spectral Subtraction)
def spectral_subtraction(y, sr):
    D = librosa.stft(y)
    magnitude, phase = np.abs(D), np.angle(D)

    noise_est = np.mean(magnitude[:, :5], axis=1, keepdims=True)
    magnitude_clean = magnitude - noise_est
    magnitude_clean = np.maximum(magnitude_clean, 0)

    D_clean = magnitude_clean * np.exp(1j * phase)
    y_clean = librosa.istft(D_clean)
    return y_clean


# 2. EQUALIZER (3-BAND)
def butter_filter(data, cutoff, fs, btype):
    nyq = 0.5 * fs

    if isinstance(cutoff, list):
        normal_cutoff = [min(c / nyq, 0.999) for c in cutoff]
    else:
        normal_cutoff = min(cutoff / nyq, 0.999)

    b, a = butter(4, normal_cutoff, btype=btype)
    return lfilter(b, a, data)


def apply_equalizer(y, sr, low_gain, mid_gain, high_gain):
    low = butter_filter(y, 300, sr, 'low')
    mid = butter_filter(y, [300, 3000], sr, 'band')
    high = butter_filter(y, 3000, sr, 'high')

    y_eq = (low_gain * low) + (mid_gain * mid) + (high_gain * high)
    return y_eq


# 3. ECHO / REVERB (CONVOLUTION)
def apply_echo(y, sr, delay=0.3, decay=0.5):
    delay_samples = int(delay * sr)
    impulse = np.zeros(delay_samples * 2)
    impulse[0] = 1
    impulse[delay_samples] = decay

    y_echo = fftconvolve(y, impulse)
    return y_echo[:len(y)]


# MAIN PROCESS PIPELINE
def process_audio(input_path, pitch_shift=0, speed=1.0,
                  noise_reduce=True,
                  low_gain=1.0, mid_gain=1.0, high_gain=1.0,
                  echo_on=False):

    # Load original
    y_original, sr = librosa.load(input_path, sr=None)
    y = y_original.copy()

    # 1. Noise Reduction
    if noise_reduce:
        y = spectral_subtraction(y, sr)

    # 2. STFT
    D = librosa.stft(y)

    # 3. Phase Vocoder
    D_stretch = librosa.phase_vocoder(D, rate=speed)

    # 4. ISTFT
    y = librosa.istft(D_stretch)

    # 5. Pitch Shift
    y = librosa.effects.pitch_shift(y, sr=sr, n_steps=pitch_shift)

    # 6. Equalizer
    y = apply_equalizer(y, sr, low_gain, mid_gain, high_gain)

    # 7. Echo
    if echo_on:
        y = apply_echo(y, sr)

    return y, sr, y_original


def save_audio(path, y, sr):
    sf.write(path, y, sr)