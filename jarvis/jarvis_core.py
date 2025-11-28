import cv2
import time
import mediapipe as mp
import threading
import sys
import webbrowser
import os
import keyboard 
import datetime
import psutil
import pyautogui

from .config import Config
from .voice_engine import VoiceEngine
from .face_id import FaceID
from .vision_yolo import VisionSystem
from .mouse_control import MouseController
from .hologram_ui import HologramUI
from .sound_fx import SoundFx

class JarvisCore:
    """
    JARVIS Mark-II Premium Core.
    Integrates Voice, Vision, Biometrics, UI, and System Control.
    """
    def __init__(self):
        print(f"[SYSTEM] Booting {Config.APP_NAME} v{Config.VERSION}...")
        Config.setup_directories()
        
        self.voice = VoiceEngine()
        self.face_sys = FaceID()
        self.vision = VisionSystem()
        self.mouse = MouseController()
        self.ui = HologramUI()
        
        # Permissions Check
        if not self.mouse.check_permissions():
            print("[WARNING] Mouse control blocked. Please enable Accessibility permissions.")
            self.ui.add_notification("MOUSE BLOCKED: Check Permissions")
        
        self.cap = cv2.VideoCapture(0)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, Config.WIDTH)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, Config.HEIGHT)
        
        self.mp_face_mesh = mp.solutions.face_mesh.FaceMesh(
            max_num_faces=3,
            refine_landmarks=True,
            min_detection_confidence=0.7
        )
        self.mp_hands = mp.solutions.hands.Hands(
            max_num_hands=1,
            min_detection_confidence=0.7
        )
        self.mp_draw = mp.solutions.drawing_utils
        
        self.running = True
        self.registering_user = None
        self.registration_buffer = []
        self.identified_user = None
        self.is_locked = False
        self.mic_muted = False
        self.debug_mode = False
        
        cv2.setUseOptimized(True)
        cv2.setNumThreads(4)
        
        self.voice.speak("Systems online. At your service, sir.")
        SoundFx.boot_sequence()

    def process_command(self, cmd):
        if self.mic_muted and "unmute" not in cmd:
            return

        self.ui.add_notification(f"CMD: {cmd}")
        
        # Security Check
        if self.is_locked and "register" not in cmd and "identify" not in cmd:
            self.voice.speak("Access denied. Please identify yourself.", emotion="urgent")
            return

        if "shutdown system" in cmd:
            self.voice.speak("Are you sure you want to shut down the PC?", emotion="urgent")
            self.running = False
            
        elif "goodbye" in cmd or "terminate" in cmd:
            self.voice.speak("Shutting down protocols. Goodbye, sir.", emotion="sad")
            self.running = False
            
        elif "enable object" in cmd:
            if self.vision.toggle(True):
                self.voice.speak("Object detection enabled.")
            else:
                self.voice.speak("Vision module failed to load.")
                
        elif "disable object" in cmd:
            self.vision.toggle(False)
            self.voice.speak("Vision module paused.")
            
        elif "register my name is" in cmd:
            name = cmd.split("name is")[-1].strip()
            self.registering_user = name
            self.registration_buffer = []
            self.voice.speak(f"Please look at the camera. Registering {name}.")
            
        elif "open youtube" in cmd:
            webbrowser.open("https://youtube.com")
            self.voice.speak("Opening YouTube.")
            
        elif "open google" in cmd:
            webbrowser.open("https://google.com")
            self.voice.speak("Opening Google.")
            
        elif "search for" in cmd:
            query = cmd.split("search for")[-1].strip()
            webbrowser.open(f"https://google.com/search?q={query}")
            self.voice.speak(f"Searching for {query}.")
            
        elif "search wikipedia" in cmd:
            query = cmd.split("wikipedia")[-1].strip()
            webbrowser.open(f"https://en.wikipedia.org/wiki/{query}")
            self.voice.speak(f"Searching Wikipedia for {query}.")
            
        elif "enable mouse" in cmd:
            self.mouse.paused_by_keyboard = False
            self.voice.speak("Mouse control active.")
            
        elif "disable mouse" in cmd:
            self.mouse.paused_by_keyboard = True
            self.voice.speak("Mouse control paused.")
            
        elif "take screenshot" in cmd:
            ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            path = os.path.join(Config.SCREENSHOT_DIR, f"screenshot_{ts}.png")
            pyautogui.screenshot(path)
            self.voice.speak("Screenshot saved.")
            self.ui.add_notification(f"Saved: {path}")
            
        elif "maximize window" in cmd:
            pyautogui.hotkey('win', 'up')
            self.voice.speak("Window maximized.")
            
        elif "minimize window" in cmd:
            pyautogui.hotkey('win', 'down')
            self.voice.speak("Window minimized.")
            
        elif "mute mic" in cmd:
            self.mic_muted = True
            self.voice.speak("Microphone muted.")
            
        elif "unmute mic" in cmd:
            self.mic_muted = False
            self.voice.speak("Microphone online.")
            
        elif "battery status" in cmd:
            batt = psutil.sensors_battery()
            if batt:
                self.voice.speak(f"Battery is at {batt.percent} percent.")
            else:
                self.voice.speak("System is running on AC power.")
                
        elif "time" in cmd:
            now = datetime.datetime.now().strftime("%I:%M %p")
            self.voice.speak(f"It is {now}.")
            
        elif "date" in cmd:
            today = datetime.datetime.now().strftime("%A, %B %d")
            self.voice.speak(f"Today is {today}.")

    def run(self):
        prev_time = 0
        
        while self.running:
            ret, frame = self.cap.read()
            if not ret:
                print("[SYSTEM] Camera Error.")
                time.sleep(1)
                continue
                
            frame = cv2.flip(frame, 1)
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            h, w, _ = frame.shape
            
            # Key Handling
            if keyboard.is_pressed('esc'):
                self.mouse.paused_by_keyboard = not self.mouse.paused_by_keyboard
                time.sleep(0.3)
            
            if keyboard.is_pressed('d'):
                self.debug_mode = not self.debug_mode
                time.sleep(0.3)
            
            # 1. Hands & Mouse
            # Process once per frame
            hand_res = self.mp_hands.process(rgb_frame)
            mouse_status = "NO_HAND"
            cursor_pos = (0, 0)
            
            if hand_res.multi_hand_landmarks and not self.is_locked:
                for idx, lm in enumerate(hand_res.multi_hand_landmarks):
                    # Handedness Check
                    handedness = hand_res.multi_handedness[idx].classification[0].label
                    # Note: MediaPipe assumes mirrored image by default, but we flipped it.
                    # So "Left" is actually Left hand if we flipped.
                    
                    target_hand = Config.GESTURE_HAND
                    if target_hand != "BOTH":
                        if target_hand != handedness.upper():
                            continue

                    # Draw Skeleton
                    self.mp_draw.draw_landmarks(
                        frame, 
                        lm, 
                        mp.solutions.hands.HAND_CONNECTIONS,
                        self.mp_draw.DrawingSpec(color=(0,255,255), thickness=2, circle_radius=2),
                        self.mp_draw.DrawingSpec(color=(255,0,0), thickness=2)
                    )
                    
                    # Update Mouse Logic
                    mouse_status = self.mouse.update(lm.landmark, (w, h))
                    cursor_pos = self.mouse.cursor_pos
                    
                    # Click Actions
                    if "CLICK" in mouse_status:
                        action = self.ui.check_menu_click(cursor_pos)
                        if action:
                            self.ui.add_notification(f"Menu: {action}")
                            SoundFx.click()
                            if action == "YOUTUBE": webbrowser.open("https://youtube.com")
                            elif action == "GOOGLE": webbrowser.open("https://google.com")
                            elif action == "MUSIC": webbrowser.open("https://music.youtube.com")
                            elif action == "OBJECTS": 
                                state = self.vision.toggle()
                                self.voice.speak(f"Vision {'enabled' if state else 'disabled'}.")
                    
                    # Only process one hand if not BOTH
                    if target_hand != "BOTH":
                        break
            else:
                mouse_status = "NO_HAND" if not self.mouse.paused_by_keyboard else "KEY-PAUSED"

            # 2. Face ID
            face_res = self.mp_face_mesh.process(rgb_frame)
            if face_res.multi_face_landmarks:
                for lm in face_res.multi_face_landmarks:
                    self.mp_draw.draw_landmarks(frame, lm, mp.solutions.face_mesh.FACEMESH_TESSELATION,
                        None, self.mp_draw.DrawingSpec(color=Config.CYAN_DIM, thickness=1, circle_radius=1))
                    
                    lms_list = [(p.x * w, p.y * h) for p in lm.landmark]
                    
                    if self.registering_user:
                        self.registration_buffer.append(lms_list)
                        count = len(self.registration_buffer)
                        
                        cv2.putText(frame, f"CALIBRATING: {int((count/Config.REGISTRATION_FRAMES)*100)}%", 
                                   (w//2 - 100, h//2), Config.FONT, 1, Config.ORANGE_WARN, 2)
                        
                        if count >= Config.REGISTRATION_FRAMES:
                            success = self.face_sys.register_face(self.registering_user, self.registration_buffer)
                            if success:
                                self.voice.speak(f"Registration complete. Welcome, {self.registering_user}.")
                                self.ui.show_greeting(f"WELCOME, {self.registering_user.upper()}")
                                SoundFx.success()
                            else:
                                self.voice.speak("Registration failed. Please try again.")
                                SoundFx.error()
                            self.registering_user = None
                            
                    else:
                        name, conf = self.face_sys.identify(lms_list)
                        
                        if name != "UNKNOWN":
                            if self.identified_user != name:
                                self.identified_user = name
                                self.is_locked = False
                                self.ui.show_greeting(f"WELCOME BACK, {name.upper()}")
                                self.voice.speak(f"Welcome back, {name}.", emotion="happy")
                                SoundFx.success()
                        else:
                            if Config.LOCK_ON_UNKNOWN and self.identified_user is None:
                                self.is_locked = True
                            
                        cx, cy = int(lms_list[1][0]), int(lms_list[1][1])
                        color = Config.GOLD if name != "UNKNOWN" else Config.RED_ALERT
                        cv2.putText(frame, f"{name} ({int(conf*100)}%)", (cx, cy - 30), Config.FONT, 0.6, color, 1)
            
            # 3. Vision
            detections = self.vision.detect(frame)
            
            # 4. UI
            curr_time = time.time()
            fps = 1 / (curr_time - prev_time) if prev_time != 0 else 0
            prev_time = curr_time
            
            frame = self.ui.update(frame, detections, mouse_status, cursor_pos, fps, self.voice.is_listening, self.is_locked)
            
            # Draw Cursor
            if mouse_status not in ["INACTIVE", "NO_HAND", "KEY-PAUSED", "PAUSED (FIST)"]:
                cv2.circle(frame, cursor_pos, 8, Config.CYAN_HOLO, 2)
                cv2.circle(frame, cursor_pos, 4, Config.CYAN_HOLO, -1)
                
            # Debug Overlay
            if self.debug_mode:
                y = h - 100
                cv2.putText(frame, f"DEBUG: Hand={Config.GESTURE_HAND} Status={mouse_status}", (20, y), Config.FONT, 0.5, Config.WHITE, 1)
                cv2.putText(frame, f"Cursor: {cursor_pos}", (20, y+20), Config.FONT, 0.5, Config.WHITE, 1)
                
                if self.mouse.debug_info:
                    d = self.mouse.debug_info
                    info = f"Palm: {d.get('palm_size')} | Thresh: {d.get('threshold')} | L: {d.get('dist_left')} | R: {d.get('dist_right')}"
                    cv2.putText(frame, info, (20, y+40), Config.FONT, 0.5, Config.CYAN_HOLO, 1)
            
            # 5. Voice
            cmd = self.voice.get_command()
            if cmd:
                self.process_command(cmd)
            
            cv2.imshow(Config.APP_NAME, frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
                
        self.cap.release()
        cv2.destroyAllWindows()
        sys.exit(0)
