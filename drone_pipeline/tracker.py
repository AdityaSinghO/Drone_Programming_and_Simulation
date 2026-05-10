import cv2

class DualTracker:
    def __init__(self):
        self.kcf_tracker = cv2.TrackerKCF_create()
        self.initialized = False

    def get_optical_flow(self, prev_gray, curr_gray, prev_pts):
        # Lucas-Kanade Optical Flow to track movement vectors
        next_pts, status, err = cv2.calcOpticalFlowPyrLK(prev_gray, curr_gray, prev_pts, None)
        return next_pts, status

    def init_kcf(self, frame, box):
        self.kcf_tracker.init(frame, box)
        self.initialized = True

    def update_kcf(self, frame):
        success, box = self.kcf_tracker.update(frame)
        return success, box