import cv2
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
from pysimverse import Drone
import time
import math

# Connections
HAND_CONNECTIONS = [
    (0,1),(1,2),(2,3),(3,4),
    (0,5),(5,6),(6,7),(7,8),
    (0,9),(9,10),(10,11),(11,12),
    (0,13),(13,14),(14,15),(15,16),
    (0,17),(17,18),(18,19),(19,20),
    (5,9),(9,13),(13,17)
]

#
# CONTROL TUNING
#
DEADZONE_XY    = 0.06   
MAX_RANGE_XY   = 0.25   
ANCHOR_SPAN_MARGIN = 0.06  
MAX_SPAN_DELTA     = 0.15  
ROT_DEADZONE  = 15   
ROT_MAX_RANGE = 45   
MAX_RC    = 100
MIN_RC    = -100
SPEED     = 50
YAW_SPEED = 30
FIST_THRESHOLD   = 0.12   
FIST_HOLD_FRAMES = 20     
ANCHOR_RESET_FRAMES = 10

# Colors
C_GREEN   = (60,  220,  60)
C_ORANGE  = (30,  160, 255)
C_RED     = (60,   60, 255)
C_WHITE   = (220, 220, 220)
C_GREY    = (100, 100, 100)
C_DARK    = (20,   20,  20)
C_CYAN    = (255, 200,   0)

#
# HELPERS
#
def get_hand_span(lms):
    return math.dist((lms[0].x, lms[0].y), (lms[12].x, lms[12].y))

def get_hand_angle(lms):
    dx = lms[5].x - lms[0].x
    dy = lms[5].y - lms[0].y
    return math.degrees(math.atan2(-dy, dx))

def is_fist(lms):
    tips = [4, 8, 12, 16, 20]
    avg_dist = sum(math.dist((lms[t].x, lms[t].y),
                             (lms[0].x, lms[0].y)) for t in tips) / len(tips)
    return avg_dist < FIST_THRESHOLD

def proportional(value, deadzone, max_range, speed):
    abs_v = abs(value)
    if abs_v < deadzone:
        return 0
    ratio = min((abs_v - deadzone) / (max_range - deadzone), 1.0)
    return int(math.copysign(ratio * speed, value))

# 
# DRAWING
# 
def draw_anchor_ui(frame, anchor, wrist, h, w):
    if anchor is None: return
    ax, ay = int(anchor[0] * w), int(anchor[1] * h)
    wx, wy = int(wrist[0]   * w), int(wrist[1]   * h)
    dz_r, max_r = int(DEADZONE_XY * w), int(MAX_RANGE_XY * w)
    cv2.circle(frame, (ax, ay), dz_r,  C_GREY,  1)
    cv2.circle(frame, (ax, ay), max_r, C_ORANGE, 1)
    cv2.line(frame, (ax, ay), (wx, wy), C_CYAN, 2)
    cv2.circle(frame, (ax, ay), 8, C_WHITE, -1)

def draw_landmarks(frame, detection_result):
    h, w, _ = frame.shape
    for lms in detection_result.hand_landmarks:
        points = [(int(l.x * w), int(l.y * h)) for l in lms]
        for s, e in HAND_CONNECTIONS:
            cv2.line(frame, points[s], points[e], (0, 200, 255), 2)
        for p in points:
            cv2.circle(frame, p, 4, C_WHITE, -1)
        cv2.line(frame, points[0], points[5], C_CYAN, 2)

def draw_rotation_dial(frame, angle, anchor_angle, yaw):
    h, w, _ = frame.shape
    cx, cy, r = w - 55, 55, 38
    cv2.circle(frame, (cx, cy), r, (40, 40, 40), -1)
    for deg in range(-ROT_DEADZONE, ROT_DEADZONE):
        a = math.radians(-(anchor_angle + deg - 90))
        ex, ey = int(cx + (r-4) * math.cos(a)), int(cy + (r-4) * math.sin(a))
        cv2.circle(frame, (ex, ey), 1, C_GREEN, -1)
    needle_rad = math.radians(-(angle - 90))
    ex, ey = int(cx + r * math.cos(needle_rad)), int(cy + r * math.sin(needle_rad))
    color = C_RED if yaw != 0 else C_WHITE
    cv2.line(frame, (cx, cy), (ex, ey), color, 3)

