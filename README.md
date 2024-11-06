---


<h3 align="center"> Worried about someone trying to mess with your computer while you are AFK. This project integrates face recognition, blink detection, and gesture recognition into a seamless experience. This README will help you get started with cloning, setting up, and running the project.
</h3>

---

# FBG Project

## Table of Contents
1. [Project Overview](#project-overview)
2. [Installation](#installation)
3. [How to Run](#how-to-run)
4. [Contributors](#Contributors)
5. [License](#license)

## Project Overview
1. Full-Screen Lock Screen: When the program runs, it displays a fullscreen image as a lock screen while the camera monitors for face movements, ensuring it's not an image being used.

2. Gesture and Face Recognition: The system detects a peace sign (two fingers), initiating face recognition. However, it won't unlock until you blink twice.

3. Unlocking Mechanism: Once the peace sign is detected and the required blinks are registered, the system recognizes your face and unlocks the screen.

## Installation
Getting Started

### 1. Clone the Repository

```bash
git clone <repository_url>
cd <repository_name>
```

### 2. Install the requirements.txt
```bash
pip install -r requirements.txt
```

### 3. Setup your Environment Variables
- **In the root folder create a .env file and add the following 
```bash
REFERENCE_IMAGES="reference1.jpg,reference2.png,reference3.jpg"
BACKGROUND_IMAGE_PATH="path/to/background_image.jpg"
```

### 4. Download Additional Resources

This project requires the `shape_predictor_68_face_landmarks.dat` file, which is used for facial landmark detection in dlib.

1. Download the file from [dlib’s model page](http://dlib.net/files/shape_predictor_68_face_landmarks.dat.bz2).
2. Extract the downloaded file if it is in a compressed format (e.g., `.bz2`).
3. Place the `shape_predictor_68_face_landmarks.dat` file in the project root directory.

## How to Run

Once everything is set up, you can start the application by running the following command:

```bash
python face_recog.py
```

## Note
- **Fail-safe Unlock**: Press **S → A → M** in sequence to trigger a password prompt.
