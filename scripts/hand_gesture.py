import cv2
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
 
# --- Drawing utility (manual, no solutions dependency) ---
HAND_CONNECTIONS = [
    (0,1),(1,2),(2,3),(3,4),           # Thumb
    (0,5),(5,6),(6,7),(7,8),           # Index
    (0,9),(9,10),(10,11),(11,12),      # Middle
    (0,13),(13,14),(14,15),(15,16),    # Ring
    (0,17),(17,18),(18,19),(19,20),    # Pinky
    (5,9),(9,13),(13,17)               # Palm
]
 
def draw_landmarks_on_frame(frame, detection_result):
    height, width, _ = frame.shape
    hand_landmarks_list = detection_result.hand_landmarks
    handedness_list = detection_result.handedness
 
    for idx in range(len(hand_landmarks_list)):
        landmarks = hand_landmarks_list[idx]
        handedness = handedness_list[idx]
 
        # Convert normalized coords to pixel coords
        points = [
            (int(lm.x * width), int(lm.y * height))
            for lm in landmarks
        ]
 
        # Draw connections
        for start, end in HAND_CONNECTIONS:
            cv2.line(frame, points[start], points[end], (0, 200, 255), 2)
 
        # Draw landmark dots
        for point in points:
            cv2.circle(frame, point, 5, (255, 255, 255), -1)
            cv2.circle(frame, point, 5, (0, 150, 255), 1)
 
        # Label Left / Right above wrist
        label = handedness[0].display_name
        cv2.putText(frame, label, (points[0][0], points[0][1] - 20),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
 
    return frame
 
 
# --- MediaPipe setup ---
base_options = python.BaseOptions(model_asset_path=r"C:\Downloads\Programming\Projects\Drone_Simulation\models\hand_landmarker.task")
options = vision.HandLandmarkerOptions(
    base_options=base_options,
    num_hands=2,
    running_mode=vision.RunningMode.VIDEO
)
detector = vision.HandLandmarker.create_from_options(options)
 
# --- OpenCV webcam ---
cap = cv2.VideoCapture(1)
 
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
 
    # Convert BGR to RGB for MediaPipe
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)
 
    # Detect
    frame_timestamp_ms += 1
    detection_result = detector.detect_for_video(mp_image, frame_timestamp_ms)
 
    # Draw
    annotated_frame = draw_landmarks_on_frame(frame, detection_result)
 
    # Hand count overlay
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