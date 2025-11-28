import winsound
import threading
import time

class SoundFx:
    """
    Futuristic UI Sound Effects.
    Uses threaded playback to prevent blocking.
    """
    @staticmethod
    def play(freq, duration):
        try:
            threading.Thread(target=lambda: winsound.Beep(freq, duration)).start()
        except: pass

    @staticmethod
    def boot_sequence():
        def _play():
            try:
                winsound.Beep(400, 100)
                time.sleep(0.05)
                winsound.Beep(600, 100)
                time.sleep(0.05)
                winsound.Beep(1000, 300)
            except: pass
        threading.Thread(target=_play).start()

    @staticmethod
    def listening_start():
        SoundFx.play(1200, 150)
        
    @staticmethod
    def listening_end():
        SoundFx.play(800, 150)

    @staticmethod
    def click():
        SoundFx.play(1500, 30)
        
    @staticmethod
    def error():
        SoundFx.play(200, 400)
        
    @staticmethod
    def success():
        def _play():
            try:
                winsound.Beep(1000, 100)
                time.sleep(0.05)
                winsound.Beep(1500, 100)
            except: pass
        threading.Thread(target=_play).start()
