import cv2
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
from mediapipe import solutions
from mediapipe.framework.formats import landmark_pb2
import numpy as np

# --- Drawing utility ---
def draw_landmarks_on_frame(frame, detection_result):
    hand_landmarks_list = detection_result.hand_landmarks
    handedness_list = detection_result.handedness

    for idx in range(len(hand_landmarks_list)):
        hand_landmarks = hand_landmarks_list[idx]
        handedness = handedness_list[idx]

        # Convert to proto for drawing
        hand_landmarks_proto = landmark_pb2.NormalizedLandmarkList()
        hand_landmarks_proto.landmark.extend([
            landmark_pb2.NormalizedLandmark(x=lm.x, y=lm.y, z=lm.z)
            for lm in hand_landmarks
        ])

        # Draw connections and landmarks
        solutions.drawing_utils.draw_landmarks(
            frame,
            hand_landmarks_proto,
            solutions.hands.HAND_CONNECTIONS,
            solutions.drawing_styles.get_default_hand_landmarks_style(),
            solutions.drawing_styles.get_default_hand_connections_style()
        )

        # Label: Left / Right hand
        height, width, _ = frame.shape
        x = int(hand_landmarks[0].x * width)
        y = int(hand_landmarks[0].y * height) - 20
        label = handedness[0].display_name
        cv2.putText(frame, label, (x, y),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

    return frame


# --- MediaPipe setup ---
base_options = python.BaseOptions(model_asset_path='hand_landmarker.task')
options = vision.HandLandmarkerOptions(
    base_options=base_options,
    num_hands=2,
    running_mode=vision.RunningMode.VIDEO   # VIDEO mode for live frame-by-frame detection
)
detector = vision.HandLandmarker.create_from_options(options)

# --- OpenCV webcam ---
cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("Error: Could not open webcam.")
    exit()

print("Hand Detection Running — Press Q to quit")

frame_timestamp_ms = 0

while True:
    ret, frame = cap.read()
    if not ret:
        print("Failed to grab frame.")
        break

    frame = cv2.flip(frame, 1)  # Mirror for natural feel

    # Convert BGR (OpenCV) to RGB (MediaPipe)
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)

    # Detect — VIDEO mode requires a monotonically increasing timestamp
    frame_timestamp_ms += 1
    detection_result = detector.detect_for_video(mp_image, frame_timestamp_ms)

    # Draw landmarks on the original BGR frame
    annotated_frame = draw_landmarks_on_frame(frame, detection_result)

    # Show hand count
    hand_count = len(detection_result.hand_landmarks)
    cv2.putText(annotated_frame, f"Hands detected: {hand_count}", (10, 40),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 0), 2)

    cv2.imshow("Hand Detection", annotated_frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# --- Cleanup ---
cap.release()
cv2.destroyAllWindows()
detector.close()