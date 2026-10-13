import cv2
import mediapipe as mp
import pyautogui
import time

# Initialize camera and MediaPipe FaceMesh
cam = cv2.VideoCapture(0)
face_mesh = mp.solutions.face_mesh.FaceMesh(refine_landmarks=True)
screen_w, screen_h = pyautogui.size()

# Store previous coordinates for relative movement
prev_x, prev_y = 0, 0

# Sensitivity and smoothing configuration
sensitivity = 3.0       # Higher = more responsive cursor movement
smoothing = 0.5         # Between 0 and 1, higher = smoother, less responsive

# Blink detection config
blink_threshold = 5     # Vertical eye distance in pixels considered a blink
click_delay = 1         # Seconds to wait between clicks

last_click_time = 0     # For click cooldown

while True:
    success, frame = cam.read()
    if not success:
        break

    # Flip the frame horizontally for mirror effect
    frame = cv2.flip(frame, 1)
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    output = face_mesh.process(rgb_frame)
    landmark_points = output.multi_face_landmarks
    frame_h, frame_w, _ = frame.shape

    if landmark_points:
        landmarks = landmark_points[0].landmark

        # -------- Eye Tracking (Right Eye: landmarks 474–477) --------
        for id, landmark in enumerate(landmarks[474:478]):
            x = int(landmark.x * frame_w)
            y = int(landmark.y * frame_h)
            cv2.circle(frame, (x, y), 3, (0, 255, 0), -1)

            if id == 1:  # Landmark 475: best for eye center
                current_x = screen_w * landmark.x
                current_y = screen_h * landmark.y

                # Apply smoothing and sensitivity to calculate movement
                move_x = (current_x - prev_x) * sensitivity
                move_y = (current_y - prev_y) * sensitivity

                # Optional: smoothing effect
                move_x *= smoothing
                move_y *= smoothing

                # Move cursor relative to previous position
                pyautogui.moveRel(move_x, move_y)

                # Update previous coordinates
                prev_x = current_x
                prev_y = current_y

        # -------- Blink Detection (Left Eye: landmarks 145 & 159) --------
        left_eye_top = landmarks[159]
        left_eye_bottom = landmarks[145]
        x1 = int(left_eye_top.x * frame_w)
        y1 = int(left_eye_top.y * frame_h)
        x2 = int(left_eye_bottom.x * frame_w)
        y2 = int(left_eye_bottom.y * frame_h)

        # Visualize blink points
        cv2.circle(frame, (x1, y1), 3, (255, 0, 255), -1)
        cv2.circle(frame, (x2, y2), 3, (255, 0, 255), -1)

        # Check if blink is detected (eye almost closed)
        vertical_distance = abs(y2 - y1)
        current_time = time.time()
        if vertical_distance < blink_threshold and (current_time - last_click_time) > click_delay:
            pyautogui.click()
            last_click_time = current_time  # Prevent multiple clicks

    # -------- Display Frame --------
    cv2.imshow('Eye Controlled Mouse (Press ESC to Exit)', frame)

    # Exit on ESC key
    if cv2.waitKey(1) & 0xFF == 27:
        break

# -------- Cleanup --------
cam.release()
cv2.destroyAllWindows()
