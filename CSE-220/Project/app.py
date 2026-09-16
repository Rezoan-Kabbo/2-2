"""
app.py
-------
MORSE SIGNAL LAB — a Tkinter desktop app for a Python Signal Processing
university project.

Run with:
    python app.py

Tabs (roughly Level 1 -> Level 3 from the project brief):
    1. Converter     - Text <-> Morse, reference table               (Level 1)
    2. Signal Lab     - synthesize/play/visualize/FFT a Morse signal   (Level 2)
    3. Noise & Filter - add noise, band-pass filter, before/after      (Level 3)
    4. Mic Decode     - record from the microphone, decode back to text (Level 3)
"""

# To Install : & "C:\Users\User\AppData\Local\Python\pythoncore-3.14-64\python.exe" -m pip install -r requirements.txt
# To Run : & "C:\Users\User\AppData\Local\Python\pythoncore-3.14-64\python.exe" d:/2-2/CSE-220/Project/app.py
# To Check : & "C:\Users\User\AppData\Local\Python\pythoncore-3.14-64\python.exe" d:/2-2/CSE-220/Project/test_core.py

import threading
import tkinter as tk
from tkinter import ttk, messagebox

import numpy as np
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

import morse_code as mc
import signal_proc as sp

SAMPLE_RATE_OPTIONS = [8000, 16000, 22050, 44100]


