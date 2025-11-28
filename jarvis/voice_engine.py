import pyttsx3
import speech_recognition as sr
import threading
import time
from collections import deque
from .config import Config
from .sound_fx import SoundFx

class VoiceEngine:
    """
    Handles Speech-to-Text (STT) and Text-to-Speech (TTS).
    Premium Edition: Deeper voice, emotional tone stubs, robust recovery.
    """
    def __init__(self):
        self.engine = pyttsx3.init()
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        
        self.command_queue = deque()
        self.lock = threading.Lock()
        self.is_speaking = False
        self.is_listening = True
        self.active_mode = False 
        
        self._setup_voice()
        self.start_listener()
        
    def _setup_voice(self):
        try:
            voices = self.engine.getProperty('voices')
            selected = None
            # Try to find a good male voice for JARVIS (David on Windows)
            for v in voices:
                if "David" in v.name:
                    selected = v.id
                    break
            if not selected and voices:
                selected = voices[0].id
                
            self.engine.setProperty('voice', selected)
            self.engine.setProperty('rate', Config.VOICE_RATE)
            self.engine.setProperty('volume', Config.VOICE_VOLUME)
            
            # Pitch adjustment is not directly supported by standard pyttsx3 SAPI5 driver easily without XML
            # But we set the rate lower to simulate a deeper, calmer tone.
        except Exception as e:
            print(f"[VOICE] Setup Error: {e}")

    def speak(self, text, emotion="neutral"):
        """
        Non-blocking speech with emotional context (stub).
        """
        print(f"[JARVIS]: {text}")
        
        def _speak_thread():
            self.is_speaking = True
            try:
                eng = pyttsx3.init()
                eng.setProperty('voice', self.engine.getProperty('voice'))
                
                # Adjust rate slightly based on emotion
                rate = Config.VOICE_RATE
                if emotion == "urgent": rate += 20
                elif emotion == "sad": rate -= 20
                eng.setProperty('rate', rate)
                
                eng.say(text)
                eng.runAndWait()
            except Exception as e:
                print(f"[VOICE] Speak Error: {e}")
            finally:
                time.sleep(0.2)
                self.is_speaking = False
                
        threading.Thread(target=_speak_thread).start()

    def start_listener(self):
        threading.Thread(target=self._listen_loop, daemon=True).start()

    def _listen_loop(self):
        print("[VOICE] Listener started.")
        
        while self.is_listening:
            try:
                with self.microphone as source:
                    self.recognizer.adjust_for_ambient_noise(source, duration=1)
                    self.recognizer.dynamic_energy_threshold = Config.MIC_DYNAMIC_ENERGY
                    self.recognizer.energy_threshold = Config.MIC_ENERGY_THRESHOLD
                    
                    while self.is_listening:
                        if self.is_speaking:
                            time.sleep(0.1)
                            continue
                            
                        try:
                            audio = self.recognizer.listen(source, timeout=None, phrase_time_limit=5)
                            text = self.recognizer.recognize_google(audio).lower()
                            print(f"[USER]: {text}")
                            
                            if Config.WAKE_WORD in text:
                                parts = text.split(Config.WAKE_WORD, 1)
                                command = parts[1].strip()
                                
                                if command and Config.ONE_SHOT_COMMAND:
                                    with self.lock:
                                        self.command_queue.append(command)
                                    SoundFx.success()
                                else:
                                    self.active_mode = True
                                    SoundFx.listening_start()
                                    self.speak("Yes sir?")
                                    
                            elif self.active_mode:
                                with self.lock:
                                    self.command_queue.append(text)
                                self.active_mode = False 
                                SoundFx.listening_end()
                                
                        except sr.WaitTimeoutError: pass
                        except sr.UnknownValueError: pass
                        except sr.RequestError:
                            print("[VOICE] Network Error")
                            time.sleep(2)
                            
            except OSError:
                print("[VOICE] Microphone Error! Retrying in 5s...")
                time.sleep(5)
            except Exception as e:
                print(f"[VOICE] Critical Listener Error: {e}")
                time.sleep(1)

    def get_command(self):
        with self.lock:
            if self.command_queue:
                return self.command_queue.popleft()
            return None
