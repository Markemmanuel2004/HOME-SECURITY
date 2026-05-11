#!/usr/bin/env python3
"""
Quick test script to verify your setup
Run this first to make sure everything is installed correctly
"""

import sys

def test_imports():
    """Test if all required packages are installed"""
    print("Testing package imports...\n")
    
    tests = [
        ("OpenCV", "cv2"),
        ("MediaPipe", "mediapipe"),
        ("NumPy", "numpy"),
        ("Matplotlib", "matplotlib"),
    ]
    
    all_passed = True
    
    for name, package in tests:
        try:
            __import__(package)
            print(f"✓ {name:15} - OK")
        except ImportError as e:
            print(f"✗ {name:15} - FAILED: {e}")
            all_passed = False
    
    return all_passed


def test_camera():
    """Test camera access"""
    import cv2
    
    print("\n" + "="*50)
    print("Testing camera access...")
    print("="*50)
    
    cap = cv2.VideoCapture(0)
    
    if not cap.isOpened():
        print("✗ Camera FAILED - Cannot open camera")
        print("  Troubleshooting:")
        print("  - Check if camera is connected")
        print("  - Close other apps using camera")
        print("  - Try a different camera index (1, 2, etc.)")
        return False
    
    ret, frame = cap.read()
    
    if not ret or frame is None:
        print("✗ Camera FAILED - Cannot read frame")
        cap.release()
        return False
    
    print(f"✓ Camera OK - Resolution: {frame.shape[1]}x{frame.shape[0]}")
    cap.release()
    return True


def test_mediapipe():
    """Test MediaPipe hands"""
    import cv2
    import mediapipe as mp
    import numpy as np
    
    print("\n" + "="*50)
    print("Testing MediaPipe hand tracking...")
    print("="*50)
    
    try:
        mp_hands = mp.solutions.hands
        hands = mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=1,
            min_detection_confidence=0.5
        )
        
        # Create dummy image
        dummy_image = np.zeros((480, 640, 3), dtype=np.uint8)
        results = hands.process(dummy_image)
        
        hands.close()
        print("✓ MediaPipe OK - Hand tracking initialized")
        return True
        
    except Exception as e:
        print(f"✗ MediaPipe FAILED: {e}")
        return False


def test_face_cascade():
    """Test OpenCV face detection"""
    import cv2
    
    print("\n" + "="*50)
    print("Testing face detection cascade...")
    print("="*50)
    
    try:
        face_cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
        )
        
        if face_cascade.empty():
            print("✗ Face cascade FAILED - Cascade file not found")
            return False
        
        print("✓ Face cascade OK - Haar cascade loaded")
        return True
        
    except Exception as e:
        print(f"✗ Face cascade FAILED: {e}")
        return False


def test_gesture_module():
    """Test gesture recognition module"""
    print("\n" + "="*50)
    print("Testing gesture recognition module...")
    print("="*50)
    
    try:
        from gesture_recognition import GestureRecognizer
        
        recognizer = GestureRecognizer(stability_window=10)
        print("✓ Gesture module OK - GestureRecognizer loaded")
        recognizer.cleanup()
        return True
        
    except ImportError as e:
        print(f"✗ Gesture module FAILED: {e}")
        print("  Make sure gesture_recognition.py is in the same directory")
        return False
    except Exception as e:
        print(f"✗ Gesture module FAILED: {e}")
        return False


def interactive_test():
    """Interactive test with camera and hand tracking"""
    import cv2
    import mediapipe as mp
    
    print("\n" + "="*50)
    print("INTERACTIVE TEST - Live Hand Tracking")
    print("="*50)
    print("\nThis will open your camera and show hand tracking.")
    print("Try showing your hand to see if it's detected.")
    print("Press 'q' to quit\n")
    
    response = input("Run interactive test? (y/n): ").strip().lower()
    
    if response != 'y':
        print("Skipping interactive test.")
        return True
    
    mp_hands = mp.solutions.hands
    mp_drawing = mp.solutions.drawing_utils
    
    hands = mp_hands.Hands(
        static_image_mode=False,
        max_num_hands=1,
        min_detection_confidence=0.5
    )
    
    cap = cv2.VideoCapture(0)
    
    if not cap.isOpened():
        print("Cannot open camera for interactive test")
        return False
    
    print("\nShowing camera feed with hand tracking...")
    print("Show your hand and make gestures!")
    
    hand_detected_count = 0
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        frame = cv2.flip(frame, 1)
        image_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = hands.process(image_rgb)
        
        if results.multi_hand_landmarks:
            hand_detected_count += 1
            for hand_landmarks in results.multi_hand_landmarks:
                mp_drawing.draw_landmarks(
                    frame,
                    hand_landmarks,
                    mp_hands.HAND_CONNECTIONS
                )
            
            cv2.putText(frame, "HAND DETECTED!", (10, 50),
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        else:
            cv2.putText(frame, "Show your hand...", (10, 50),
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
        
        cv2.putText(frame, "Press 'q' to quit", (10, frame.shape[0] - 20),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
        
        cv2.imshow('Hand Tracking Test', frame)
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    
    cap.release()
    cv2.destroyAllWindows()
    hands.close()
    
    if hand_detected_count > 10:
        print(f"\n✓ Hand tracking working! Detected hand in {hand_detected_count} frames")
        return True
    else:
        print(f"\n⚠ Hand detected in only {hand_detected_count} frames")
        print("  This might work, but try improving lighting or hand position")
        return True


def main():
    """Run all tests"""
    print("="*60)
    print("HOME SECURITY SYSTEM - SETUP VERIFICATION")
    print("="*60)
    
    results = []
    
    # Test 1: Package imports
    results.append(("Packages", test_imports()))
    
    # Test 2: Camera
    results.append(("Camera", test_camera()))
    
    # Test 3: MediaPipe
    results.append(("MediaPipe", test_mediapipe()))
    
    # Test 4: Face cascade
    results.append(("Face Detection", test_face_cascade()))
    
    # Test 5: Gesture module
    results.append(("Gesture Module", test_gesture_module()))
    
    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    
    all_passed = True
    for name, passed in results:
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"{name:20} {status}")
        if not passed:
            all_passed = False
    
    print("="*60)
    
    if all_passed:
        print("\n🎉 ALL TESTS PASSED!")
        print("\nYou're ready to run the system:")
        print("  1. Test gestures only:  python gesture_recognition.py")
        print("  2. Full system:          python secure_entry_system.py")
        
        # Offer interactive test
        interactive_test()
        
    else:
        print("\n⚠️  SOME TESTS FAILED")
        print("\nPlease fix the failed tests before running the system.")
        print("Common fixes:")
        print("  - Install missing packages: pip install -r requirements.txt")
        print("  - Check camera connection")
        print("  - Restart Python/terminal")
    
    print("\n")
    return all_passed


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
