"""
signal_proc.py
---------------
All the actual "signal processing" for the project:

  * Morse string  -> audio waveform (sine-tone synthesis)
  * waveform      -> playback / recording (sounddevice)
  * waveform      -> frequency spectrum (FFT)
  * waveform      -> noisy waveform (AWGN at a target SNR)
  * noisy waveform -> filtered waveform (Butterworth band-pass)
  * waveform      -> Morse string (envelope detection / decoding)

Kept independent of tkinter so it can be unit tested or reused in a
notebook / CLI script.
"""

import numpy as np
from scipy import signal as sp_signal

try:
    import sounddevice as sd
    SOUND_AVAILABLE = True
except Exception:  # pragma: no cover - environment without audio hardware
    SOUND_AVAILABLE = False


# --------------------------------------------------------------------------
# 1. Morse -> signal (synthesis)
# --------------------------------------------------------------------------

def dot_duration(wpm: float) -> float:
    """
    Standard PARIS timing formula: one dot ("unit") lasts 1.2/wpm seconds.
    A dash = 3 units, intra-letter gap = 1 unit,
    inter-letter gap = 3 units, inter-word gap = 7 units.
    """
    return 1.2 / max(wpm, 1e-6)


def _tone(duration, freq, sample_rate, amplitude):
    """One continuous sine tone, with a short fade in/out to avoid clicks."""
    n = max(int(round(sample_rate * duration)), 1)
    t = np.arange(n) / sample_rate
    wave = amplitude * np.sin(2 * np.pi * freq * t)

    fade_len = min(int(0.005 * sample_rate), n // 2)  # 5 ms fade
    if fade_len > 1:
        fade = np.linspace(0.0, 1.0, fade_len)
        wave[:fade_len] *= fade
        wave[-fade_len:] *= fade[::-1]
    return wave


def _silence(duration, sample_rate):
    n = max(int(round(sample_rate * duration)), 0)
    return np.zeros(n)


def morse_to_signal(morse_code: str, freq=700.0, wpm=20.0,
                     sample_rate=44100, amplitude=0.7):
    """
    Turn a Morse string (as produced by morse_code.text_to_morse) into a
    1-D numpy float array representing the audio waveform.
    """
    unit = dot_duration(wpm)
    words = [w for w in morse_code.strip().split(' / ') if w != '']
    chunks = []

    for wi, word in enumerate(words):
        letters = [l for l in word.strip().split(' ') if l != '']
        for li, letter in enumerate(letters):
            for si, symbol in enumerate(letter):
                if symbol == '.':
                    chunks.append(_tone(unit, freq, sample_rate, amplitude))
                elif symbol == '-':
                    chunks.append(_tone(unit * 3, freq, sample_rate, amplitude))
                else:
                    continue  # unknown symbol ('?') -> skip silently
                if si < len(letter) - 1:
                    chunks.append(_silence(unit, sample_rate))       # intra-letter
            if li < len(letters) - 1:
                chunks.append(_silence(unit * 3, sample_rate))       # inter-letter
        if wi < len(words) - 1:
            chunks.append(_silence(unit * 7, sample_rate))           # inter-word

    if not chunks:
        return np.array([], dtype=float)
    return np.concatenate(chunks)


# --------------------------------------------------------------------------
# 2. Playback / recording
# --------------------------------------------------------------------------

def play_signal(data, sample_rate=44100, blocking=False):
    """Play a waveform through the default output device."""
    if not SOUND_AVAILABLE:
        raise RuntimeError("No audio output device available (sounddevice).")
    sd.play(data, sample_rate)
    if blocking:
        sd.wait()


def stop_playback():
    if SOUND_AVAILABLE:
        sd.stop()


def record_audio(duration, sample_rate=44100):
    """Record `duration` seconds of mono audio from the default mic."""
    if not SOUND_AVAILABLE:
        raise RuntimeError("No audio input device available (sounddevice).")
    audio = sd.rec(int(duration * sample_rate), samplerate=sample_rate,
                    channels=1, dtype='float64')
    sd.wait()
    return audio.flatten()


# --------------------------------------------------------------------------
# 3. Frequency-domain analysis (FFT)
# --------------------------------------------------------------------------

def compute_fft(data, sample_rate):
    """Return (frequencies, magnitude) of the one-sided amplitude spectrum."""
    n = len(data)
    if n == 0:
        return np.array([]), np.array([])
    freqs = np.fft.rfftfreq(n, d=1.0 / sample_rate)
    mag = np.abs(np.fft.rfft(data)) / n
    return freqs, mag


def dominant_frequency(data, sample_rate):
    """Estimate the strongest frequency component (ignoring DC)."""
    freqs, mag = compute_fft(data, sample_rate)
    if len(freqs) < 2:
        return 0.0
    idx = np.argmax(mag[1:]) + 1  # skip the DC bin at index 0
    return float(freqs[idx])


# --------------------------------------------------------------------------
# 4. Noise
# --------------------------------------------------------------------------

def add_noise(data, snr_db=10.0):
    """Add white Gaussian noise to reach the requested SNR (in dB)."""
    if len(data) == 0:
        return data
    sig_power = np.mean(data ** 2)
    if sig_power == 0:
        sig_power = 1e-12
    noise_power = sig_power / (10 ** (snr_db / 10))
    noise = np.sqrt(noise_power) * np.random.randn(len(data))
    return data + noise


def estimate_snr_db(clean, noisy):
    """Rough SNR estimate given the original and the noisy signal."""
    noise = noisy - clean
    sig_power = np.mean(clean ** 2)
    noise_power = np.mean(noise ** 2)
    if noise_power <= 0:
        return float('inf')
    return 10 * np.log10(sig_power / noise_power)


# --------------------------------------------------------------------------
# 5. Filtering
# --------------------------------------------------------------------------

def bandpass_filter(data, center_freq, sample_rate, bandwidth=200.0, order=4):
    """Zero-phase Butterworth band-pass filter around the carrier tone."""
    if len(data) == 0:
        return data
    nyq = sample_rate / 2.0
    low = max((center_freq - bandwidth / 2.0) / nyq, 1e-4)
    high = min((center_freq + bandwidth / 2.0) / nyq, 0.999)
    if low >= high:
        return data
    b, a = sp_signal.butter(order, [low, high], btype='band')
    padlen = 3 * (max(len(a), len(b)) - 1)
    if len(data) <= padlen:
        return data  # too short to filtfilt safely
    return sp_signal.filtfilt(b, a, data)


# --------------------------------------------------------------------------
# 6. Envelope detection & decoding (waveform -> Morse)
# --------------------------------------------------------------------------

def envelope(data, sample_rate, smoothing_ms=5.0):
    """Amplitude envelope via the Hilbert transform + short moving average."""
    if len(data) == 0:
        return data
    analytic = sp_signal.hilbert(data)
    env = np.abs(analytic)
    window = max(int(sample_rate * smoothing_ms / 1000.0), 1)
    kernel = np.ones(window) / window
    return np.convolve(env, kernel, mode='same')


def decode_signal_to_morse(data, sample_rate, threshold_ratio=0.35):
    """
    Recover a Morse string directly from an audio waveform.

    Self-calibrating: instead of requiring the exact WPM up front, it
    measures the shortest "tone on" run in the recording and treats that
    as one timing unit (a dot) -- the same way a real Morse decoder has
    to infer the operator's speed from the signal itself.
    """
    env = envelope(data, sample_rate)
    if len(env) == 0:
        return ''
    peak = np.max(env)
    if peak <= 0:
        return ''

    threshold = threshold_ratio * peak
    on = env > threshold

    # Collapse into (state, duration_seconds) runs
    runs = []
    start = 0
    current = bool(on[0])
    for i in range(1, len(on)):
        if bool(on[i]) != current:
            runs.append((current, (i - start) / sample_rate))
            start = i
            current = bool(on[i])
    runs.append((current, (len(on) - start) / sample_rate))

    on_durations = [d for state, d in runs if state]
    if not on_durations:
        return ''
    unit = min(on_durations)
    if unit <= 0:
        return ''

    morse = ''
    for state, dur in runs:
        n_units = dur / unit
        if state:
            morse += '.' if n_units < 2 else '-'
        else:
            if n_units < 2:
                continue            # intra-letter gap -> no separator needed
            elif n_units < 5:
                morse += ' '        # inter-letter gap
            else:
                morse += ' / '      # inter-word gap
    return morse.strip(' /')