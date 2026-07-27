import os
import platform
import cv2
import pytesseract
import re

import platform

if platform.system() == "Windows":
    pytesseract.pytesseract.tesseract_cmd = (
        r"C:\Program Files\Tesseract-OCR\tesseract.exe"
    )
else:
    pytesseract.pytesseract.tesseract_cmd = "/usr/bin/tesseract"

def extract_meter_reading(image_path):

    if not os.path.exists(image_path):
        return None

    image = cv2.imread(image_path)

    if image is None:
        return None

    gray = cv2.cvtColor(
        image,
        cv2.COLOR_BGR2GRAY
    )

    gray = cv2.resize(
        gray,
        None,
        fx=8,
        fy=8,
        interpolation=cv2.INTER_CUBIC
    )

    best_number = None

    for threshold in [80, 100, 120, 140, 160, 180, 200]:

        _, thresh = cv2.threshold(
            gray,
            threshold,
            255,
            cv2.THRESH_BINARY
        )

        kernel = cv2.getStructuringElement(
            cv2.MORPH_RECT,
            (2, 2)
        )

        thresh = cv2.dilate(
            thresh,
            kernel,
            iterations=1
        )

        for psm in [6, 7, 8, 13]:

            config = (
                f'--oem 3 '
                f'--psm {psm} '
                '-c tessedit_char_whitelist=0123456789'
            )

            text = pytesseract.image_to_string(
                thresh,
                config=config
            )

            print("OCR:", text)

            numbers = re.findall(r"\d+", text)

            if numbers:

                candidate = max(
                    numbers,
                    key=len
                )

                if len(candidate) >= 3:
                    return candidate

                if (
                    best_number is None or
                    len(candidate) > len(best_number)
                ):
                    best_number = candidate

    return best_number