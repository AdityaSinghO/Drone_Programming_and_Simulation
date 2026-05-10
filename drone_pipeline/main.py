import cv2
import time
import numpy as np
from pysimverse import Drone
from detector import CombatDetector

# --- Constants ---
MODEL_PATH = "yolo_v4_tiny"
ENEMY_MODEL = "enemy_model.xml"


def main():
    drone = Drone()
    detector = CombatDetector(MODEL_PATH)

    # Load the "brain" trained by trainer.py
    face_recognizer = cv2.face.LBPHFaceRecognizer_create()
    try:
        face_recognizer.read(ENEMY_MODEL)
    except:
        print("Warning: No trained model found. Run trainer.py first.")

    drone.connect()
    time.sleep(1)
    drone.take_off()

    cap = cv2.VideoCapture(0)
    ret, old_frame = cap.read()
    old_gray = cv2.cvtColor(old_frame, cv2.COLOR_BGR2GRAY)

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret: break

        display_frame = frame.copy()
        frame_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # 1. Top-Down Motion Detection (Farneback Optical Flow)
        flow = cv2.calcOpticalFlowFarneback(old_gray, frame_gray, None, 0.5, 3, 15, 3, 5, 1.2, 0)
        mag, _ = cv2.cartToPolar(flow[..., 0], flow[..., 1])
        if np.mean(mag) > 2.0:
            cv2.putText(display_frame, "MOTION ALERT", (10, 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)

        # 2. Identification Loop
        boxes = detector.detect_people(frame)
        for box in boxes:
            x, y, w, h = box
            team = detector.classify_team(frame, box)

            # Identify Unknowns via Face/Uniform Dataset
            roi_gray = frame_gray[y:y + h, x:x + w]
            if roi_gray.size > 0:
                roi_gray = cv2.resize(roi_gray, (100, 100))
                label, confidence = face_recognizer.predict(roi_gray)
                # Map LBPH distance to a 0-100% probability
                probability = max(0, min(100, 100 - confidence))
            else:
                probability = 0

            # --- COLOR LOGIC ---
            if team == "ENEMY" or (probability > 75):
                color = (0, 0, 255)  # Red
                label_text = f"ENEMY ({probability:.1f}%)"
            elif team == "ALLY":
                color = (0, 255, 0)  # Green
                label_text = "ALLY"
            else:
                color = (0, 255, 255)  # Yellow
                label_text = f"UNKNOWN - Prob: {probability:.1f}%"

            cv2.rectangle(display_frame, (x, y), (x + w, y + h), color, 2)
            cv2.putText(display_frame, label_text, (x, y - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

        # 3. Manual Keyboard Controls
        key = cv2.waitKey(1) & 0xFF
        lr, fb, ud, yaw = 0, 0, 0, 0

        if key == ord('w'):
            fb = 50
        elif key == ord('s'):
            fb = -50
        elif key == ord('a'):
            lr = -50
        elif key == ord('d'):
            lr = 50
        elif key == ord('u'):
            ud = 50
        elif key == ord('j'):
            ud = -50
        elif key == ord('q'):
            break  # Land

        drone.send_rc_control(lr, fb, ud, yaw)

        cv2.imshow("Drone Tactical HUD", display_frame)
        old_gray = frame_gray.copy()

    drone.land()
    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()