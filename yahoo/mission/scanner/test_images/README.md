# Test Images Directory

Upload your test form images here for testing the scanner pipeline.

## Usage

After uploading an image, test it with:

```bash
python3 yahoo/mission/scanner/mac_tests/test_mac_run.py yahoo/mission/scanner/test_images/your_image.png
```

Or use the accuracy report script on all images in this folder:

```bash
python3 yahoo/mission/scanner/mac_tests/test_mac_accuracy_report.py
```

## Expected Format

- Images should be of test papers with:
  - Student name box (handwritten name)
  - 10 multiple-choice questions (A, B, C, D bubbles)
  - Clear, well-lit images work best


