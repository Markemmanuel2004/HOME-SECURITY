import cv2
import numpy as np
import time
import os
from gesture_recognition import GestureRecognizer


class SecureEntrySystem:

    def __init__(self,
                 known_faces_folder=r"D:\MARK\FINAL PROJECT\OUTPUT",
                 identities=['MARK', 'CHIRAG', 'ANKIT', 'ADNAN'],
                 unlock_time=5.0,
                 log_folder="./security_logs"):

        self.identities = identities
        self.known_faces_folder = known_faces_folder
        self.unlock_time = unlock_time
        self.log_folder = log_folder

        os.makedirs(log_folder, exist_ok=True)

        self.face_cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
        )

        self.known_face_encodings = {}
        self.load_known_faces()

        self.gesture_recognizer = GestureRecognizer(stability_window=30)

        self.current_state = "LOCKED"
        self.recognized_identity = None
        self.face_recognition_time = None
        self.unlock_start_time = None

    # =========================
    # LOAD FACES
    # =========================
    def load_known_faces(self):
        print("Loading known faces...")

        for identity in self.identities:
            identity_path = os.path.join(self.known_faces_folder, identity)

            if not os.path.isdir(identity_path):
                print(f"Warning: No folder for {identity}")
                continue

            faces = []

            for img_name in os.listdir(identity_path):
                if img_name.lower().endswith('.jpg'):
                    img_path = os.path.join(identity_path, img_name)
                    img = cv2.imread(img_path, cv2.IMREAD_GRAYSCALE)

                    if img is not None:
                        img = cv2.resize(img, (224, 224))
                        vec = img.flatten().astype(np.float32)
                        vec = np.nan_to_num(vec)
                        faces.append(vec)

            if len(faces) > 0:
                self.known_face_encodings[identity] = np.array(faces)
                print(f"  Loaded {len(faces)} faces for {identity}")

        print(f"Total identities loaded: {len(self.known_face_encodings)}")

    # =========================
    # FACE RECOGNITION
    # =========================
    def detect_and_recognize_face(self, frame):

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        faces = self.face_cascade.detectMultiScale(
            gray, 1.1, 4, minSize=(100, 100)
        )

        if len(faces) == 0:
            return None, 0.0, None

        x, y, w, h = sorted(faces, key=lambda f: f[2]*f[3], reverse=True)[0]

        face_crop = gray[y:y+h, x:x+w]
        face_resized = cv2.resize(face_crop, (224, 224))
        face_vector = cv2.equalizeHist(face_resized).flatten().astype(np.float32)
        face_vector = np.nan_to_num(face_vector)

        best_match = None
        best_distance = float('inf')

        for identity, encodings in self.known_face_encodings.items():
            encodings = np.nan_to_num(encodings)

            distances = np.linalg.norm(encodings - face_vector, axis=1)
            min_distance = np.min(distances)

            if min_distance < best_distance:
                best_distance = min_distance
                best_match = identity

        threshold = 18000

        if best_distance < threshold:
            confidence = 1.0 - (best_distance / threshold)
            return best_match, confidence, (x, y, w, h)
        else:
            return None, 0.0, (x, y, w, h)

    # =========================
    # STATE MACHINE
    # =========================
    def process_state_machine(self, face_detected, face_identity, gesture, gesture_info):

        current_time = time.time()

        if self.current_state == "LOCKED":
            if face_detected and face_identity:
                self.current_state = "FACE_RECOGNIZED"
                self.recognized_identity = face_identity
                self.face_recognition_time = current_time

        elif self.current_state == "FACE_RECOGNIZED":

            if current_time - self.face_recognition_time > 10:
                self.reset_to_locked()

            elif not face_detected:
                self.reset_to_locked()

            elif gesture_info['confirmed'] and gesture_info['hold_time'] >= 2.0:

                if gesture in ['distress', 'ok_sign']:
                    self.current_state = "DISTRESS"
                    self.unlock_start_time = current_time

                elif gesture in ['unlock', 'peace', 'palm_open']:
                    self.current_state = "UNLOCKED"
                    self.unlock_start_time = current_time

        elif self.current_state in ["UNLOCKED", "DISTRESS"]:
            if current_time - self.unlock_start_time > self.unlock_time:
                self.reset_to_locked()

    def reset_to_locked(self):
        self.current_state = "LOCKED"
        self.recognized_identity = None
        self.face_recognition_time = None
        self.unlock_start_time = None

    # =========================
    # RUN
    # =========================
    def run(self):

        cap = cv2.VideoCapture(0)

        if not cap.isOpened():
            print("Camera error")
            return

        while True:
            ret, frame = cap.read()
            if not ret:
                break

            frame = cv2.flip(frame, 1)

            # FACE DETECTION
            face_identity, face_confidence, face_bbox = self.detect_and_recognize_face(frame)
            face_detected = face_identity is not None

            # DRAW FACE UI
            if face_bbox is not None:
                x, y, w, h = face_bbox

                if face_identity:
                    color = (0, 255, 0)
                    label = face_identity
                else:
                    color = (0, 0, 255)
                    label = "UNKNOWN PERSON"

                cv2.rectangle(frame, (x, y), (x+w, y+h), color, 2)
                cv2.putText(frame, label, (x, y-10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 2)

                # BIG WARNING
                if not face_identity:
                    cv2.putText(frame, "⚠ UNKNOWN DETECTED",
                                (20, 60),
                                cv2.FONT_HERSHEY_SIMPLEX, 1,
                                (0, 0, 255), 3)

            # GESTURE DETECTION
            frame, gesture, gesture_confirmed, gesture_info = \
                self.gesture_recognizer.process_frame(frame)

            # DRAW GESTURE UI
            frame = self.gesture_recognizer.draw_info_overlay(frame, gesture_info)

            # STATE MACHINE
            self.process_state_machine(face_detected, face_identity, gesture, gesture_info)

            # DRAW STATE
            cv2.putText(frame, f"STATE: {self.current_state}",
                        (20, frame.shape[0] - 20),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8,
                        (255, 255, 255), 2)

            # SHOW
            cv2.imshow('Secure Entry System', frame)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        cap.release()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    system = SecureEntrySystem()
    system.run()