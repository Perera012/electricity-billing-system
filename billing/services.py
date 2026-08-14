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

        print("========== OCR START ==========")
        print("Image path:", image_path)
        print("Image exists:", os.path.exists(image_path))

        # Check image file
        if not os.path.exists(image_path):
            print("OCR ERROR: Image file does not exist.")
            return None

        # Check Tesseract
        print("Tesseract path:",
              pytesseract.pytesseract.tesseract_cmd)

        # Read image
        image = cv2.imread(image_path)

        if image is None:
            print("OCR ERROR: OpenCV could not read the image.")
            return None

        # Convert to grayscale
        gray = cv2.cvtColor(
            image,
            cv2.COLOR_BGR2GRAY
        )

        # Resize if image is small
        h, w = gray.shape

        if w < 1000:
            gray = cv2.resize(
                gray,
                None,
                fx=4,
                fy=4,
                interpolation=cv2.INTER_CUBIC
            )

        # OCR configuration
        config = (
            "--oem 3 "
            "--psm 7 "
            "-c tessedit_char_whitelist=0123456789"
        )

        text = pytesseract.image_to_string(
            gray,
            config=config
        )

        print("OCR RAW TEXT:", text)

        numbers = re.findall(r"\d+", text)

        if not numbers:
            print("OCR ERROR: No numbers detected.")
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

            print("Detected numbers:", valid_numbers)
            print("Selected reading:", valid_numbers[0])
            print("=========== OCR END ===========")

            return valid_numbers[0]

        print("Detected numbers:", numbers)
        print("Selected reading:", numbers[0])
        print("=========== OCR END ===========")

        return numbers[0]

    except Exception as e:

        print("OCR ERROR:", e)

        return None