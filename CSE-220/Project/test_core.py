"""
test_core.py
-------------
Quick sanity tests for morse_code.py and signal_proc.py that do NOT
require tkinter or an audio device, so they can run anywhere (CI,
grading scripts, etc.):

    python test_core.py
"""

import numpy as np

import morse_code as mc
import signal_proc as sp


def test_text_roundtrip():
    for text in ["HELLO WORLD", "SOS", "Python 3.12!", "A B C"]:
        morse = mc.text_to_morse(text)
        back = mc.morse_to_text(morse)
        assert back == text.upper(), f"Roundtrip failed for {text!r}: got {back!r}"
    print("[OK] text <-> morse roundtrip")


def test_signal_generation():
    morse = mc.text_to_morse("SOS")
    sig = sp.morse_to_signal(morse, freq=700, wpm=20, sample_rate=8000, amplitude=0.8)
    assert len(sig) > 0
    assert np.max(np.abs(sig)) <= 0.8 + 1e-9
    print(f"[OK] signal generation ({len(sig)} samples, {len(sig)/8000:.2f}s)")
    return sig


def test_fft_recovers_frequency(sig):
    freq_est = sp.dominant_frequency(sig, 8000)
    assert abs(freq_est - 700) < 15, f"Expected ~700 Hz, got {freq_est} Hz"
    print(f"[OK] FFT dominant frequency ~= {freq_est:.1f} Hz")


def test_noise_filter_decode_pipeline(sig):
    noisy = sp.add_noise(sig, snr_db=6)
    filtered = sp.bandpass_filter(noisy, 700, 8000, bandwidth=250)
    morse_out = sp.decode_signal_to_morse(filtered, 8000)
    text_out = mc.morse_to_text(morse_out)
    assert text_out == "SOS", f"Expected SOS, got {text_out!r}"
    print(f"[OK] noise -> filter -> decode pipeline recovered: {text_out!r}")


def test_invalid_morse_detection():
    assert mc.is_valid_morse(".... . .-.. .-.. --- / .-- --- .-. .-.. -..")
    assert not mc.is_valid_morse("HELLO")
    print("[OK] morse validity check")


if __name__ == '__main__':
    test_text_roundtrip()
    sig = test_signal_generation()
    test_fft_recovers_frequency(sig)
    test_noise_filter_decode_pipeline(sig)
    test_invalid_morse_detection()
    print("\nAll core tests passed.")