def draw_status_bar(frame, lr, fb, ud, yaw, fist_frames, hand_detected):
    h, w, _ = frame.shape
    cv2.rectangle(frame, (0, h - 65), (w, h), C_DARK, -1)
    if not hand_detected:
        cv2.putText(frame, "NO HAND — HOVERING", (w//2 - 100, h - 22), cv2.FONT_HERSHEY_SIMPLEX, 0.7, C_GREY, 2)
        return
    cmds = [f"LR:{lr:+d}", f"FB:{fb:+d}", f"UD:{ud:+d}", f"YAW:{yaw:+d}"]
    cv2.putText(frame, " | ".join(cmds), (10, h - 12), cv2.FONT_HERSHEY_SIMPLEX, 0.65, C_GREEN, 2)

#
# MAIN LOOP
#
drone = Drone()
drone.connect()
time.sleep(1)
drone.take_off()

base_options = python.BaseOptions(model_asset_path='C:\\Downloads\\Programming\\Projects\\Drone_Simulation\\models\\hand_landmarker.task')
options = vision.HandLandmarkerOptions(base_options=base_options, num_hands=1, running_mode=vision.RunningMode.VIDEO)
detector = vision.HandLandmarker.create_from_options(options)

cap = cv2.VideoCapture(1)
anchor_xy = anchor_span = anchor_angle = None
no_hand_ctr = fist_ctr = frame_ts = 0

while True:
    ret, frame = cap.read()
    if not ret: break
    frame = cv2.flip(frame, 1)
    h, w, _ = frame.shape
    mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
    frame_ts += 1
    result = detector.detect_for_video(mp_image, frame_ts)

    lr = fb = ud = yaw = 0

    if result.hand_landmarks:
        no_hand_ctr = 0
        lms = result.hand_landmarks[0]
        wx, wy, span, angle = lms[0].x, lms[0].y, get_hand_span(lms), get_hand_angle(lms)

        if anchor_xy is None:
            anchor_xy, anchor_span, anchor_angle = (wx, wy), span, angle

        if is_fist(lms):
            fist_ctr += 1
            if fist_ctr >= FIST_HOLD_FRAMES:
                print("\nLanding...")
                break
        elif anchor_xy is not None:  # FIX: Guard against NoneType subtraction
            lr = proportional(wx - anchor_xy[0], DEADZONE_XY, MAX_RANGE_XY, SPEED)
            ud = proportional(-(wy - anchor_xy[1]), DEADZONE_XY, MAX_RANGE_XY, SPEED)
            fb = proportional(span - anchor_span, ANCHOR_SPAN_MARGIN, MAX_SPAN_DELTA, SPEED)
            
            angle_delta = angle - anchor_angle
            if angle_delta > 180: angle_delta -= 360
            if angle_delta < -180: angle_delta += 360
            yaw = proportional(-angle_delta, ROT_DEADZONE, ROT_DEADZONE + ROT_MAX_RANGE, YAW_SPEED)

        drone.send_rc_control(lr, fb, ud, yaw)
        draw_landmarks(frame, result)
        draw_anchor_ui(frame, anchor_xy, (wx, wy), h, w)
        draw_rotation_dial(frame, angle, anchor_angle or angle, yaw)
        draw_status_bar(frame, lr, fb, ud, yaw, fist_ctr, True)
    else:
        no_hand_ctr += 1
        drone.send_rc_control(0, 0, 0, 0)
        if no_hand_ctr >= ANCHOR_RESET_FRAMES:
            anchor_xy = anchor_span = anchor_angle = None
        draw_status_bar(frame, 0, 0, 0, 0, 0, False)

    cv2.imshow("Hand Drone Control", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'): break

cap.release()
cv2.destroyAllWindows()
drone.land()