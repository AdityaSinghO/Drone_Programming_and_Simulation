from pysimverse import Drone
import time

drone = Drone()
drone.connect()
drone.take_off()

drone.rotate(50)
drone.set_speed(200)
drone.move_forward(350)

drone.land()
time.sleep(1)