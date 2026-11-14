from djitellopySim import Tello
import time
import cv2

drone = Tello()
drone.connect()
time.sleep(1)
drone.streamon()
drone.takeoff()
frame_reader = drone.get_frame_read()

while True:
    frame = frame_reader.frame

    if frame is not None:
        cv2.imshow("Drone Feed", frame)
    cv2.waitKey(1)

drone.land()
drone.end()
time.sleep(1)
