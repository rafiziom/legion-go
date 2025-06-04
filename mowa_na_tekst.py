#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sounddevice as sd
from vosk import Model, KaldiRecognizer
import json
import subprocess
import sys
import time
import numpy as np
import os
import signal
import locale

# Konfiguracja
MODEL_PATH = "/home/bazzite/.local/share/vosk/vosk-model-small-pl-0.22"
MICROPHONE_ID = 5  # Sprawdź ID: python3 -m sounddevice
SAMPLERATE = 48000  # 16kHz działa lepiej z Vosk
CHUNK_SIZE = 2000
BEEP_DURATION = 0.3
PID_FILE = "/tmp/voice_to_text.pid"

# Ustawienia locale dla polskich znaków
locale.setlocale(locale.LC_ALL, 'pl_PL.UTF-8')

class VoiceToText:
    def __init__(self):
        self.is_recording = False
        self.stream = None
        self.rec = None

    def generate_beep(self, freq=440, volume=0.5):
        t = np.linspace(0, BEEP_DURATION, int(BEEP_DURATION * SAMPLERATE), False)
        return volume * np.sin(2 * np.pi * freq * t)

    def play_sound(self, sound_data):
        try:
            # Walidacja: jeśli sounddevice już gra, nie próbuj ponownie
            if hasattr(self, '_is_playing') and self._is_playing:
                return
            self._is_playing = True
            sd.play(sound_data, samplerate=SAMPLERATE, blocking=True)
            self._is_playing = False
        except Exception as e:
            print(f"Błąd dźwięku: {e}", file=sys.stderr)
            self._is_playing = False

    def type_polish_text(self, text):
        """Specjalna funkcja do obsługi polskich znaków i zamiany słów na znaki interpunkcyjne oraz Enter (spacja po interpunkcji i na końcu frazy)"""
        try:
            replacements = {
                'kropka': '.',
                'przecinek': ',',
                'myślnik': '-',
                'dwukropek': ':',
                'średnik': ';',
                'wykrzyknik': '!',
                'znak zapytania': '?',
                'otwarty nawias': '(',
                'zamknięty nawias': ')',
                'cudzysłów': '"',
                'apostrof': "'",
                'pauza': '—',
                'kropka i przecinek': '.,',
            }
            clean_text = text.encode('utf-8').decode('utf-8').strip()
            # Obsługa komendy Enter
            if 'enter' in clean_text.lower():
                before_enter = clean_text.lower().split('enter')[0].strip()
                words = before_enter.split()
                out = []
                for word in words:
                    out.append(replacements.get(word, word))
                # Składanie tekstu: spacja po interpunkcji i na końcu frazy
                result = ''
                for i, word in enumerate(out):
                    if word in replacements.values():
                        result = result.rstrip() + word + ' '
                    else:
                        result += word + ' '
                result = result.rstrip() + ' '
                if result.strip():
                    subprocess.run([
                        "xdotool", "type", "--clearmodifiers", "--delay=25", result
                    ], check=True)
                subprocess.run(["xdotool", "key", "Return"], check=True)
                return
            # Zwykła zamiana interpunkcji (tylko całe słowa)
            words = clean_text.split()
            out = []
            for word in words:
                out.append(replacements.get(word, word))
            result = ''
            for i, word in enumerate(out):
                if word in replacements.values():
                    result = result.rstrip() + word + ' '
                else:
                    result += word + ' '
            result = result.rstrip() + ' '
            if result.strip():
                subprocess.run(
                    ["xdotool", "type", "--clearmodifiers", "--delay=25", result],
                    check=True
                )
        except Exception as e:
            print(f"Błąd wpisywania: {e}", file=sys.stderr)
            print(f"Rozpoznano: {text}")

    def check_running(self):
        if not os.path.exists(PID_FILE):
            return False
        
        with open(PID_FILE, 'r') as f:
            try:
                pid = int(f.read().strip())
                os.kill(pid, 0)  # Sprawdza czy proces istnieje
                return True
            except:
                return False

    def start_recording(self):
        try:
            # Walidacja: jeśli już nagrywa, nie uruchamiaj ponownie
            if self.is_recording:
                print("Nagrywanie już trwa.")
                return
            self.is_recording = True
            # Zapisz PID
            with open(PID_FILE, 'w') as f:
                f.write(str(os.getpid()))
            
            model = Model(MODEL_PATH)
            self.rec = KaldiRecognizer(model, SAMPLERATE)
            
            def callback(indata, frames, time, status):
                if status:
                    print(status, file=sys.stderr)
                # Poprawka: użyj indata.tobytes() zamiast bytes(indata)
                if len(indata) > 0 and self.rec.AcceptWaveform(indata.tobytes()):
                    result = json.loads(self.rec.Result())
                    if 'text' in result and result['text']:
                        print("Rozpoznano:", result['text'])  # Logowanie
                        self.type_polish_text(result['text'])

            self.stream = sd.InputStream(
                samplerate=SAMPLERATE,
                blocksize=CHUNK_SIZE,
                device=MICROPHONE_ID,
                dtype='int16',
                channels=1,
                callback=callback
            )
            self.stream.start()
            self.play_sound(self.generate_beep(880))
            print("NAGRYWANIE AKTYWNE (Ctrl+C aby zatrzymać)")
            
            while True:
                time.sleep(0.1)
                
        except Exception as e:
            print(f"Błąd: {e}", file=sys.stderr)
            self.cleanup()
            sys.exit(1)

    def _sigterm_handler(self, signum, frame):
        print("\nOtrzymano sygnał zakończenia (SIGTERM). Zamykanie...")
        self.cleanup()
        sys.exit(0)

    def stop_recording(self):
        # Walidacja: jeśli nie ma PID, nie próbuj zatrzymywać
        if not os.path.exists(PID_FILE):
            print("Brak aktywnego procesu do zatrzymania.")
            return

        if os.path.exists(PID_FILE):
            with open(PID_FILE, 'r') as f:
                try:
                    pid = int(f.read().strip())
                    os.kill(pid, signal.SIGTERM)
                except ProcessLookupError:
                    pass
                except Exception as e:
                    print(f"Błąd przy zamykaniu: {e}", file=sys.stderr)
            os.remove(PID_FILE)

    def cleanup(self):
        if self.stream:
            self.stream.stop()
            self.stream.close()
        if os.path.exists(PID_FILE):
            os.remove(PID_FILE)
        # Dźwięk wyłączania: wyższy, krótki sygnał (np. 660 Hz)
        self.play_sound(self.generate_beep(660, 0.7))

if __name__ == "__main__":
    vtt = VoiceToText()
    # Obsługa SIGTERM
    signal.signal(signal.SIGTERM, vtt._sigterm_handler)
    
    if vtt.check_running():
        vtt.stop_recording()
        print("Zatrzymano istniejący proces")
    else:
        try:
            vtt.start_recording()
        except KeyboardInterrupt:
            print("\nZamykanie...")
        finally:
            vtt.cleanup()