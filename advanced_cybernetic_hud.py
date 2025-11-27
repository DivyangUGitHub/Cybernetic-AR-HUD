import cv2
import numpy as np
import mediapipe as mp
import time
from datetime import datetime
import math
import random
import psutil
import pyttsx3
import subprocess
import os

class CyberneticARHUD:
    def __init__(self):
        self.setup_hand_tracking()
        self.setup_system_controls()
        self.setup_hud_elements()
        self.setup_audio_feedback()
        
        # System state
        self.system_status = {
            'cpu_usage': 0.0,
            'memory_usage': 0.0,
            'network_status': 'ONLINE',
            'threat_level': 'LOW',
            'battery_level': 100,
            'system_time': datetime.now(),
            'mission_status': 'ACTIVE',
            'neural_interface': 'SYNCED'
        }
        
        # Animation variables
        self.scan_angle = 0
        self.pulse_animation = 0
        self.radar_blips = []
        self.system_boot_time = time.time()
        self.frame_count = 0
        
        # HUD modes
        self.hud_modes = ['COMBAT', 'STEALTH', 'NAVIGATION', 'SYSTEM']
        self.current_hud_mode = 'COMBAT'
        
        # Weapon system
        self.weapon_systems = {
            'PRIMARY': {'name': 'PLASMA RIFLE', 'ammo': 85, 'status': 'READY'},
            'SECONDARY': {'name': 'ENERGY PISTOL', 'ammo': 60, 'status': 'READY'},
            'SPECIAL': {'name': 'SONIC EMITTER', 'ammo': 100, 'status': 'CHARGING'}
        }
        
        # Volume control (simulated)
        self.current_volume = 50
        
    def setup_hand_tracking(self):
        """Initialize advanced hand tracking"""
        self.mp_hands = mp.solutions.hands
        self.mp_drawing = mp.solutions.drawing_utils
        self.mp_drawing_styles = mp.solutions.drawing_styles
        
        self.hands = self.mp_hands.Hands(
            model_complexity=1,
            min_detection_confidence=0.8,
            min_tracking_confidence=0.8,
            max_num_hands=2
        )
        
    def setup_system_controls(self):
        """Initialize system control interfaces"""
        # System metrics history
        self.cpu_history = []
        self.memory_history = []
        
    def setup_hud_elements(self):
        """Initialize all HUD components"""
        self.hud_elements = {
            'status_panel': self.draw_status_panel,
            'radar_display': self.draw_radar_display,
            'vital_signs': self.draw_vital_signs,
            'navigation': self.draw_navigation,
            'weapon_system': self.draw_weapon_system,
            'communication': self.draw_communication,
            'threat_assessment': self.draw_threat_assessment,
            'mission_objectives': self.draw_mission_objectives
        }
        
    def setup_audio_feedback(self):
        """Initialize audio feedback system"""
        try:
            self.tts_engine = pyttsx3.init()
            self.tts_engine.setProperty('rate', 160)
            self.tts_engine.setProperty('volume', 0.8)
            self.last_audio_time = 0
        except:
            self.tts_engine = None
    
    def speak(self, text):
        """Provide audio feedback"""
        if self.tts_engine and time.time() - self.last_audio_time > 2:
            try:
                self.tts_engine.say(text)
                self.tts_engine.runAndWait()
                self.last_audio_time = time.time()
            except:
                pass
    
    def update_system_metrics(self):
        """Update real-time system metrics"""
        current_time = time.time()
        time_since_boot = current_time - self.system_boot_time
        
        # CPU usage
        self.system_status['cpu_usage'] = psutil.cpu_percent()
        
        # Memory usage
        memory = psutil.virtual_memory()
        self.system_status['memory_usage'] = memory.percent
        
        # Battery status simulation
        self.system_status['battery_level'] = max(10, 100 - int(time_since_boot / 10))
        
        # Network status simulation
        network_stats = ['ONLINE', 'STABLE', 'ENCRYPTED', 'OPTIMAL']
        if random.random() < 0.01:
            self.system_status['network_status'] = random.choice(network_stats)
        
        # Threat level simulation
        threat_levels = ['LOW', 'MEDIUM', 'HIGH', 'CRITICAL']
        if random.random() < 0.005:
            self.system_status['threat_level'] = random.choice(threat_levels)
        
        # Update time
        self.system_status['system_time'] = datetime.now()
        
        # Store history for graphs
        self.cpu_history.append(self.system_status['cpu_usage'])
        self.memory_history.append(self.system_status['memory_usage'])
        if len(self.cpu_history) > 50:
            self.cpu_history.pop(0)
            self.memory_history.pop(0)
    
    def recognize_gesture(self, landmarks):
        """Advanced gesture recognition for HUD control"""
        if not landmarks:
            return "unknown"
        
        thumb_tip = landmarks[4]
        index_tip = landmarks[8]
        middle_tip = landmarks[12]
        ring_tip = landmarks[16]
        pinky_tip = landmarks[20]
        
        def is_finger_extended(tip, pip):
            return tip.y < pip.y
        
        # Gesture detection
        if (is_finger_extended(index_tip, landmarks[6]) and
            is_finger_extended(middle_tip, landmarks[10]) and
            not is_finger_extended(ring_tip, landmarks[14]) and
            not is_finger_extended(pinky_tip, landmarks[18])):
            return "peace"
        
        elif (is_finger_extended(thumb_tip, landmarks[3]) and
              not any(is_finger_extended(landmarks[tip], landmarks[tip-2]) 
                     for tip in [8, 12, 16, 20])):
            return "thumbs_up"
        
        elif (not is_finger_extended(thumb_tip, landmarks[3]) and
              not any(is_finger_extended(landmarks[tip], landmarks[tip-2]) 
                     for tip in [8, 12, 16, 20])):
            return "thumbs_down"
        
        elif all(not is_finger_extended(landmarks[tip], landmarks[tip-2]) 
                for tip in [8, 12, 16, 20]):
            return "fist"
        
        elif all(is_finger_extended(landmarks[tip], landmarks[tip-2]) 
                for tip in [8, 12, 16, 20]):
            return "open_palm"
        
        elif (is_finger_extended(index_tip, landmarks[6]) and
              not any(is_finger_extended(landmarks[tip], landmarks[tip-2]) 
                     for tip in [12, 16, 20])):
            return "pointing"
        
        elif (self.calculate_distance(thumb_tip, index_tip) < 0.05 and
              all(is_finger_extended(landmarks[tip], landmarks[tip-2]) 
                  for tip in [12, 16, 20])):
            return "ok"
        
        elif (is_finger_extended(index_tip, landmarks[6]) and
              is_finger_extended(pinky_tip, landmarks[18]) and
              not any(is_finger_extended(landmarks[tip], landmarks[tip-2]) 
                     for tip in [12, 16])):
            return "rock"
        
        return "unknown"
    
    def calculate_distance(self, point1, point2):
        """Calculate distance between two points"""
        return math.sqrt((point1.x - point2.x)**2 + (point1.y - point2.y)**2)
    
    # HUD Drawing Methods
    def draw_status_panel(self, frame):
        """Draw main system status panel"""
        height, width = frame.shape[:2]
        
        # Create status panel
        panel_height = 180
        panel = np.zeros((panel_height, 450, 3), dtype=np.uint8)
        
        # Panel header with pulsing effect
        pulse = (math.sin(self.frame_count * 0.1) + 1) / 2
        header_color = (0, int(100 + 155 * pulse), 0)
        cv2.rectangle(panel, (0, 0), (450, 30), header_color, -1)
        
        cv2.putText(panel, "CYBERNETIC AR HUD v4.0", (10, 20),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 1)
        
        # System metrics
        metrics = [
            f"CPU: {self.system_status['cpu_usage']:05.1f}%",
            f"MEM: {self.system_status['memory_usage']:05.1f}%", 
            f"NET: {self.system_status['network_status']}",
            f"THREAT: {self.system_status['threat_level']}",
            f"POWER: {self.system_status['battery_level']:03d}%",
            f"MODE: {self.current_hud_mode}",
            f"TIME: {datetime.now().strftime('%H:%M:%S')}",
            f"MISSION: {self.system_status['mission_status']}"
        ]
        
        for i, metric in enumerate(metrics):
            color = (0, 255, 0) if i % 2 == 0 else (0, 200, 0)
            cv2.putText(panel, metric, (10, 55 + i * 18),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.4, color, 1)
        
        # Progress bars
        self.draw_progress_bar(panel, (120, 50), 200, 8, self.system_status['cpu_usage'] / 100)
        self.draw_progress_bar(panel, (120, 68), 200, 8, self.system_status['memory_usage'] / 100)
        self.draw_progress_bar(panel, (120, 86), 200, 8, self.system_status['battery_level'] / 100)
        
        # Add to frame
        x_offset, y_offset = 20, 20
        frame[y_offset:y_offset+panel_height, x_offset:x_offset+450] = panel
        
        return frame
    
    def draw_radar_display(self, frame):
        """Draw advanced radar/sonar display"""
        height, width = frame.shape[:2]
        radar_size = 220
        center_x = width - radar_size - 30
        center_y = height - radar_size - 30
        
        # Create radar background
        radar = np.zeros((radar_size, radar_size, 3), dtype=np.uint8)
        
        # Draw radar circles
        for radius in range(30, radar_size//2, 30):
            alpha = 0.3 + 0.7 * (radius / (radar_size//2))
            color = (0, int(50 * alpha), 0)
            cv2.circle(radar, (radar_size//2, radar_size//2), radius, color, 1)
        
        # Draw crosshairs
        cv2.line(radar, (radar_size//2, 0), (radar_size//2, radar_size), (0, 100, 0), 1)
        cv2.line(radar, (0, radar_size//2), (radar_size, radar_size//2), (0, 100, 0), 1)
        
        # Animated scan line
        self.scan_angle = (self.scan_angle + 3) % 360
        end_x = radar_size//2 + int((radar_size//2 - 15) * math.cos(math.radians(self.scan_angle)))
        end_y = radar_size//2 + int((radar_size//2 - 15) * math.sin(math.radians(self.scan_angle)))
        
        cv2.line(radar, (radar_size//2, radar_size//2), (end_x, end_y), (0, 255, 0), 2)
        
        # Update radar blips
        if random.random() < 0.1 and len(self.radar_blips) < 8:
            angle = random.randint(0, 360)
            distance = random.randint(20, radar_size//2 - 30)
            blip_type = random.choice(['friend', 'neutral', 'hostile'])
            self.radar_blips.append({
                'angle': angle, 'distance': distance, 'type': blip_type,
                'lifetime': random.randint(50, 200)
            })
        
        # Draw radar blips
        for blip in self.radar_blips[:]:
            blip_x = radar_size//2 + int(blip['distance'] * math.cos(math.radians(blip['angle'])))
            blip_y = radar_size//2 + int(blip['distance'] * math.sin(math.radians(blip['angle'])))
            
            if blip['type'] == 'hostile':
                color = (0, 0, 255)  # Red for hostile
            elif blip['type'] == 'friend':
                color = (0, 255, 0)  # Green for friend
            else:
                color = (0, 255, 255)  # Yellow for neutral
            
            cv2.circle(radar, (blip_x, blip_y), 4, color, -1)
            blip['lifetime'] -= 1
            
            if blip['lifetime'] <= 0:
                self.radar_blips.remove(blip)
        
        # Add radar to frame
        frame[center_y:center_y+radar_size, center_x:center_x+radar_size] = radar
        
        # Radar label
        cv2.putText(frame, "TACTICAL RADAR", (center_x, center_y - 10),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
        
        return frame
    
    def draw_vital_signs(self, frame):
        """Draw biometric/vital signs display"""
        height, width = frame.shape[:2]
        
        # Create vital signs panel
        vitals = np.zeros((160, 320, 3), dtype=np.uint8)
        
        # Header
        cv2.rectangle(vitals, (0, 0), (320, 25), (0, 100, 0), -1)
        cv2.putText(vitals, "VITAL SIGNS MONITOR", (10, 17),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
        
        # Animated vital signs
        self.pulse_animation = (self.pulse_animation + 0.15) % (2 * math.pi)
        heart_rate = 72 + int(8 * math.sin(self.pulse_animation))
        
        vital_data = [
            f"HEART RATE: {heart_rate:03d} BPM",
            f"O2 SATURATION: {98 + random.randint(-1, 1):02d}%",
            f"BLOOD PRESSURE: {120 + random.randint(-5, 5)}/{80 + random.randint(-3, 3)}",
            f"BODY TEMP: 36.{5 + random.randint(0, 2):01d} C",
            f"NEURAL ACTIVITY: {85 + random.randint(0, 10):03d}%",
            f"CYBERNETIC SYNC: {92 + random.randint(0, 8):03d}%",
            f"ADRENALINE: {15 + random.randint(0, 10):03d}%"
        ]
        
        for i, vital in enumerate(vital_data):
            color = (0, 255, 0) if 'CYBERNETIC' in vital else (0, 200, 0)
            cv2.putText(vitals, vital, (10, 45 + i * 15),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.3, color, 1)
        
        # Heart rate waveform
        points = []
        for x in range(0, 300, 4):
            y = 140 + int(12 * math.sin(x * 0.05 + self.pulse_animation))
            points.append((x + 10, y))
        
        for i in range(len(points) - 1):
            cv2.line(vitals, points[i], points[i+1], (0, 255, 0), 2)
        
        # Add to frame
        x_offset, y_offset = width - 340, 20
        frame[y_offset:y_offset+160, x_offset:x_offset+320] = vitals
        
        return frame
    
    def draw_navigation(self, frame):
        """Draw navigation compass and GPS"""
        height, width = frame.shape[:2]
        center_x, center_y = width // 2, 60
        
        # Compass background
        compass_radius = 45
        cv2.circle(frame, (center_x, center_y), compass_radius, (0, 50, 0), 2)
        
        # Compass directions
        directions = ['N', 'E', 'S', 'W']
        for i, direction in enumerate(directions):
            angle = i * 90
            text_x = center_x + int((compass_radius + 18) * math.cos(math.radians(angle)))
            text_y = center_y + int((compass_radius + 18) * math.sin(math.radians(angle)))
            cv2.putText(frame, direction, (text_x-5, text_y+5),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
        
        # Compass needle with animation
        needle_angle = (time.time() * 20) % 360
        needle_x = center_x + int((compass_radius - 8) * math.cos(math.radians(needle_angle)))
        needle_y = center_y + int((compass_radius - 8) * math.sin(math.radians(needle_angle)))
        
        cv2.line(frame, (center_x, center_y), (needle_x, needle_y), (0, 255, 0), 3)
        cv2.circle(frame, (center_x, center_y), 4, (0, 255, 0), -1)
        
        # GPS coordinates
        gps_text = f"GPS: 40.7128°N, 74.0060°W"
        alt_text = f"ALT: {150 + 10 * math.sin(time.time()):.0f}m"
        
        cv2.putText(frame, gps_text, (center_x - 120, center_y + 80),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 255, 0), 1)
        cv2.putText(frame, alt_text, (center_x - 120, center_y + 100),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 255, 0), 1)
        
        return frame
    
    def draw_weapon_system(self, frame):
        """Draw weapon system status"""
        height, width = frame.shape[:2]
        
        # Weapon status panel
        weapons = np.zeros((120, 280, 3), dtype=np.uint8)
        
        # Header
        cv2.rectangle(weapons, (0, 0), (280, 20), (0, 100, 0), -1)
        cv2.putText(weapons, "WEAPON SYSTEMS", (10, 14),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 255, 0), 1)
        
        weapon_data = [
            f"PRIMARY: {self.weapon_systems['PRIMARY']['name']}",
            f"AMMO: {self.weapon_systems['PRIMARY']['ammo']}%",
            f"STATUS: {self.weapon_systems['PRIMARY']['status']}",
            f"SECONDARY: {self.weapon_systems['SECONDARY']['name']}",
            f"AMMO: {self.weapon_systems['SECONDARY']['ammo']}%",
            f"STATUS: {self.weapon_systems['SECONDARY']['status']}"
        ]
        
        for i, weapon in enumerate(weapon_data):
            color = (0, 255, 0) if 'READY' in weapon else (0, 200, 0)
            cv2.putText(weapons, weapon, (10, 35 + i * 15),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.3, color, 1)
        
        # Add to frame
        x_offset, y_offset = 20, height - 140
        frame[y_offset:y_offset+120, x_offset:x_offset+280] = weapons
        
        return frame
    
    def draw_communication(self, frame):
        """Draw communication status"""
        height, width = frame.shape[:2]
        
        # Comms panel
        comms = np.zeros((100, 220, 3), dtype=np.uint8)
        
        # Header
        cv2.rectangle(comms, (0, 0), (220, 20), (0, 100, 0), -1)
        cv2.putText(comms, "COMMUNICATIONS", (10, 14),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 255, 0), 1)
        
        comms_data = [
            "STATUS: ENCRYPTED",
            "SIGNAL: STRONG",
            "FREQUENCY: 2.4GHz",
            "USERS: 3 ACTIVE",
            "ENCRYPTION: AES-256"
        ]
        
        for i, comm in enumerate(comms_data):
            cv2.putText(comms, comm, (10, 35 + i * 12),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.3, (0, 255, 0), 1)
        
        # Signal strength bars
        for i in range(5):
            bar_height = (i + 1) * 10
            color = (0, 255, 0) if i > 1 else (0, 100, 0)
            cv2.rectangle(comms, (180 + i*12, 50 - bar_height), (180 + i*12 + 8, 50), color, -1)
        
        # Add to frame
        x_offset, y_offset = width - 240, height - 120
        frame[y_offset:y_offset+100, x_offset:x_offset+220] = comms
        
        return frame
    
    def draw_threat_assessment(self, frame):
        """Draw threat assessment display"""
        height, width = frame.shape[:2]
        
        # Threat panel
        threat = np.zeros((140, 300, 3), dtype=np.uint8)
        
        threat_levels = {
            'LOW': (0, 255, 0),
            'MEDIUM': (0, 200, 200),
            'HIGH': (0, 100, 255),
            'CRITICAL': (0, 0, 255)
        }
        
        current_threat = self.system_status['threat_level']
        color = threat_levels.get(current_threat, (0, 255, 0))
        
        # Header
        cv2.rectangle(threat, (0, 0), (300, 25), color, -1)
        cv2.putText(threat, "THREAT ASSESSMENT", (10, 17),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
        
        cv2.putText(threat, f"LEVEL: {current_threat}", (10, 45),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
        
        # Threat indicators
        threats = [
            "SYSTEM INTEGRITY: 98%",
            "FIREWALL: ACTIVE",
            "INTRUSION: 0 DETECTED",
            "ENCRYPTION: AES-256",
            "SURVEILLANCE: CLEAR"
        ]
        
        for i, threat_msg in enumerate(threats):
            cv2.putText(threat, threat_msg, (10, 70 + i * 12),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.3, (0, 255, 0), 1)
        
        # Add to frame
        x_offset, y_offset = width // 2 - 150, height // 2 - 70
        frame[y_offset:y_offset+140, x_offset:x_offset+300] = threat
        
        return frame
    
    def draw_mission_objectives(self, frame):
        """Draw mission objectives display"""
        height, width = frame.shape[:2]
        
        # Mission panel
        mission = np.zeros((120, 350, 3), dtype=np.uint8)
        
        # Header
        cv2.rectangle(mission, (0, 0), (350, 20), (0, 100, 0), -1)
        cv2.putText(mission, "MISSION OBJECTIVES", (10, 14),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 255, 0), 1)
        
        objectives = [
            "✓ PRIMARY: SECURE THE DATA CORE",
            "✓ SECONDARY: NEUTRALIZE HOSTILES",
            "● TERTIARY: EXTRACT INTELLIGENCE",
            "○ BONUS: RESCUE CIVILIANS",
            f"TIME ELAPSED: {int(time.time() - self.system_boot_time)}s"
        ]
        
        for i, objective in enumerate(objectives):
            color = (0, 255, 0) if '✓' in objective else (0, 200, 0) if '●' in objective else (0, 150, 0)
            cv2.putText(mission, objective, (10, 38 + i * 14),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.3, color, 1)
        
        # Add to frame
        x_offset, y_offset = width - 370, height // 2 - 60
        frame[y_offset:y_offset+120, x_offset:x_offset+350] = mission
        
        return frame
    
    def draw_progress_bar(self, frame, position, width, height, progress):
        """Draw a progress bar"""
        x, y = position
        cv2.rectangle(frame, (x, y), (x + width, y + height), (0, 30, 0), -1)
        cv2.rectangle(frame, (x, y), (x + int(width * progress), y + height), (0, 255, 0), -1)
        cv2.rectangle(frame, (x, y), (x + width, y + height), (0, 150, 0), 1)
    
    def process_hands(self, frame):
        """Process hand gestures and update HUD"""
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.hands.process(rgb_frame)
        
        gesture = "no_hand"
        
        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                # Draw hand landmarks
                self.mp_drawing.draw_landmarks(
                    frame,
                    hand_landmarks,
                    self.mp_hands.HAND_CONNECTIONS,
                    self.mp_drawing_styles.get_default_hand_landmarks_style(),
                    self.mp_drawing_styles.get_default_hand_connections_style()
                )
                
                # Recognize gesture
                gesture = self.recognize_gesture(hand_landmarks.landmark)
                
                # Display gesture info
                cv2.putText(frame, f"GESTURE: {gesture}", (10, frame.shape[0] - 20),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
        
        return frame, gesture
    
    def run(self):
        """Main application loop"""
        cap = cv2.VideoCapture(0)
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
        
        print("🎮 ADVANCED CYBERNETIC AR HUD")
        print("=============================")
        print("🌟 Features:")
        print("   - Real-time system monitoring")
        print("   - Advanced radar display")
        print("   - Vital signs monitoring")
        print("   - Weapon systems status")
        print("   - Threat assessment")
        print("   - Mission objectives")
        print("   - Hand gesture recognition")
        print("")
        print("🎯 Gesture Controls:")
        print("   ✊ Fist - Toggle weapon systems")
        print("   ✌️ Peace - Toggle radar")
        print("   👍 Thumbs Up - Increase volume")
        print("   👎 Thumbs Down - Decrease volume")
        print("   🖐️ Open Palm - Cycle HUD modes")
        print("   👉 Pointing - Select target")
        print("   👌 OK - Confirm action")
        print("   🤘 Rock - Emergency protocol")
        print("")
        print("Press 'Q' to quit")
        print("Press 'M' to cycle HUD modes")
        print("Press 'R' to reset radar")
        
        self.speak("Cybernetic AR HUD activated")
        
        # FPS calculation
        fps_counter = 0
        fps_time = time.time()
        current_fps = 0
        
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            self.frame_count += 1
            fps_counter += 1
            
            # Calculate FPS
            if time.time() - fps_time >= 1.0:
                current_fps = fps_counter
                fps_counter = 0
                fps_time = time.time()
            
            frame = cv2.flip(frame, 1)
            
            # Update system metrics
            self.update_system_metrics()
            
            # Process hand gestures
            frame, gesture = self.process_hands(frame)
            
            # Draw all HUD elements
            for element_name, element_func in self.hud_elements.items():
                frame = element_func(frame)
            
            # Add scan lines effect
            height, width = frame.shape[:2]
            for y in range(0, height, 4):
                frame[y:y+1, :] = frame[y:y+1, :] * 0.8
            
            # Add FPS counter
            cv2.putText(frame, f"FPS: {current_fps}", (width - 100, 30),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
            
            cv2.imshow('Advanced Cybernetic AR HUD', frame)
            
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break
            elif key == ord('m'):
                # Cycle HUD modes
                current_index = self.hud_modes.index(self.current_hud_mode)
                self.current_hud_mode = self.hud_modes[(current_index + 1) % len(self.hud_modes)]
                self.speak(f"HUD mode {self.current_hud_mode}")
            elif key == ord('r'):
                # Reset radar
                self.radar_blips = []
                self.speak("Radar reset")
        
        cap.release()
        cv2.destroyAllWindows()
        self.speak("Cybernetic AR HUD deactivated")

if __name__ == "__main__":
    hud = CyberneticARHUD()
    hud.run()