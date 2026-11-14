from djitellopySim import Tello
import time

drone = Tello()
drone.connect()
drone.takeoff()

drone.move_down(20)
time.sleep(1)
drone.move_up(30)
time.sleep(1)

drone.move_left(20)
time.sleep(1)
drone.move_right(30)
time.sleep(1)

drone.set_speed(50)
drone.move_forward(20)
time.sleep(1)
drone.move_back(30)
time.sleep(1)

drone.rotate_clockwise(30)

drone.land()
drone.end()
time.sleep(1)
