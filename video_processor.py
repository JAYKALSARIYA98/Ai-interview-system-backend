import cv2
import mediapipe as mp
import numpy as np

# Initialize MediaPipe Face Mesh
mp_face_mesh = mp.solutions.face_mesh
face_mesh = mp_face_mesh.FaceMesh()


def analyze_frame(frame):
    """Analyze a single frame for facial expressions and eye contact."""
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    # Get the image dimensions (height and width)
    frame_height, frame_width = frame.shape[:2]
    image_dimensions = np.array([frame_width, frame_height])  # Pass actual image dimensions

    # Process the frame with the image dimensions
    results = face_mesh.process(rgb_frame)

    if results.multi_face_landmarks:
        face_landmarks = results.multi_face_landmarks[0]

        # Calculate eye contact (example heuristic)
        left_eye = np.array([(face_landmarks.landmark[i].x, face_landmarks.landmark[i].y) for i in range(36, 42)])
        right_eye = np.array([(face_landmarks.landmark[i].x, face_landmarks.landmark[i].y) for i in range(42, 48)])
        eye_contact = calculate_eye_contact(left_eye, right_eye)

        # Calculate confidence and nervousness (example heuristic)
        confidence = 0.8  # Placeholder
        nervousness = 0.2  # Placeholder

        return {
            "confidence": confidence,
            "nervousness": nervousness,
            "eye_contact": eye_contact,
        }

    return None


def calculate_eye_contact(left_eye, right_eye):
    """Calculate eye contact based on eye landmarks."""
    eye_center = np.mean(np.vstack((left_eye, right_eye)), axis=0)
    image_center = np.array([0.5, 0.5])  # Normalized coordinates
    dx = eye_center[0] - image_center[0]
    dy = eye_center[1] - image_center[1]
    angle = np.arctan2(dy, dx)
    return 1 if np.abs(angle) < 0.2 else 0  # Threshold for direct eye contact


def calculate_score(confidence, nervousness, eye_contact):
    """Calculate score based on the overall analysis."""
    score = 10 * (confidence + eye_contact) / 2 - (nervousness * 2)
    return min(max(score+3, 0), 10)  # Ensure score is between 0 and 10


def generate_feedback(confidence, nervousness, eye_contact):
    """Generate feedback based on the analysis."""
    feedback = []

    if confidence > 0.7:
        feedback.append("You appear confident.")
    else:
        feedback.append("You seem a bit unsure.")

    if nervousness < 0.3:
        feedback.append("You seem calm and composed.")
    else:
        feedback.append("You seem a bit nervous.")

    if eye_contact > 0.5:
        feedback.append("You maintained good eye contact.")
    else:
        feedback.append("You lacked eye contact during the interview.")

    return " ".join(feedback)


def process_video(video_path):
    """Process a video file and return overall metrics and feedback."""
    cap = cv2.VideoCapture(video_path)
    results = []

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        # Debugging: Print when video frame processing starts
        print("Starting video frame processing...")

        # Analyze the frame and get results
        analysis = analyze_frame(frame)
        if analysis:
            results.append(analysis)

        # Debugging: Print when video frame processing ends
        print("Finished video frame processing.")

    cap.release()

    # Calculate overall metrics
    overall_confidence = np.mean([r["confidence"] for r in results])
    overall_nervousness = np.mean([r["nervousness"] for r in results])
    overall_eye_contact = np.mean([r["eye_contact"] for r in results])

    # Calculate the score
    score = calculate_score(overall_confidence, overall_nervousness, overall_eye_contact)

    # Generate feedback
    feedback = generate_feedback(overall_confidence, overall_nervousness, overall_eye_contact)

    return {
        "score": score,
        "feedback": feedback,
    }


if __name__ == "__main__":
    # Specify the video path
    video_path = "your_video.mp4"  # Replace with the path to your video file

    # Process the video and get the analysis
    results = process_video(video_path)
    print("\nOverall Analysis:")
    print(f"Score: {results['score']}/10")
    print(f"Feedback: {results['feedback']}")
