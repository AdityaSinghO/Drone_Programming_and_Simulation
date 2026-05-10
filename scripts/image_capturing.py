from pysimverse import Drone
import keyboard
import cv2
import time
import os
from datetime import datetime

# --- Setup ---
SCREENSHOTS_DIR = "drone_screenshots"
os.makedirs(SCREENSHOTS_DIR, exist_ok=True)

drone = Drone()
drone.connect()
time.sleep(1)
drone.streamon()
drone.take_off()
time.sleep(1)

MAX_RC = 100
MIN_RC = -100
SPEED = 50
YAW_SPEED = 5

screenshot_taken = False  # Debounce flag for Z key

print("Drone Keyboard Controls:")
print("  W / S            -> Forward / Backward")
print("  A / D            -> Left / Right")
print("  Up / Down arrows -> Ascend / Descend")
print("  Left / Right arrows -> Rotate (Yaw)")
print("  Z                -> Screenshot")
print("  Q                -> Quit and Land")
print(f"\nScreenshots will be saved to: '{SCREENSHOTS_DIR}/'")

while True:
    # --- Video Feed ---
    frame, is_success = drone.get_frame()

    if is_success and frame is not None:

        # --- Screenshot ---
        if keyboard.is_pressed('z'):
            if not screenshot_taken:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = os.path.join(SCREENSHOTS_DIR, f"snapshot_{timestamp}.png")
                cv2.imwrite(filename, frame)
                print(f"Screenshot saved: {filename}")
                screenshot_taken = True
        else:
            screenshot_taken = False  # Reset debounce when key released

        # Overlay screenshot feedback on frame
        display_frame = frame.copy()
        if screenshot_taken:
            cv2.putText(display_frame, "SNAPSHOT SAVED!", (10, 40),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

        cv2.imshow("Drone Feed", display_frame)

    cv2.waitKey(1)

    # --- Keyboard RC Control ---
    left_right       = 0
    forward_backward = 0
    up_down          = 0
    yaw              = 0

    if keyboard.is_pressed('w'):
        forward_backward = SPEED
    elif keyboard.is_pressed('s'):
        forward_backward = -SPEED

    if keyboard.is_pressed('a'):
        left_right = -SPEED
    elif keyboard.is_pressed('d'):
        left_right = SPEED

    if keyboard.is_pressed('up'):
        up_down = SPEED
    elif keyboard.is_pressed('down'):
        up_down = -SPEED

    if keyboard.is_pressed('left'):
        yaw = -YAW_SPEED
    elif keyboard.is_pressed('right'):
        yaw = YAW_SPEED

    if keyboard.is_pressed('q'):
        print("Landing...")
        break

    drone.send_rc_control(
        max(MIN_RC, min(MAX_RC, left_right)),
        max(MIN_RC, min(MAX_RC, forward_backward)),
        max(MIN_RC, min(MAX_RC, up_down)),
        max(MIN_RC, min(MAX_RC, yaw))
    )

    time.sleep(0.05)  # ~20Hz control loop

# --- Cleanup ---
cv2.destroyAllWindows()
drone.land()
time.sleep(1)