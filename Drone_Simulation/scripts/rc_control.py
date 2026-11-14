from djitellopySim import Tello
import time

drone = Tello()
drone.connect()
drone.takeoff()

left_right = 0
forward_backward = 50
up_down = 0
yaw = 0

while True:
    drone.send_rc_control(left_right, forward_backward, up_down, yaw)

drone.land()
drone.end()
time.sleep(1)