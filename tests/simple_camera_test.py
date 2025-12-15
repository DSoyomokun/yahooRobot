#!/usr/bin/env python3
"""Simple camera test without MediaPipe to isolate the issue."""

import cv2
import time

print("Opening camera...")
cap = cv2.VideoCapture(0, cv2.CAP_AVFOUNDATION)

if not cap.isOpened():
    print("Failed to open camera with AVFoundation, trying default...")
    cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("ERROR: Could not open camera")
    exit(1)

print("Camera opened successfully")

# Configure camera
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)

print("Waiting for camera to initialize...")
time.sleep(2.0)

print("Reading warm-up frames...")
for i in range(10):
    ret, frame = cap.read()
    if ret:
        print(f"✓ Got frame {i+1}: {frame.shape}")
        if i == 0:  # After first successful frame
            break
    else:
        print(f"✗ Failed to get frame {i+1}")
    time.sleep(0.1)

if not ret:
    print("ERROR: Could not read any frames")
    cap.release()
    exit(1)

print("\nCamera working! Starting display loop...")
print("Press 'q' to quit")

frame_count = 0
while True:
    ret, frame = cap.read()
    if not ret:
        print(f"\nFailed to read frame {frame_count}")
        break

    frame_count += 1

    # Add frame counter to image
    cv2.putText(frame, f"Frame: {frame_count}", (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

    cv2.imshow("Simple Camera Test", frame)

    if frame_count % 30 == 0:
        print(f"Showing frame {frame_count}...")

    if cv2.waitKey(1) & 0xFF == ord('q'):
        print("\nQuitting...")
        break

cap.release()
cv2.destroyAllWindows()
print(f"\nTotal frames displayed: {frame_count}")
