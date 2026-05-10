from pysimverse import Drone
import time

drone = Drone()
drone.connect()
drone.take_off(100, 200)

drone.rotate(-35)
drone.set_speed(200)
drone.move_forward(400)
drone.land(200)

drone.take_off(50, 100)
drone.rotate(150)
drone.move_forward(470)
drone.land()

drone.land()
time.sleep(1)