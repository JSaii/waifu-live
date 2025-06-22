import cv2
from multiprocessing import Event

def run_camera(event, ready_event):
    cap = cv2.VideoCapture(1)

    if not cap.isOpened():
        print("Cannot open camera")
        exit()

    ready_event.set()
    while True:
        ret, frame = cap.read()
        if not ret:
            print("Can't receive frame (stream end?). Exiting ...")
            break
        cv2.imshow('Webcam Feed', frame)
        if cv2.waitKey(1) == ord('q'):
            break

        if event.is_set():
            cv2.imwrite("resources/screenshot.jpg", frame)
            event.clear()
        else : continue

    cap.release()
    cv2.destroyAllWindows()
