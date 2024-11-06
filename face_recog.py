import cv2
import dlib
import numpy as np
from deepface import DeepFace
from scipy.spatial import distance as dist
from hands_recog import HandWireframe
import warnings
import tkinter as tk
from PIL import Image, ImageTk
from threading import Thread, Event
import os
from dotenv import load_dotenv

# Suppress specific deprecation warning
warnings.filterwarnings("ignore", message="SymbolDatabase.GetPrototype() is deprecated")

load_dotenv()

# Initialize dlib's face detector and shape predictor
detector = dlib.get_frontal_face_detector()
predictor = dlib.shape_predictor('shape_predictor_68_face_landmarks.dat')

# Load and preprocess reference images for face recognition
reference_images = os.getenv("REFERENCE_IMAGES").split(',')
output_images = []
target_height = 480

for ref_img_path in reference_images:
    reference_img = cv2.imread(ref_img_path)
    aspect_ratio = reference_img.shape[1] / reference_img.shape[0]
    new_width = int(target_height * aspect_ratio)
    reference_img_resized = cv2.resize(reference_img, (new_width, target_height))
    output_images.append(reference_img_resized)


def get_eye_aspect_ratio(eye):
    A = dist.euclidean(eye[1], eye[5])
    B = dist.euclidean(eye[2], eye[4])
    C = dist.euclidean(eye[0], eye[3])
    return (A + B) / (2.0 * C)


def detect_face_and_blink(frame, blink_counter, blink_detected):
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    rects = detector(gray, 0)

    for rect in rects:
        shape = predictor(gray, rect)
        shape = np.array([[p.x, p.y] for p in shape.parts()])

        left_eye = shape[36:42]
        right_eye = shape[42:48]

        ear_left = get_eye_aspect_ratio(left_eye)
        ear_right = get_eye_aspect_ratio(right_eye)
        ear = (ear_left + ear_right) / 2.0

        EAR_THRESHOLD = 0.2
        if ear < EAR_THRESHOLD:
            if not blink_detected:
                blink_counter += 1
                blink_detected = True
                print(blink_counter)
        else:
            blink_detected = False

    return blink_counter, blink_detected


def fail_safe_unlock(window, stop_event):
    # Create a small pop-up window for the password
    unlock_window = tk.Toplevel(window)
    unlock_window.title("Fail-safe Unlock")

    label = tk.Label(unlock_window, text="Enter password to unlock:", font=("Helvetica", 16))
    label.pack(pady=10)

    password_entry = tk.Entry(unlock_window, show="*", font=("Helvetica", 14))
    password_entry.pack(pady=10)

    def check_password():
        password = password_entry.get()
        if password == "1234":  # Replace with a more secure password or logic
            stop_event.set()  # Signal to stop the camera and lock screen
            unlock_window.destroy()  # Close unlock window
            window.quit()  # Exit the Tkinter main loop and unlock
        else:
            label.config(text="Incorrect password, try again.")

    submit_button = tk.Button(unlock_window, text="Submit", command=check_password, font=("Helvetica", 14))
    submit_button.pack(pady=10)

    # Close the unlock window and resume lock screen on escape
    unlock_window.bind('<Escape>', lambda event: unlock_window.destroy())
    unlock_window.mainloop()


def show_afk_window(stop_event, image_path):
    afk_window = tk.Tk()
    afk_window.attributes('-fullscreen', True)  # Make the window fullscreen
    afk_window.title("Lock Screen")

    # Load the image and display it
    img = Image.open(image_path)
    screen_width = afk_window.winfo_screenwidth()
    screen_height = afk_window.winfo_screenheight()
    img = img.resize((screen_width, screen_height), Image.Resampling.LANCZOS)
    photo_img = ImageTk.PhotoImage(img)

    label = tk.Label(afk_window, image=photo_img)
    label.photo_img = photo_img  # Keep a reference
    label.pack(expand=True)

    # Bind key events for fail-safe unlock sequence
    key_sequence = []

    def on_key_press(event):
        nonlocal key_sequence
        key = event.keysym.lower()
        print(f"Key pressed: {key}")

        # Track the sequence S -> A -> M
        if key == 's' and (not key_sequence or key_sequence[-1] == 'm'):
            key_sequence = ['s']
        elif key == 'a' and key_sequence == ['s']:
            key_sequence.append('a')
        elif key == 'm' and key_sequence == ['s', 'a']:
            key_sequence.append('m')

            # Trigger fail-safe unlock when sequence 'S', 'A', 'M' is complete
            if key_sequence == ['s', 'a', 'm']:
                print("Triggering fail-safe unlock...")
                fail_safe_unlock(afk_window, stop_event)
                key_sequence = []
        else:
            key_sequence = []

    afk_window.bind('<KeyPress>', on_key_press)

    # Run the Tkinter event loop
    while not stop_event.is_set():
        afk_window.update_idletasks()
        afk_window.update()

    afk_window.quit()  # Exit the Tkinter loop once stop_event is set


def camera_thread(stop_event):
    cap = cv2.VideoCapture(0)
    hand_wireframe = HandWireframe()
    blink_counter = 0
    blink_detected = False
    peace_sign_detected = False

    while not stop_event.is_set():
        ret, frame = cap.read()
        if not ret or frame is None:
            print("Failed to capture frame. Exiting...")
            break

        # Check for peace sign
        peace_sign_detected = hand_wireframe.draw_hand_wireframe(frame)

        if not isinstance(peace_sign_detected, bool):
            print("Error: peace_sign_detected is not a boolean.")
            continue

        if peace_sign_detected:
            blink_counter, blink_detected = detect_face_and_blink(frame, blink_counter, blink_detected)
            if blink_counter >= 2:
                try:
                    for ref_img in output_images:
                        result = DeepFace.verify(frame, ref_img, detector_backend='opencv')
                        if result['verified']:
                            print("Face recognized. Unlocking...")
                            stop_event.set()  # Signal to stop the AFK window and unlock
                            cap.release()
                            return
                except Exception as e:
                    print(f"Error during face recognition: {e}")

        # Display the frame (this is not visible due to off-screen window)
        cv2.imshow("Camera", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()


def main():
    stop_event = Event()  # Event to signal when to stop
    image_path = os.getenv("BACKGROUND_IMAGE_PATH")  # Path to lock screen image

    # Start the AFK/Lock Screen window in a separate thread
    afk_thread = Thread(target=show_afk_window, args=(stop_event, image_path))
    afk_thread.start()

    # Start the camera thread
    camera_thread(stop_event)

    # Wait for threads to finish
    afk_thread.join()


if __name__ == "__main__":
    main()
