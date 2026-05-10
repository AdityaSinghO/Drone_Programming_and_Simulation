import cv2
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
from pysimverse import Drone
import time

# --- Pose Connections (MediaPipe Pose Topology) ---
# This list defines the lines drawn between body joints
POSE_CONNECTIONS = mp.solutions.pose.POSE_CONNECTIONS

# --- Zone boundaries (normalized 0.0 - 1.0) ---
LEFT_ZONE = 0.33
RIGHT_ZONE = 0.66

# --- RC speeds ---
MAX_RC = 100
MIN_RC = -100
SPEED = 50

ZONE_COLORS = {
    "LEFT": (50, 50, 180),
    "DEADZONE": (50, 120, 50),
    "RIGHT": (180, 50, 50),
}
ZONE_ACTIVE_COLORS = {
    "LEFT": (60, 60, 255),
    "DEADZONE": (60, 220, 60),
    "RIGHT": (255, 80, 60),
}
ZONE_ALPHA = 0.25


def get_zone(norm_x):
    if norm_x < LEFT_ZONE:
        return "LEFT"
    elif norm_x > RIGHT_ZONE:
        return "RIGHT"
    else:
        return "DEADZONE"


def draw_zones(frame, active_zone):
    h, w, _ = frame.shape
    overlay = frame.copy()
    zones = [
        ("LEFT", 0, int(w * LEFT_ZONE)),
        ("DEADZONE", int(w * LEFT_ZONE), int(w * RIGHT_ZONE)),
        ("RIGHT", int(w * RIGHT_ZONE), w),
    ]
    for name, x1, x2 in zones:
        color = ZONE_ACTIVE_COLORS[name] if name == active_zone else ZONE_COLORS[name]
        cv2.rectangle(overlay, (x1, 0), (x2, h), color, -1)
    cv2.addWeighted(overlay, ZONE_ALPHA, frame, 1 - ZONE_ALPHA, 0, frame)
    cv2.line(frame, (int(w * LEFT_ZONE), 0), (int(w * LEFT_ZONE), h), (255, 255, 255), 1)
    cv2.line(frame, (int(w * RIGHT_ZONE), 0), (int(w * RIGHT_ZONE), h), (255, 255, 255), 1)


def draw_pose_landmarks(frame, detection_result):
    h, w, _ = frame.shape
    center_x = None

    if not detection_result.pose_landmarks:
        return None

    for landmarks in detection_result.pose_landmarks:
        points = [(int(lm.x * w), int(lm.y * h)) for lm in landmarks]

        # We'll use the midpoint between shoulders (landmarks 11 and 12)
        # to track the body center
        center_x = (landmarks[11].x + landmarks[12].x) / 2

        # Draw skeleton connections
        for connection in POSE_CONNECTIONS:
            start_idx, end_idx = connection
            cv2.line(frame, points[start_idx], points[end_idx], (0, 200, 255), 2)

        # Draw joints
        for point in points:
            cv2.circle(frame, point, 4, (255, 255, 255), -1)
            cv2.circle(frame, point, 4, (0, 150, 255), 1)

    return center_x


# --- Drone setup ---
drone = Drone()
drone.connect()
time.sleep(1)
drone.take_off()
time.sleep(1)

# --- MediaPipe Pose setup ---
# NOTE: Ensure you have the pose_landmarker.task file at this path
base_options = python.BaseOptions(model_asset_path="pose_landmarker.task")
options = vision.PoseLandmarkerOptions(
    base_options=base_options,
    running_mode=vision.RunningMode.VIDEO
)
detector = vision.PoseLandmarker.create_from_options(options)

# --- Webcam ---
cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("Error: Could not open webcam.")
    drone.land()
    exit()

print("Body Tracking Drone Control Running — Press Q to quit and land")

frame_timestamp_ms = 0
current_zone = "DEADZONE"

while True:
    ret, frame = cap.read()
    if not ret:
        break

    frame = cv2.flip(frame, 1)
    h, w, _ = frame.shape

    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)

    frame_timestamp_ms = int(time.time() * 1000)
    detection_result = detector.detect_for_video(mp_image, frame_timestamp_ms)

    # --- Determine zone based on body center ---
    body_x = draw_pose_landmarks(frame, detection_result)
    if body_x is not None:
        current_zone = get_zone(body_x)
    else:
        current_zone = "DEADZONE"

    # --- Map zone to RC controls ---
    left_right = 0
    if current_zone == "LEFT":
        left_right = -SPEED
    elif current_zone == "RIGHT":
        left_right = SPEED

    drone.send_rc_control(left_right, 0, 0, 0)

    # --- Draw UI ---
    draw_zones(frame, current_zone)

    # Status bar
    bar_color = ZONE_ACTIVE_COLORS[current_zone]
    cv2.rectangle(frame, (0, h - 60), (w, h), (20, 20, 20), -1)
    status = f"BODY ZONE: {current_zone} | CMD: {'MOVE LEFT' if current_zone == 'LEFT' else 'MOVE RIGHT' if current_zone == 'RIGHT' else 'HOVER'}"
    cv2.putText(frame, status, (20, h - 20), cv2.FONT_HERSHEY_SIMPLEX, 0.7, bar_color, 2)

    cv2.imshow("Body Drone Control", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# --- Cleanup ---
cap.release()
cv2.destroyAllWindows()
detector.close()
drone.land()