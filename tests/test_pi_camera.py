import cv2

def main():
    cap = cv2.VideoCapture(0)

    # 🔹 Lower resolution = less data to send over X11
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 320)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 240)

    # Optional: cap FPS (not all drivers obey this)
    cap.set(cv2.CAP_PROP_FPS, 10)

    if not cap.isOpened():
        print("Error: Could not open /dev/video0")
        return

    print("Camera opened. Press 'q' in the window to quit.")

    frame_count = 0

    while True:
        ret, frame = cap.read()
        if not ret:
            print("Failed to grab frame")
            break

        frame_count += 1

        # 🔹 Optionally only show every 2nd or 3rd frame
        if frame_count % 2 != 0:
            continue
        
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        cv2.imshow("Pi Camera Test (/dev/video0) - Grayscale", gray)

        cv2.imshow("Pi Camera Test (/dev/video0)", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()
    print("Done.")

if __name__ == "__main__":
    main()