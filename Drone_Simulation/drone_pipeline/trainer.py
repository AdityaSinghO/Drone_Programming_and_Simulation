import cv2
import numpy as np
import os


class TacticalTrainer:
    def __init__(self, dataset_path="enemy_data"):
        self.dataset_path = dataset_path
        self.face_recognizer = cv2.face.LBPHFaceRecognizer_create()

    def train(self):
        """
        Processes images in 'enemy_data/faces' and 'enemy_data/uniforms'
        to build a recognition profile.
        """
        faces, labels = [], []
        face_dir = os.path.join(self.dataset_path, "faces")

        if not os.path.exists(face_dir):
            print("Error: Dataset directory not found.")
            return

        for idx, filename in enumerate(os.listdir(face_dir)):
            path = os.path.join(face_dir, filename)
            img = cv2.imread(path, cv2.IMREAD_GRAYSCALE)
            if img is not None:
                # Resize to standard dimensions for LBPH
                img = cv2.resize(img, (100, 100))
                faces.append(img)
                labels.append(1)  # Label 1 for ENEMY

        if faces:
            self.face_recognizer.train(faces, np.array(labels))
            self.face_recognizer.save("enemy_model.xml")
            print("Model successfully trained on enemy dataset.")


if __name__ == "__main__":
    trainer = TacticalTrainer()
    trainer.train()