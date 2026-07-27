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

    # Enlarge image
    gray = cv2.resize(
        gray,
        None,
        fx=8,
        fy=8,
        interpolation=cv2.INTER_CUBIC
    )

    best_number = None

    # Try multiple thresholds
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

        # Try different page segmentation modes
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

            valid_numbers = []

            for num in numbers:

                # Most electricity meters contain 4-6 digits
                if 4 <= len(num) <= 6:
                    valid_numbers.append(num)

            if valid_numbers:

                # Remove duplicates
                valid_numbers = list(set(valid_numbers))

                # Prefer the longest number
                valid_numbers.sort(
                    key=len,
                    reverse=True
                )

                print("Valid Numbers:", valid_numbers)

                return valid_numbers[0]

            # Fallback if OCR only finds short numbers
            for num in numbers:

                if best_number is None:
                    best_number = num

                elif len(num) > len(best_number):
                    best_number = num

    return best_number