class MorseSignalLab(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Morse Signal Lab")
        self.geometry("880x680")
        self.minsize(760, 600)

        # Shared state passed between tabs
        self.current_signal = np.array([])      # clean generated signal
        self.current_sample_rate = 44100
        self.noisy_signal = np.array([])
        self.filtered_signal = np.array([])
        self.recorded_signal = np.array([])

        self._build_style()
        notebook = ttk.Notebook(self)
        notebook.pack(fill='both', expand=True, padx=8, pady=8)

        self.converter_tab = ConverterTab(notebook, self)
        self.signal_tab = SignalLabTab(notebook, self)
        self.noise_tab = NoiseFilterTab(notebook, self)
        self.mic_tab = MicDecodeTab(notebook, self)

        notebook.add(self.converter_tab, text="1. Converter")
        notebook.add(self.signal_tab, text="2. Signal Lab")
        notebook.add(self.noise_tab, text="3. Noise & Filter")
        notebook.add(self.mic_tab, text="4. Mic Decode")

        if not sp.SOUND_AVAILABLE:
            self.after(200, lambda: messagebox.showwarning(
                "Audio unavailable",
                "No audio device found (sounddevice). Encoding, waveform "
                "plots and FFT will still work; play/record features will be "
                "disabled."))

    def _build_style(self):
        style = ttk.Style(self)
        try:
            style.theme_use('clam')
        except tk.TclError:
            pass
        style.configure('TNotebook.Tab', padding=(14, 8))
        style.configure('Header.TLabel', font=('Segoe UI', 13, 'bold'))
        style.configure('SubHeader.TLabel', font=('Segoe UI', 10, 'bold'))


# ==========================================================================
# Tab 1 -- Converter (Level 1)
# ==========================================================================

class ConverterTab(ttk.Frame):
    def __init__(self, parent, app: MorseSignalLab):
        super().__init__(parent, padding=12)
        self.app = app
        self.mode = tk.StringVar(value='text2morse')

        ttk.Label(self, text="Text \u2194 Morse Converter", style='Header.TLabel').pack(anchor='w')

        mode_frame = ttk.Frame(self)
        mode_frame.pack(fill='x', pady=(8, 4))
        ttk.Radiobutton(mode_frame, text="Text \u2192 Morse", variable=self.mode,
                         value='text2morse').pack(side='left', padx=(0, 16))
        ttk.Radiobutton(mode_frame, text="Morse \u2192 Text", variable=self.mode,
                         value='morse2text').pack(side='left')

        ttk.Label(self, text="Input", style='SubHeader.TLabel').pack(anchor='w', pady=(12, 2))
        self.input_box = tk.Text(self, height=4, wrap='word', font=('Consolas', 11))
        self.input_box.pack(fill='x')
        self.input_box.insert('1.0', 'HELLO WORLD')

        btn_frame = ttk.Frame(self)
        btn_frame.pack(fill='x', pady=8)
        ttk.Button(btn_frame, text="Convert", command=self.convert).pack(side='left')
        ttk.Button(btn_frame, text="Clear", command=self.clear).pack(side='left', padx=6)
        ttk.Button(btn_frame, text="Send to Signal Lab \u2192",
                   command=self.send_to_signal_lab).pack(side='left', padx=6)

        ttk.Label(self, text="Output", style='SubHeader.TLabel').pack(anchor='w', pady=(4, 2))
        self.output_box = tk.Text(self, height=4, wrap='word', font=('Consolas', 11), state='disabled')
        self.output_box.pack(fill='x')

        ttk.Label(self, text="Morse Code Reference Table", style='SubHeader.TLabel').pack(anchor='w', pady=(16, 4))
        self._build_table()

    def _build_table(self):
        container = ttk.Frame(self)
        container.pack(fill='both', expand=True)
        cols = ('char', 'code')

        # Split the table into 3 side-by-side lists so it stays compact
        rows = mc.morse_table_rows()
        third = (len(rows) + 2) // 3
        columns_of_rows = [rows[i:i + third] for i in range(0, len(rows), third)]

        trees_frame = ttk.Frame(container)
        trees_frame.pack(fill='both', expand=True)
        for col_rows in columns_of_rows:
            t = ttk.Treeview(trees_frame, columns=cols, show='headings', height=len(col_rows))
            t.heading('char', text='Char')
            t.heading('code', text='Code')
            t.column('char', width=70, anchor='center')
            t.column('code', width=110, anchor='center')
            for ch, code in col_rows:
                t.insert('', 'end', values=(ch, code))
            t.pack(side='left', fill='y', expand=True, padx=4)

    def convert(self):
        raw = self.input_box.get('1.0', 'end').strip()
        if not raw:
            return
        if self.mode.get() == 'text2morse':
            result = mc.text_to_morse(raw)
        else:
            if not mc.is_valid_morse(raw):
                messagebox.showerror("Invalid input",
                                      "Morse input should only contain '.', '-', spaces and '/'.")
                return
            result = mc.morse_to_text(raw)
        self._set_output(result)

    def clear(self):
        self.input_box.delete('1.0', 'end')
        self._set_output('')

    def _set_output(self, text):
        self.output_box.config(state='normal')
        self.output_box.delete('1.0', 'end')
        self.output_box.insert('1.0', text)
        self.output_box.config(state='disabled')

    def send_to_signal_lab(self):
        """Push the current morse output (or convert text on the fly) to Tab 2."""
        out = self.output_box.get('1.0', 'end').strip()
        if not out and self.mode.get() == 'text2morse':
            self.convert()
            out = self.output_box.get('1.0', 'end').strip()
        if self.mode.get() == 'morse2text':
            # If we're in morse->text mode, the *input* box already holds morse
            out = self.input_box.get('1.0', 'end').strip()
        if not out:
            messagebox.showinfo("Nothing to send", "Convert some text to Morse first.")
            return
        self.app.signal_tab.set_morse_input(out)


# ==========================================================================
# Tab 2 -- Signal Lab (Level 2)
# ==========================================================================

class SignalLabTab(ttk.Frame):
    def __init__(self, parent, app: MorseSignalLab):
        super().__init__(parent, padding=12)
        self.app = app

        ttk.Label(self, text="Morse \u2192 Signal Generator", style='Header.TLabel').pack(anchor='w')

        self.morse_var = tk.StringVar(value=mc.text_to_morse("SOS"))
        entry_frame = ttk.Frame(self)
        entry_frame.pack(fill='x', pady=(8, 4))
        ttk.Label(entry_frame, text="Morse:").pack(side='left')
        ttk.Entry(entry_frame, textvariable=self.morse_var, font=('Consolas', 11)).pack(
            side='left', fill='x', expand=True, padx=6)

        # --- signal settings ------------------------------------------------
        settings = ttk.LabelFrame(self, text="Signal Settings", padding=10)
        settings.pack(fill='x', pady=10)

        self.freq_var = tk.DoubleVar(value=700)
        self.wpm_var = tk.DoubleVar(value=20)
        self.vol_var = tk.DoubleVar(value=70)
        self.sr_var = tk.IntVar(value=44100)

        self._make_slider(settings, "Frequency (Hz)", self.freq_var, 200, 1500, 0)
        self._make_slider(settings, "Speed (WPM)", self.wpm_var, 5, 40, 1)
        self._make_slider(settings, "Volume (%)", self.vol_var, 0, 100, 2)

        ttk.Label(settings, text="Sample rate:").grid(row=3, column=0, sticky='w', pady=4)
        sr_menu = ttk.OptionMenu(settings, self.sr_var, self.sr_var.get(), *SAMPLE_RATE_OPTIONS)
        sr_menu.grid(row=3, column=1, sticky='w')
        settings.columnconfigure(1, weight=1)

        # --- action buttons ---------------------------------------------
        btns = ttk.Frame(self)
        btns.pack(fill='x', pady=4)
        ttk.Button(btns, text="Generate Signal", command=self.generate).pack(side='left')
        self.play_btn = ttk.Button(btns, text="\u25b6 Play", command=self.play)
        self.play_btn.pack(side='left', padx=6)
        ttk.Button(btns, text="\u25a0 Stop", command=self.stop).pack(side='left')
        ttk.Button(btns, text="Send to Noise Lab \u2192", command=self.send_to_noise_lab).pack(side='left', padx=6)

        self.info_var = tk.StringVar(value="No signal generated yet.")
        ttk.Label(self, textvariable=self.info_var).pack(anchor='w', pady=(4, 6))

        # --- plot area with Waveform / FFT toggle ------------------------
        plot_toggle = ttk.Frame(self)
        plot_toggle.pack(fill='x')
        self.plot_mode = tk.StringVar(value='waveform')
        ttk.Radiobutton(plot_toggle, text="Waveform", variable=self.plot_mode,
                         value='waveform', command=self.redraw).pack(side='left')
        ttk.Radiobutton(plot_toggle, text="FFT Spectrum", variable=self.plot_mode,
                         value='fft', command=self.redraw).pack(side='left', padx=10)

        self.figure = Figure(figsize=(6, 3), dpi=100)
        self.ax = self.figure.add_subplot(111)
        self.canvas = FigureCanvasTkAgg(self.figure, master=self)
        self.canvas.get_tk_widget().pack(fill='both', expand=True, pady=6)
        self.redraw()

    def _make_slider(self, parent, label, var, lo, hi, row):
        ttk.Label(parent, text=label).grid(row=row, column=0, sticky='w', pady=4)
        val_lbl = ttk.Label(parent, width=6, anchor='e')
        val_lbl.grid(row=row, column=2, sticky='e')

        def on_change(_evt=None):
            val_lbl.config(text=f"{var.get():.0f}")

        scale = ttk.Scale(parent, from_=lo, to=hi, orient='horizontal', variable=var,
                           command=on_change)
        scale.grid(row=row, column=1, sticky='ew', padx=8)
        on_change()

    def set_morse_input(self, morse_str):
        self.morse_var.set(morse_str)
        self.generate()

    def generate(self):
        morse = self.morse_var.get().strip()
        if not morse:
            messagebox.showinfo("Nothing to generate", "Enter a Morse string first.")
            return
        freq = self.freq_var.get()
        wpm = self.wpm_var.get()
        amp = self.vol_var.get() / 100.0
        sr = self.sr_var.get()

        sig = sp.morse_to_signal(morse, freq=freq, wpm=wpm, sample_rate=sr, amplitude=amp)
        self.app.current_signal = sig
        self.app.current_sample_rate = sr
        duration = len(sig) / sr if sr else 0
        self.info_var.set(f"Generated {len(sig)} samples \u2022 {duration:.2f} s \u2022 "
                           f"{freq:.0f} Hz \u2022 {wpm:.0f} WPM \u2022 {sr} Hz sample rate")
        self.redraw()

    def redraw(self):
        self.ax.clear()
        sig = self.app.current_signal
        sr = self.app.current_sample_rate
        if len(sig) == 0:
            self.ax.set_title("No signal yet \u2014 click Generate Signal")
            self.canvas.draw()
            return

        if self.plot_mode.get() == 'waveform':
            # Downsample purely for plotting speed on long signals
            max_points = 20000
            step = max(1, len(sig) // max_points)
            t = np.arange(0, len(sig), step) / sr
            self.ax.plot(t, sig[::step], linewidth=0.8, color='#2563eb')
            self.ax.set_xlabel("Time (s)")
            self.ax.set_ylabel("Amplitude")
            self.ax.set_title("Time-domain Waveform")
        else:
            freqs, mag = sp.compute_fft(sig, sr)
            self.ax.plot(freqs, mag, linewidth=0.9, color='#dc2626')
            self.ax.set_xlim(0, min(3000, sr / 2))
            self.ax.set_xlabel("Frequency (Hz)")
            self.ax.set_ylabel("Magnitude")
            self.ax.set_title("Frequency Spectrum (FFT)")
        self.figure.tight_layout()
        self.canvas.draw()

    def play(self):
        if len(self.app.current_signal) == 0:
            messagebox.showinfo("Nothing to play", "Generate a signal first.")
            return
        try:
            sp.play_signal(self.app.current_signal, self.app.current_sample_rate)
        except RuntimeError as e:
            messagebox.showerror("Playback error", str(e))

    def stop(self):
        sp.stop_playback()

    def send_to_noise_lab(self):
        if len(self.app.current_signal) == 0:
            messagebox.showinfo("Nothing to send", "Generate a signal first.")
            return
        self.app.noise_tab.load_clean_signal()


# ==========================================================================
# Tab 3 -- Noise & Filter (Level 3)
# ==========================================================================

class NoiseFilterTab(ttk.Frame):
    def __init__(self, parent, app: MorseSignalLab):
        super().__init__(parent, padding=12)
        self.app = app

        ttk.Label(self, text="Noise Injection & Band-pass Filtering", style='Header.TLabel').pack(anchor='w')
        ttk.Label(self, text="Uses the signal generated in the Signal Lab tab.").pack(anchor='w', pady=(2, 10))

        row = ttk.Frame(self)
        row.pack(fill='x')
        self.snr_var = tk.DoubleVar(value=8)
        ttk.Label(row, text="Target SNR (dB):").pack(side='left')
        ttk.Scale(row, from_=-10, to=30, orient='horizontal', variable=self.snr_var,
                  length=220).pack(side='left', padx=8)
        self.snr_lbl = ttk.Label(row, width=6)
        self.snr_lbl.pack(side='left')
        self.snr_var.trace_add('write', lambda *_: self.snr_lbl.config(text=f"{self.snr_var.get():.0f}"))
        self.snr_lbl.config(text=f"{self.snr_var.get():.0f}")

        row2 = ttk.Frame(self)
        row2.pack(fill='x', pady=(6, 0))
        self.bw_var = tk.DoubleVar(value=200)
        ttk.Label(row2, text="Filter bandwidth (Hz):").pack(side='left')
        ttk.Scale(row2, from_=50, to=600, orient='horizontal', variable=self.bw_var,
                  length=220).pack(side='left', padx=8)
        self.bw_lbl = ttk.Label(row2, width=6)
        self.bw_lbl.pack(side='left')
        self.bw_var.trace_add('write', lambda *_: self.bw_lbl.config(text=f"{self.bw_var.get():.0f}"))
        self.bw_lbl.config(text=f"{self.bw_var.get():.0f}")

        btns = ttk.Frame(self)
        btns.pack(fill='x', pady=10)
        ttk.Button(btns, text="1. Add Noise", command=self.add_noise).pack(side='left')
        ttk.Button(btns, text="2. Apply Filter", command=self.apply_filter).pack(side='left', padx=6)
        ttk.Button(btns, text="\u25b6 Play Noisy", command=lambda: self._play(self.app.noisy_signal)).pack(side='left', padx=(20, 4))
        ttk.Button(btns, text="\u25b6 Play Filtered", command=lambda: self._play(self.app.filtered_signal)).pack(side='left')
        ttk.Button(btns, text="Decode Filtered \u2192 Text", command=self.decode_filtered).pack(side='left', padx=6)

        self.info_var = tk.StringVar(value="Generate a signal in Signal Lab, then add noise here.")
        ttk.Label(self, textvariable=self.info_var, wraplength=820, justify='left').pack(anchor='w', pady=(2, 6))

        self.figure = Figure(figsize=(6, 4), dpi=100)
        self.ax_before = self.figure.add_subplot(211)
        self.ax_after = self.figure.add_subplot(212)
        self.canvas = FigureCanvasTkAgg(self.figure, master=self)
        self.canvas.get_tk_widget().pack(fill='both', expand=True, pady=6)
        self._draw_placeholder()

    def _draw_placeholder(self):
        self.ax_before.clear()
        self.ax_after.clear()
        self.ax_before.set_title("Noisy signal (before filtering)")
        self.ax_after.set_title("Filtered signal (after filtering)")
        self.figure.tight_layout()
        self.canvas.draw()

    def load_clean_signal(self):
        self.info_var.set(f"Loaded clean signal: {len(self.app.current_signal)} samples "
                           f"at {self.app.current_sample_rate} Hz. Ready to add noise.")

    def add_noise(self):
        clean = self.app.current_signal
        if len(clean) == 0:
            messagebox.showinfo("No signal", "Generate a signal in the Signal Lab tab first.")
            return
        snr = self.snr_var.get()
        noisy = sp.add_noise(clean, snr_db=snr)
        self.app.noisy_signal = noisy
        sr = self.app.current_sample_rate

        self.ax_before.clear()
        max_points = 20000
        step = max(1, len(noisy) // max_points)
        t = np.arange(0, len(noisy), step) / sr
        self.ax_before.plot(t, noisy[::step], linewidth=0.7, color='#f59e0b')
        self.ax_before.set_title(f"Noisy signal (SNR \u2248 {snr:.0f} dB)")
        self.ax_before.set_xlabel("Time (s)")
        self.figure.tight_layout()
        self.canvas.draw()
        self.info_var.set(f"Added noise at target SNR {snr:.0f} dB. Now apply the band-pass filter.")

    def apply_filter(self):
        noisy = self.app.noisy_signal
        if len(noisy) == 0:
            messagebox.showinfo("No noisy signal", "Click 'Add Noise' first.")
            return
        freq = self.app.signal_tab.freq_var.get()
        bw = self.bw_var.get()
        sr = self.app.current_sample_rate
        filtered = sp.bandpass_filter(noisy, freq, sr, bandwidth=bw)
        self.app.filtered_signal = filtered

        self.ax_after.clear()
        max_points = 20000
        step = max(1, len(filtered) // max_points)
        t = np.arange(0, len(filtered), step) / sr
        self.ax_after.plot(t, filtered[::step], linewidth=0.7, color='#16a34a')
        self.ax_after.set_title(f"Filtered signal (band-pass \u00b1{bw/2:.0f} Hz around {freq:.0f} Hz)")
        self.ax_after.set_xlabel("Time (s)")
        self.figure.tight_layout()
        self.canvas.draw()

        snr_est = sp.estimate_snr_db(self.app.current_signal, self.app.noisy_signal)
        self.info_var.set(f"Filtered around {freq:.0f} Hz (bandwidth {bw:.0f} Hz). "
                           f"Estimated input SNR was {snr_est:.1f} dB.")

    def decode_filtered(self):
        filtered = self.app.filtered_signal
        if len(filtered) == 0:
            messagebox.showinfo("No filtered signal", "Add noise and apply the filter first.")
            return
        sr = self.app.current_sample_rate
        morse = sp.decode_signal_to_morse(filtered, sr)
        text = mc.morse_to_text(morse)
        messagebox.showinfo("Decoded from filtered signal",
                             f"Morse:\n{morse}\n\nText:\n{text}")

    def _play(self, data):
        if len(data) == 0:
            messagebox.showinfo("Nothing to play", "Generate that signal first.")
            return
        try:
            sp.play_signal(data, self.app.current_sample_rate)
        except RuntimeError as e:
            messagebox.showerror("Playback error", str(e))


# ==========================================================================
# Tab 4 -- Microphone Decode (Level 3, advanced)
# ==========================================================================

class MicDecodeTab(ttk.Frame):
    def __init__(self, parent, app: MorseSignalLab):
        super().__init__(parent, padding=12)
        self.app = app

        ttk.Label(self, text="Microphone \u2192 Morse \u2192 Text", style='Header.TLabel').pack(anchor='w')
        ttk.Label(self, text="Key/whistle Morse into your microphone (or play the "
                              "Signal Lab tone near it), then decode.",
                  wraplength=820, justify='left').pack(anchor='w', pady=(2, 10))

        row = ttk.Frame(self)
        row.pack(fill='x')
        self.duration_var = tk.DoubleVar(value=4.0)
        ttk.Label(row, text="Record duration (s):").pack(side='left')
        ttk.Scale(row, from_=1, to=15, orient='horizontal', variable=self.duration_var,
                  length=220).pack(side='left', padx=8)
        self.dur_lbl = ttk.Label(row, width=6)
        self.dur_lbl.pack(side='left')
        self.duration_var.trace_add('write', lambda *_: self.dur_lbl.config(text=f"{self.duration_var.get():.0f}"))
        self.dur_lbl.config(text=f"{self.duration_var.get():.0f}")

        btns = ttk.Frame(self)
        btns.pack(fill='x', pady=10)
        self.record_btn = ttk.Button(btns, text="\U0001F3A4 Record & Decode", command=self.record_and_decode)
        self.record_btn.pack(side='left')
        if not sp.SOUND_AVAILABLE:
            self.record_btn.state(['disabled'])

        self.status_var = tk.StringVar(value="Idle.")
        ttk.Label(self, textvariable=self.status_var).pack(anchor='w', pady=(2, 6))

        ttk.Label(self, text="Decoded Morse:", style='SubHeader.TLabel').pack(anchor='w')
        self.morse_out = tk.Text(self, height=2, font=('Consolas', 11), state='disabled')
        self.morse_out.pack(fill='x')

        ttk.Label(self, text="Decoded Text:", style='SubHeader.TLabel').pack(anchor='w', pady=(8, 2))
        self.text_out = tk.Text(self, height=2, font=('Consolas', 11), state='disabled')
        self.text_out.pack(fill='x')

        self.figure = Figure(figsize=(6, 2.6), dpi=100)
        self.ax = self.figure.add_subplot(111)
        self.canvas = FigureCanvasTkAgg(self.figure, master=self)
        self.canvas.get_tk_widget().pack(fill='both', expand=True, pady=8)

    def record_and_decode(self):
        self.record_btn.state(['disabled'])
        self.status_var.set("Recording...")
        duration = self.duration_var.get()
        thread = threading.Thread(target=self._record_worker, args=(duration,), daemon=True)
        thread.start()

    def _record_worker(self, duration):
        sr = 44100
        try:
            audio = sp.record_audio(duration, sample_rate=sr)
        except RuntimeError as e:
            self.after(0, lambda: self._on_record_error(str(e)))
            return
        self.after(0, lambda: self._on_recorded(audio, sr))

    def _on_record_error(self, msg):
        self.status_var.set("Recording failed.")
        self.record_btn.state(['!disabled'])
        messagebox.showerror("Recording error", msg)

    def _on_recorded(self, audio, sr):
        self.app.recorded_signal = audio
        morse = sp.decode_signal_to_morse(audio, sr)
        text = mc.morse_to_text(morse) if morse else ''

        self._set_text(self.morse_out, morse or '(no tone detected)')
        self._set_text(self.text_out, text)
        self.status_var.set(f"Decoded {len(audio)/sr:.1f}s of audio.")
        self.record_btn.state(['!disabled'])

        self.ax.clear()
        t = np.arange(len(audio)) / sr
        self.ax.plot(t, audio, linewidth=0.7, color='#7c3aed')
        self.ax.set_title("Recorded microphone signal")
        self.ax.set_xlabel("Time (s)")
        self.figure.tight_layout()
        self.canvas.draw()

    @staticmethod
    def _set_text(widget, value):
        widget.config(state='normal')
        widget.delete('1.0', 'end')
        widget.insert('1.0', value)
        widget.config(state='disabled')


if __name__ == '__main__':
    app = MorseSignalLab()
    app.mainloop()