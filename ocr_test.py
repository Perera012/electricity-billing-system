import pytesseract
from PIL import Image
import re


pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"


image_path = r"C:\Users\akash\Downloads\meter 900.png"


image = Image.open(image_path)


text = pytesseract.image_to_string(image)

print("========== OCR OUTPUT ==========")
print(text)


numbers = re.findall(r"\d+", text)

print("\nDetected Numbers:")

if numbers:
    for number in numbers:
        print(number)
else:
    print("No numbers detected.")