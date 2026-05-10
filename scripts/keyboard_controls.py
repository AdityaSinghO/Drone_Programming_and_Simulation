from pysimverse import Drone
import keyboard
import time

drone = Drone()
drone.connect()
drone.take_off()
time.sleep(1)


MAX_RC = 100
MIN_RC = -100
SPEED = 50
YAW_SPEED = 20

print("Drone Keyboard Controls:")
print("  W / S       -> Forward / Backward")
print("  A / D       -> Left / Right")
print("  Up / Down   -> Ascend / Descend")
print("  Left / Right arrows -> Rotate (Yaw)")
print("  Q           -> Quit and Land")

while True:
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
        break

    drone.send_rc_control(left_right, forward_backward, up_down, yaw)
    time.sleep(0.05)  # ~20Hz control loop

drone.land()
time.sleep(1)