import cv2
import pytesseract
import re
import os
import platform

# Configure Tesseract path
if platform.system() == "Windows":
    pytesseract.pytesseract.tesseract_cmd = (
        r"C:\Program Files\Tesseract-OCR\tesseract.exe"
    )
else:
    pytesseract.pytesseract.tesseract_cmd = "/usr/bin/tesseract"


def extract_meter_reading(image_path):

    try:
        print("STEP 1 - File Exists")

        if not os.path.exists(image_path):
            print("File not found")
            return None

        print("STEP 2 - Reading Image")

        image = cv2.imread(image_path)

        if image is None:
            print("Image is None")
            return None

        print("STEP 3 - Image Loaded")

        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        print("STEP 4 - Gray Complete")

        h, w = gray.shape
        print("Image Size:", w, "x", h)

        gray = cv2.resize(
            gray,
            None,
            fx=4,
            fy=4,
            interpolation=cv2.INTER_CUBIC
        )

        print("STEP 5 - Resize Complete")

        _, thresh = cv2.threshold(
            gray,
            140,
            255,
            cv2.THRESH_BINARY
        )

        print("STEP 6 - Threshold Complete")

        text = pytesseract.image_to_string(
            thresh,
            config="--oem 3 --psm 7 -c tessedit_char_whitelist=0123456789"
        )

        print("STEP 7 - OCR Finished")

        print("OCR TEXT:", text)

        numbers = re.findall(r"\d+", text)

        print("Numbers:", numbers)

        if numbers:
            return numbers[0]

        return None

    except Exception as e:
        print("OCR ERROR:", e)
        return None