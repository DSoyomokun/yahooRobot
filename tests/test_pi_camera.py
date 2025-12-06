import cv2
import argparse
from yahoo.config.cameras import CSI_CAMERA, USB_CAMERA
from yahoo.sense.camera import open_camera


def main():
    parser = argparse.ArgumentParser(description="Test CSI or USB camera on Pi.")
    parser.add_argument(
        "--cam",
        choices=["csi", "usb"],
        default="csi",
        help="Which camera to test: 'csi' (/dev/video0) or 'usb' (/dev/video1).",
    )
    parser.add_argument(
        "--headless",
        action="store_true",
        help="Run without cv2.imshow (print only).",
    )
    args = parser.parse_args()

    cfg = CSI_CAMERA if args.cam == "csi" else USB_CAMERA
    print(f"[INFO] Opening {cfg.name} at index {cfg.index}")

    cap = open_camera(cfg)
    if cap is None:
        return

    print("[INFO] Camera opened. Press 'q' in the window to quit (non-headless mode).")

    frame_idx = 0

    while True:
        ret, frame = cap.read()
        if not ret:
            print("[WARN] Failed to grab frame")
            break

        frame_idx += 1

        if args.headless:
            if frame is not None:
                h, w = frame.shape[:2]
                if frame_idx % 10 == 0:
                    print(f"[{cfg.name}] frame {frame_idx}: {w}x{h}")
            continue

        cv2.imshow(f"Camera test ({cfg.name})", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    if not args.headless:
        cv2.destroyAllWindows()
    print("[INFO] Done.")


if __name__ == "__main__":
    main()