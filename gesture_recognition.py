import cv2
import mediapipe as mp
import numpy as np
import time
from collections import deque

class GestureRecognizer:
    """
    Live hand gesture recognition using MediaPipe
    No training required - uses geometric relationships between hand landmarks
    """
    
    def __init__(self, 
                 stability_window=30,  # frames to confirm gesture
                 confidence_threshold=0.7):
        
        # Initialize MediaPipe Hands
        self.mp_hands = mp.solutions.hands
        self.mp_drawing = mp.solutions.drawing_utils
        self.mp_drawing_styles = mp.solutions.drawing_styles
        
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=1,  # Only track one hand for security
            min_detection_confidence=0.7,
            min_tracking_confidence=0.5
        )
        
        # Gesture stability tracking
        self.stability_window = stability_window
        self.gesture_history = deque(maxlen=stability_window)
        self.confidence_threshold = confidence_threshold
        
        # Gesture state
        self.current_gesture = "none"
        self.gesture_confirmed = False
        self.gesture_start_time = None
        
    def get_finger_states(self, hand_landmarks, handedness):
        """
        Determine which fingers are extended
        Returns: [thumb, index, middle, ring, pinky] - True if extended
        """
        
        # Landmark indices for finger tips and joints
        finger_tips = [4, 8, 12, 16, 20]  # Thumb, Index, Middle, Ring, Pinky
        finger_pips = [3, 6, 10, 14, 18]  # PIP joints (one below tip)
        
        fingers_extended = []
        
        # Get all landmarks
        landmarks = hand_landmarks.landmark
        
        # Check thumb (different logic - horizontal movement)
        thumb_tip = landmarks[finger_tips[0]]
        thumb_ip = landmarks[finger_pips[0]]
        
        # Thumb is extended if tip is further from palm center than IP joint
        if handedness == "Right":
            thumb_extended = thumb_tip.x < thumb_ip.x
        else:  # Left hand
            thumb_extended = thumb_tip.x > thumb_ip.x
            
        fingers_extended.append(thumb_extended)
        
        # Check other fingers (vertical movement)
        for i in range(1, 5):
            tip = landmarks[finger_tips[i]]
            pip = landmarks[finger_pips[i]]
            
            # Finger is extended if tip is above PIP joint
            extended = tip.y < pip.y
            fingers_extended.append(extended)
        
        return fingers_extended
    
    def calculate_hand_openness(self, hand_landmarks):
        """
        Calculate how "open" the hand is (0 = closed fist, 1 = fully open)
        """
        landmarks = hand_landmarks.landmark
        
        # Calculate average distance between fingertips and palm center
        palm_center = landmarks[0]  # Wrist
        fingertips = [landmarks[i] for i in [4, 8, 12, 16, 20]]
        
        distances = []
        for tip in fingertips:
            dist = np.sqrt(
                (tip.x - palm_center.x)**2 + 
                (tip.y - palm_center.y)**2
            )
            distances.append(dist)
        
        avg_distance = np.mean(distances)
        
        # Normalize (typical range: 0.1 to 0.3)
        openness = np.clip((avg_distance - 0.1) / 0.2, 0, 1)
        return openness
    
    def recognize_gesture(self, hand_landmarks, handedness):
        """
        Recognize specific gestures based on hand landmarks
        
        Gestures:
        - "unlock": Thumbs up
        - "distress": Closed fist
        - "peace": Peace sign (index + middle extended)
        - "palm_open": All fingers extended
        - "none": No recognizable gesture
        """
        
        fingers = self.get_finger_states(hand_landmarks, handedness)
        openness = self.calculate_hand_openness(hand_landmarks)
        
        # Gesture 1: THUMBS UP (Unlock gesture)
        # Only thumb extended, other fingers closed
        if fingers[0] and not any(fingers[1:]):
            landmarks = hand_landmarks.landmark
            # Additional check: thumb pointing upward
            thumb_tip = landmarks[4]
            thumb_mcp = landmarks[2]
            if thumb_tip.y < thumb_mcp.y:  # Thumb pointing up
                return "unlock", 0.9
        
        # Gesture 2: CLOSED FIST (Distress signal)
        # All fingers closed, hand very closed
        if not any(fingers) and openness < 0.3:
            return "distress", 0.95
        
        # Gesture 3: PEACE SIGN (Alternative unlock)
        # Only index and middle fingers extended
        if not fingers[0] and fingers[1] and fingers[2] and not fingers[3] and not fingers[4]:
            return "peace", 0.85
        
        # Gesture 4: OPEN PALM (Alternative unlock)
        # All fingers extended
        if all(fingers) and openness > 0.7:
            return "palm_open", 0.8
        
        # Gesture 5: OK SIGN (Alternative distress - thumb + index forming circle)
        # This is more complex, using distance between thumb and index tips
        landmarks = hand_landmarks.landmark
        thumb_tip = landmarks[4]
        index_tip = landmarks[8]
        
        distance = np.sqrt(
            (thumb_tip.x - index_tip.x)**2 + 
            (thumb_tip.y - index_tip.y)**2
        )
        
        # If thumb and index are very close, and other fingers extended
        if distance < 0.05 and fingers[2] and fingers[3] and fingers[4]:
            return "ok_sign", 0.8
        
        return "none", 0.0
    
    def update_gesture_stability(self, gesture, confidence):
        """
        Track gesture over time to ensure it's intentional
        Returns True if gesture is stable and confirmed
        """
        
        # Add current gesture to history
        self.gesture_history.append((gesture, confidence))
        
        # Check if we have enough frames
        if len(self.gesture_history) < self.stability_window:
            return False, "none", 0.0
        
        # Count occurrences of each gesture in the window
        gesture_counts = {}
        total_confidence = {}
        
        for g, c in self.gesture_history:
            if g not in gesture_counts:
                gesture_counts[g] = 0
                total_confidence[g] = 0
            gesture_counts[g] += 1
            total_confidence[g] += c
        
        # Find most common gesture
        if not gesture_counts:
            return False, "none", 0.0
        
        most_common = max(gesture_counts, key=gesture_counts.get)
        consistency = gesture_counts[most_common] / len(self.gesture_history)
        avg_confidence = total_confidence[most_common] / gesture_counts[most_common]
        
        # Gesture is confirmed if it appears in >80% of recent frames
        # and has high average confidence
        if consistency > 0.8 and avg_confidence > self.confidence_threshold:
            return True, most_common, avg_confidence
        
        return False, "none", 0.0
    
    def process_frame(self, frame):
        """
        Process a single video frame
        Returns: (annotated_frame, gesture, confirmed, info_dict)
        """
        
        # Convert BGR to RGB
        image_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # Process with MediaPipe
        results = self.hands.process(image_rgb)
        
        # Draw on frame
        annotated_frame = frame.copy()
        
        gesture = "none"
        confidence = 0.0
        handedness = "Right"
        
        if results.multi_hand_landmarks:
            # Get first hand (we only track one for security)
            hand_landmarks = results.multi_hand_landmarks[0]
            handedness_info = results.multi_handedness[0]
            handedness = handedness_info.classification[0].label
            
            # Draw hand landmarks
            self.mp_drawing.draw_landmarks(
                annotated_frame,
                hand_landmarks,
                self.mp_hands.HAND_CONNECTIONS,
                self.mp_drawing_styles.get_default_hand_landmarks_style(),
                self.mp_drawing_styles.get_default_hand_connections_style()
            )
            
            # Recognize gesture
            gesture, confidence = self.recognize_gesture(hand_landmarks, handedness)
        
        # Update stability tracking
        confirmed, stable_gesture, stable_confidence = self.update_gesture_stability(
            gesture, confidence
        )
        
        # Track gesture confirmation timing
        if confirmed and stable_gesture != "none":
            if self.gesture_start_time is None:
                self.gesture_start_time = time.time()
            hold_time = time.time() - self.gesture_start_time
        else:
            self.gesture_start_time = None
            hold_time = 0.0
        
        # Prepare info dictionary
        info = {
            'gesture': stable_gesture if confirmed else "none",
            'raw_gesture': gesture,
            'confidence': stable_confidence,
            'confirmed': confirmed,
            'handedness': handedness,
            'hold_time': hold_time
        }
        
        return annotated_frame, stable_gesture if confirmed else "none", confirmed, info
    
    def draw_info_overlay(self, frame, info):
        """
        Draw gesture information on frame
        """
        h, w = frame.shape[:2]
        
        # Create semi-transparent overlay
        overlay = frame.copy()
        cv2.rectangle(overlay, (10, 10), (w-10, 150), (0, 0, 0), -1)
        cv2.addWeighted(overlay, 0.3, frame, 0.7, 0, frame)
        
        # Colors for different states
        color_normal = (255, 255, 255)
        color_unlock = (0, 255, 0)
        color_distress = (0, 0, 255)
        
        gesture = info['gesture']
        confirmed = info['confirmed']
        hold_time = info['hold_time']
        
        # Determine color based on gesture
        if gesture in ['unlock', 'peace', 'palm_open']:
            text_color = color_unlock
            status = "UNLOCK GESTURE DETECTED"
        elif gesture in ['distress', 'ok_sign']:
            text_color = color_distress
            status = "⚠️ DISTRESS SIGNAL ⚠️"
        else:
            text_color = color_normal
            status = "Waiting for gesture..."
        
        # Draw text
        cv2.putText(frame, status, (20, 40), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.8, text_color, 2)
        
        cv2.putText(frame, f"Gesture: {gesture.upper()}", (20, 70),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, color_normal, 2)
        
        cv2.putText(frame, f"Confidence: {info['confidence']:.2f}", (20, 95),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, color_normal, 2)
        
        if confirmed and hold_time > 0:
            cv2.putText(frame, f"Hold Time: {hold_time:.1f}s", (20, 120),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, color_normal, 2)
            
            # Progress bar for hold time (require 2 seconds)
            required_time = 2.0
            progress = min(hold_time / required_time, 1.0)
            bar_width = int((w - 40) * progress)
            
            cv2.rectangle(frame, (20, 130), (20 + bar_width, 145), 
                         text_color, -1)
            cv2.rectangle(frame, (20, 130), (w - 20, 145), 
                         color_normal, 2)
        
        return frame
    
    def cleanup(self):
        """Release resources"""
        self.hands.close()


