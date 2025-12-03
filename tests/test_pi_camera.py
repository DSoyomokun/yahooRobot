import cv2

def main():
    # Use /dev/video0 (your IMX219 CSI camera)
    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        print("Error: Could not open /dev/video0")
        return

    print("Camera opened. Press 'q' to quit.")

    while True:
        ret, frame = cap.read()
        if not ret:
            print("Failed to grab frame")
            break

        cv2.imshow("Pi Camera Test (/dev/video0)", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()