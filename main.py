import cv2
import mediapipe as mp
import pyautogui
import time

# Initialize camera and MediaPipe FaceMesh
cam = cv2.VideoCapture(0)
face_mesh = mp.solutions.face_mesh.FaceMesh(refine_landmarks=True)
screen_w, screen_h = pyautogui.size()

while True:
    success, frame = cam.read()
    if not success:
        break

    frame = cv2.flip(frame, 1)
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    output = face_mesh.process(rgb_frame)
    landmark_points = output.multi_face_landmarks
    frame_h, frame_w, _ = frame.shape

    if landmark_points:
        landmarks = landmark_points[0].landmark

        # Eye tracking with right eye landmarks (474–477)
        for id, landmark in enumerate(landmarks[474:478]):
            x = int(landmark.x * frame_w)
            y = int(landmark.y * frame_h)
            cv2.circle(frame, (x, y), 3, (0, 255, 0), -1)
            if id == 1:
                screen_x = screen_w * landmark.x
                screen_y = screen_h * landmark.y
                pyautogui.moveTo(screen_x, screen_y)

        # Blink detection using left eye landmarks [145, 159]
        left_eye_top = landmarks[159]
        left_eye_bottom = landmarks[145]
        x1 = int(left_eye_top.x * frame_w)
        y1 = int(left_eye_top.y * frame_h)
        x2 = int(left_eye_bottom.x * frame_w)
        y2 = int(left_eye_bottom.y * frame_h)
        cv2.circle(frame, (x1, y1), 3, (255, 0, 255), -1)
        cv2.circle(frame, (x2, y2), 3, (255, 0, 255), -1)

        # Check for blink (eye almost closed)
        if abs(y2 - y1) < 5:
            pyautogui.click()
            time.sleep(1)

    cv2.imshow('Eye Controlled Mouse', frame)

    if cv2.waitKey(1) & 0xFF == 27:  # Press ESC to exit
        break

cam.release()
cv2.destroyAllWindows()
