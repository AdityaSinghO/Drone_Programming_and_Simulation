from pysimverse import Drone
import time

drone = Drone()
drone.connect()
drone.take_off(100, 100)

drone.rotate(-80)
drone.set_speed(200)
drone.move_forward(240)
drone.land(200)

drone.take_off(100, 100)
drone.rotate(140)
drone.move_forward(270)
drone.land(200)

drone.take_off(100, 100)
drone.rotate(15)
drone.move_forward(270)

drone.land(200)
time.sleep(1)