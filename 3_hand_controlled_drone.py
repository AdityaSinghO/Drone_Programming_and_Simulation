import cv2
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
from pysimverse import Drone
import time

# --- Hand Connections ---
HAND_CONNECTIONS = [
    (0,1),(1,2),(2,3),(3,4),
    (0,5),(5,6),(6,7),(7,8),
    (0,9),(9,10),(10,11),(11,12),
    (0,13),(13,14),(14,15),(15,16),
    (0,17),(17,18),(18,19),(19,20),
    (5,9),(9,13),(13,17)
]

# --- Zone boundaries (normalized 0.0 - 1.0) ---
LEFT_ZONE  = 0.33
RIGHT_ZONE = 0.66

# --- RC speeds ---
MAX_RC    = 100
MIN_RC    = -100
SPEED     = 50
YAW_SPEED = 20

ZONE_COLORS = {
    "LEFT":     (50,  50, 180),
    "DEADZONE": (50, 120,  50),
    "RIGHT":    (180, 50,  50),
}
ZONE_ACTIVE_COLORS = {
    "LEFT":     (60,  60, 255),
    "DEADZONE": (60, 220,  60),
    "RIGHT":    (255, 80,  60),
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
        ("LEFT",     0,               int(w * LEFT_ZONE)),
        ("DEADZONE", int(w * LEFT_ZONE),  int(w * RIGHT_ZONE)),
        ("RIGHT",    int(w * RIGHT_ZONE), w),
    ]
    for name, x1, x2 in zones:
        color = ZONE_ACTIVE_COLORS[name] if name == active_zone else ZONE_COLORS[name]
        cv2.rectangle(overlay, (x1, 0), (x2, h), color, -1)
    cv2.addWeighted(overlay, ZONE_ALPHA, frame, 1 - ZONE_ALPHA, 0, frame)
    cv2.line(frame, (int(w * LEFT_ZONE), 0),  (int(w * LEFT_ZONE), h),  (255,255,255), 1)
    cv2.line(frame, (int(w * RIGHT_ZONE), 0), (int(w * RIGHT_ZONE), h), (255,255,255), 1)
    for name, x1, x2 in zones:
        cx = (x1 + x2) // 2
        color = ZONE_ACTIVE_COLORS[name] if name == active_zone else (180, 180, 180)
        text_size = cv2.getTextSize(name, cv2.FONT_HERSHEY_SIMPLEX, 0.7, 2)[0]
        cv2.putText(frame, name, (cx - text_size[0]//2, 35),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)

def draw_landmarks(frame, detection_result):
    h, w, _ = frame.shape
    wrist_x_list = []
    for idx in range(len(detection_result.hand_landmarks)):
        landmarks  = detection_result.hand_landmarks[idx]
        handedness = detection_result.handedness[idx]
        points = [(int(lm.x * w), int(lm.y * h)) for lm in landmarks]
        wrist_x_list.append(landmarks[0].x)
        for start, end in HAND_CONNECTIONS:
            cv2.line(frame, points[start], points[end], (0, 200, 255), 2)
        for point in points:
            cv2.circle(frame, point, 5, (255, 255, 255), -1)
            cv2.circle(frame, point, 5, (0, 150, 255),   1)
        label = handedness[0].display_name
        cv2.putText(frame, label, (points[0][0], points[0][1] - 20),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
    return wrist_x_list

# --- Drone setup ---
drone = Drone()
drone.connect()
time.sleep(1)
drone.take_off()
time.sleep(1)

# --- MediaPipe setup ---
base_options = python.BaseOptions(model_asset_path="C:\\Downloads\\Programming\\Projects\\Drone_Simulation\\models\\hand_landmarker.task")
options = vision.HandLandmarkerOptions(
    base_options=base_options,
    num_hands=2,
    running_mode=vision.RunningMode.VIDEO
)
detector = vision.HandLandmarker.create_from_options(options)

# --- Webcam ---
cap = cv2.VideoCapture(1)  # Change index if needed
if not cap.isOpened():
    print("Error: Could not open webcam.")
    drone.land()
    exit()

print("Hand Drone Control Running — Press Q to quit and land")

frame_timestamp_ms = 0
current_zone = "DEADZONE"

while True:
    ret, frame = cap.read()
    if not ret:
        break

    frame = cv2.flip(frame, 1)
    h, w, _ = frame.shape

    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    mp_image  = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)

    frame_timestamp_ms += 1
    detection_result = detector.detect_for_video(mp_image, frame_timestamp_ms)

    # --- Determine zone ---
    wrist_xs = draw_landmarks(frame, detection_result)
    if wrist_xs:
        avg_x = sum(wrist_xs) / len(wrist_xs)
        current_zone = get_zone(avg_x)
    else:
        current_zone = "DEADZONE"

    # --- Map zone to RC controls ---
    left_right       = 0
    forward_backward = 0
    up_down          = 0
    yaw              = 0

    if current_zone == "LEFT":
        left_right = -SPEED          # Rotate left
    elif current_zone == "RIGHT":
        left_right = SPEED           # Rotate right
    # DEADZONE: all values stay 0 — drone hovers

    drone.send_rc_control(
        max(MIN_RC, min(MAX_RC, left_right)),
        max(MIN_RC, min(MAX_RC, forward_backward)),
        max(MIN_RC, min(MAX_RC, up_down)),
        max(MIN_RC, min(MAX_RC, yaw))
    )

    # --- Draw UI ---
    draw_zones(frame, current_zone)
    draw_landmarks(frame, detection_result)

    # Status bar
    bar_color = ZONE_ACTIVE_COLORS[current_zone]
    cv2.rectangle(frame, (0, h - 60), (w, h), (20, 20, 20), -1)
    status = f"ZONE: {current_zone}  |  CMD: {'YAW LEFT' if current_zone == 'LEFT' else 'YAW RIGHT' if current_zone == 'RIGHT' else 'HOVER'}"
    text_size = cv2.getTextSize(status, cv2.FONT_HERSHEY_SIMPLEX, 0.8, 2)[0]
    cv2.putText(frame, status, ((w - text_size[0]) // 2, h - 15),
                cv2.FONT_HERSHEY_SIMPLEX, 0.8, bar_color, 2)

    print(f"\rZone: {current_zone:<10} | Yaw: {yaw:>4}", end="", flush=True)

    cv2.imshow("Hand Drone Control", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        print("\nLanding...")
        break

# --- Cleanup ---
cap.release()
cv2.destroyAllWindows()
detector.close()
drone.land()
time.sleep(1)