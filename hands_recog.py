import cv2
import mediapipe as mp
import numpy as np
import warnings

# Suppress specific deprecation warning
warnings.filterwarnings("ignore", message="SymbolDatabase.GetPrototype() is deprecated")

class HandWireframe:
    def __init__(self):
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(min_detection_confidence=0.7, min_tracking_confidence=0.7)
        self.mp_drawing = mp.solutions.drawing_utils

    def draw_hand_wireframe(self, frame):
        # Convert the frame to RGB for MediaPipe
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.hands.process(rgb_frame)

        if results.multi_hand_landmarks:
            for landmarks in results.multi_hand_landmarks:
                # Draw hand landmarks
                self.mp_drawing.draw_landmarks(frame, landmarks, self.mp_hands.HAND_CONNECTIONS)

                # Check for peace sign (two fingers extended)
                if self.is_peace_sign(landmarks):
                    print("Peace sign detected")  # For debugging
                    return True

        return False

    def is_peace_sign(self, landmarks):
        # Get coordinates of finger tips and joints
        index_tip = np.array([landmarks.landmark[8].x, landmarks.landmark[8].y])
        index_joint = np.array([landmarks.landmark[6].x, landmarks.landmark[6].y])
        middle_tip = np.array([landmarks.landmark[12].x, landmarks.landmark[12].y])
        middle_joint = np.array([landmarks.landmark[10].x, landmarks.landmark[10].y])
        thumb_tip = np.array([landmarks.landmark[4].x, landmarks.landmark[4].y])
        ring_tip = np.array([landmarks.landmark[16].x, landmarks.landmark[16].y])
        pinky_tip = np.array([landmarks.landmark[20].x, landmarks.landmark[20].y])

        # Calculate distances
        index_distance = np.linalg.norm(index_tip - index_joint)
        middle_distance = np.linalg.norm(middle_tip - middle_joint)
        thumb_distance = np.linalg.norm(thumb_tip - index_tip)
        ring_distance = np.linalg.norm(ring_tip - index_tip)
        pinky_distance = np.linalg.norm(pinky_tip - index_tip)

        # Define thresholds
        finger_threshold = 0.05
        thumb_ring_pinky_threshold = 0.15

        # Check if index and middle fingers are extended
        index_extended = index_distance > finger_threshold
        middle_extended = middle_distance > finger_threshold

        # Check if thumb, ring, and pinky are retracted
        thumb_retracted = thumb_distance > thumb_ring_pinky_threshold
        ring_retracted = ring_distance > thumb_ring_pinky_threshold
        pinky_retracted = pinky_distance > thumb_ring_pinky_threshold

        # Ensure only index and middle fingers are extended
        return index_extended and middle_extended and thumb_retracted and ring_retracted and pinky_retracted

def main():
    hand_wireframe = HandWireframe()
    cap = cv2.VideoCapture(0)

    while True:
        ret, frame = cap.read()

        if not ret or frame is None:
            print("Failed to capture frame from camera. Exiting...")
            break

        # Process the hand wireframe drawing and gesture detection
        peace_sign_detected = hand_wireframe.draw_hand_wireframe(frame)

        # Display the frame
        cv2.imshow("Hand Wireframe", frame)

        # Exit on 'q' key press
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
