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

        if not os.path.exists(image_path):
            return None

        image = cv2.imread(image_path)

        if image is None:
            return None

        # Convert to grayscale
        gray = cv2.cvtColor(
            image,
            cv2.COLOR_BGR2GRAY
        )

        # Resize only if image is small
        h, w = gray.shape

        if w < 1000:
            gray = cv2.resize(
                gray,
                None,
                fx=4,
                fy=4,
                interpolation=cv2.INTER_CUBIC
            )

        # OCR directly on grayscale image
        config = (
            "--oem 3 "
            "--psm 7 "
            "-c tessedit_char_whitelist=0123456789"
        )

        text = pytesseract.image_to_string(
            gray,
            config=config
        )

        print("OCR:", text)

        numbers = re.findall(r"\d+", text)

        if not numbers:
            return None

        # Accept numbers with 3–6 digits
        valid_numbers = []

        for num in numbers:

            if 3 <= len(num) <= 6:
                valid_numbers.append(num)

        if valid_numbers:

            valid_numbers = list(set(valid_numbers))

            valid_numbers.sort(
                key=len,
                reverse=True
            )

            print("Detected:", valid_numbers)

            return valid_numbers[0]

        return numbers[0]

    except Exception as e:

     print("========== OCR ERROR ==========")
    print("OCR ERROR TYPE:", type(e).__name__)
    print("OCR ERROR:", str(e))
    print("================================")

    return None