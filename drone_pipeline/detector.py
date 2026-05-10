import cv2
import numpy as np


class CombatDetector:
    def __init__(self, model_path):
        # Load YOLO/SSD (example using OpenCV DNN)
        self.net = cv2.dnn.readNet(model_path + ".weights", model_path + ".cfg")
        self.layer_names = self.net.getLayerNames()
        self.output_layers = [self.layer_names[i - 1] for i in self.net.getUnconnectedOutLayers()]

    def classify_team(self, frame, box):
        x, y, w, h = box
        # Extract the torso area (center of the bounding box)
        roi = frame[y + h // 4: y + h // 2, x + w // 4: x + 3 * w // 4]
        if roi.size == 0: return "UNKNOWN"

        hsv = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)

        # Define Color Ranges
        red_lower = np.array([0, 100, 100]);
        red_upper = np.array([10, 255, 255])
        green_lower = np.array([35, 100, 100]);
        green_upper = np.array([85, 255, 255])

        red_mask = cv2.inRange(hsv, red_lower, red_upper)
        green_mask = cv2.inRange(hsv, green_lower, green_upper)

        if np.sum(red_mask) > np.sum(green_mask):
            return "ENEMY"
        elif np.sum(green_mask) > np.sum(red_mask):
            return "ALLY"
        return "NEUTRAL"