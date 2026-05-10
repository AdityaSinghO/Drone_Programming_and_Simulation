from pysimverse import Drone
import time

drone = Drone()
drone.connect()
drone.take_off()

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
drone.move_backward(30)
time.sleep(1)

drone.rotate(30) # positive int for clock-wise rotation, negative int for anti - clockwise rotation

drone.land()
time.sleep(1)