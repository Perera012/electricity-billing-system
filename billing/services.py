import cv2
import pytesseract
import re
import os
import platform

# Configure Tesseract
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

        # Resize only if the image is small
        height, width = gray.shape

        if width < 1000:
            gray = cv2.resize(
                gray,
                None,
                fx=4,
                fy=4,
                interpolation=cv2.INTER_CUBIC
            )

        best_number = None

        # Only two thresholds (saves memory)
        for threshold in [120, 160]:

            _, thresh = cv2.threshold(
                gray,
                threshold,
                255,
                cv2.THRESH_BINARY
            )

            # Only two OCR attempts
            for psm in [6, 7]:

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

                if not numbers:
                    continue

                # Accept numbers between 3 and 6 digits
                valid_numbers = []

                for num in numbers:

                    if 3 <= len(num) <= 6:
                        valid_numbers.append(num)

                if valid_numbers:

                    # Remove duplicates
                    valid_numbers = list(set(valid_numbers))

                    # Prefer the longest number
                    valid_numbers.sort(
                        key=len,
                        reverse=True
                    )

                    print("Detected:", valid_numbers)

                    return valid_numbers[0]

                # Keep the best fallback
                for num in numbers:

                    if (
                        best_number is None
                        or len(num) > len(best_number)
                    ):
                        best_number = num

        return best_number

    except Exception as e:

        print("OCR ERROR:", e)

        return None