# ==============================
# DEMO / TESTING
# ==============================
def main():
    """
    Test the gesture recognition system with webcam
    """
    
    print("=== Hand Gesture Recognition System ===")
    print("\nGestures:")
    print("  🔓 UNLOCK: Thumbs up, Peace sign, or Open palm")
    print("  🚨 DISTRESS: Closed fist or OK sign")
    print("\nHold gesture for 2 seconds to confirm")
    print("Press 'q' to quit\n")
    
    # Initialize recognizer
    recognizer = GestureRecognizer(stability_window=30)
    
    # Open webcam
    cap = cv2.VideoCapture(0)
    
    if not cap.isOpened():
        print("Error: Cannot open webcam")
        return
    
    # Set resolution
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
    
    gesture_executed = False
    
    while True:
        ret, frame = cap.read()
        if not ret:
            print("Error: Cannot read frame")
            break
        
        # Flip frame horizontally for mirror view
        frame = cv2.flip(frame, 1)
        
        # Process frame
        annotated_frame, gesture, confirmed, info = recognizer.process_frame(frame)
        
        # Draw info overlay
        annotated_frame = recognizer.draw_info_overlay(annotated_frame, info)
        
        # Check if gesture is confirmed and held for 2 seconds
        if confirmed and info['hold_time'] >= 2.0 and not gesture_executed:
            if gesture in ['unlock', 'peace', 'palm_open']:
                print("\n✅ UNLOCK GESTURE CONFIRMED!")
                print(">>> Door would unlock here <<<")
                gesture_executed = True
                
            elif gesture in ['distress', 'ok_sign']:
                print("\n🚨 DISTRESS SIGNAL DETECTED!")
                print(">>> Alert authorities + unlock door <<<")
                gesture_executed = True
        
        # Reset when no gesture
        if gesture == "none":
            gesture_executed = False
        
        # Display
        cv2.imshow('Hand Gesture Recognition - Home Security', annotated_frame)
        
        # Quit on 'q'
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    
    # Cleanup
    cap.release()
    cv2.destroyAllWindows()
    recognizer.cleanup()
    
    print("\nGesture recognition stopped.")


if __name__ == "__main__":
    main()
