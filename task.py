import pandas as pd
import re
from pdf2image import convert_from_path
import cv2
from paddleocr import PaddleOCR, draw_ocr
import warnings
import os
warnings.filterwarnings("ignore")
import logging
logging.getLogger("ppocr").setLevel(logging.INFO)
from PIL import Image
from PIL import ImageFont

# we need to convert the pdf to the image to feed the model
images = convert_from_path("Sample Problem.pdf")
# make folder to save the pages as image from the PDF for the input to the model
image_folder = 'images'
os.makedirs(image_folder, exist_ok=True)

for i, image in enumerate(images):
    image.save(os.path.join(image_folder, 'page'+ str(i) +'.jpg'), 'JPEG')

""" 
    A function that reads the image, detect the contours using openCV library.
    Once we detect the countours, we check if it is rectangle, if it is, then we sort them and store the
    coordinates of the rectangles and return the coordinates.
"""
def func(path):
  image = cv2.imread(path)
  gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
  edges = cv2.Canny(gray, 50, 150)
  contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
  rectangles = []
  for contour in contours:
      approx = cv2.approxPolyDP(contour, 0.04 * cv2.arcLength(contour, True), True)
      if len(approx) == 4:
          rectangles.append(approx)
  rectangles.sort(key=lambda x: cv2.contourArea(x), reverse=True)
  cropped_images = []
  for rect in rectangles:
    if cv2.contourArea(rect) < rectangles[1][0][0][0]:
      break
    else:
      x, y, w, h = cv2.boundingRect(rect)
      cropped_image = image[y:y+h, x:x+w]
      cropped_images.append(cropped_image)
  return cropped_images

# getting coordinates of the boxes to crop them, so that we can detect the text in it
all_images = []
image_files = [f for f in os.listdir(image_folder) if f.endswith('.jpg')]
for image_path in image_files:
    all_images.append(func(os.path.join("images",image_path)))
# creating to folder to annotate the image and save it
result_images = 'result_images'
os.makedirs(result_images, exist_ok=True)

# we are using pretrained paddleOCR model to predict the model
ocr = PaddleOCR(use_angle_cls=True, lang='en')

messages = []
font_path = '/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf'
for cropped_images in all_images:
    for i in range(len(cropped_images)):
        # getting the text from the model
        result = ocr.ocr(cropped_images[i], cls=True)
        image = Image.fromarray(cropped_images[i])
        boxes = [line[0] for line in result[0]]
        txts = [line[1][0] for line in result[0]]
        scores = [line[1][1] for line in result[0]]
        # annotating the image with the OCR text detected
        im_show = draw_ocr(image, boxes, txts, scores, font_path=font_path)  
        im_show = Image.fromarray(im_show)
        im_show.save(os.path.join(result_images,'result' + str(i) + '.jpg'))
        # storing the texts only as we need texts only
        messages.append(txts)

# note that the "Deleted" watermarked images contain a character E at the place of serial number, so drop them
profiles = []
for message in messages:
    x = True
    for info in message:
        if 'E' == info:
            x = False
            break
    if x:
        profiles.append([item.upper() for item in message])

# We dont need the information of "Photo Available", so remove the redundancy
for profile in profiles:
    if 'PHOTO' in profile:
        profile.remove('PHOTO')
    if 'AVAILABLE' in profile:
        profile.remove('AVAILABLE')

"""
    this class will store all the essential information corresponding to a profile.
    Necessary informations are:
        1. Age
        2. Gender
        3. Address
        4. Name
        5. Relative's Name
        6. Relation type
        7. Serial Number 
        8. Eipc Number
    The functions do the tasks as specified. 

    Note that PaddleOCR model returns the text from top to bottom, left to right order, hence, serial number 
    and epic numbers are the first two values in the array.

"""
class Profile:
    def __init__(self, profile_data):
        self.profile_data = profile_data
        self.age = None
        self.gender = None
        self.address = None
        self.name = None
        self.relative_name = None
        self.relation_type = None
        self.sl_no = None
        self.epic_no = None

        # Automatically extract and set profile properties
        self.extract_gender_and_age()
        self.extract_house_number()
        self.extract_relation_info()
        self.extract_sl_no_and_epic_no()

    def extract_gender_and_age(self):
        """
            Updates the Age and Gender to appropriate values.

            check if any string that contains AGE followed by any characters including space.
            then check if there is any digits, if yes store it and it will be the age.

            Similary, if Gender is mentioned we just need to check if there exist Female or male.
        """
        for item in self.profile_data:
            pattern = r'AGE.+'
            if re.search(pattern, item, flags=re.IGNORECASE):
                age = ""
                for i in item:
                    if i.isdigit():
                        age += i
                self.age = int(age)
            pattern_gender = r"GENDER.*?(FEMALE|MALE)"

            match = re.search(pattern_gender, item, flags=re.IGNORECASE)

            if match:
                gender = match.group(1).upper()
                self.gender = 'M' if gender=="MALE" else 'F'

    def extract_house_number(self):
        """
            Updates the Address to appropriate value.

            We need to check if any string contains HOUSE and NUMBER, the texts following that should
            be the address.

            Note, spaces characters in the beginning of the adresses are removed.
        """
        for item in self.profile_data:
            item = re.sub(r'^[^\w]+', '', item)
            match = re.search(r'HOUSE\s*[^a-zA-Z0-9]*NUMBER\s*[^a-zA-Z0-9]*([\w\s-]*)', item, re.IGNORECASE)
            if match:
                self.address = re.sub(r'^\W+|\W+$', '', match.group(1))

    def extract_relation_info(self):
        """
            updates Name, and relatives name and relation type using regex
        """
        name_pattern = r'NAME\W*(.*)'
        father_name_pattern = r"FATHER'?S?\W*NAME\W*(.*)"
        husband_name_pattern = r"HUSBAND'?S?\W*NAME\W*(.*)"
        others_pattern = r"OTHERS\W*(.*)"

        for item in self.profile_data:
            if re.search(father_name_pattern, item, re.IGNORECASE):
                self.relative_name = re.search(father_name_pattern, item, re.IGNORECASE).group(1).strip()
                self.relation_type = 'FTHR'
                break
            elif re.search(husband_name_pattern, item, re.IGNORECASE):
                self.relative_name = re.search(husband_name_pattern, item, re.IGNORECASE).group(1).strip()
                self.relation_type = 'HSBN'
                break
            elif re.search(others_pattern, item, re.IGNORECASE):
                self.relative_name = re.search(others_pattern, item, re.IGNORECASE).group(1).strip()
                self.relation_type = 'OTHR'
                break
            elif re.search(name_pattern, item, re.IGNORECASE):
                self.name = re.search(name_pattern, item, re.IGNORECASE).group(1).strip()

    def extract_sl_no_and_epic_no(self):
        if len(self.profile_data) >= 2:
            self.sl_no = self.profile_data[0]
            self.epic_no = self.profile_data[1]

    def get_profile_info(self):
        return {
            "Age": self.age,
            "Gender": self.gender,
            "Address": self.address,
            "Name": self.name,
            "Relative Name": self.relative_name,
            "Relation Type": self.relation_type,
            "SL No": self.sl_no,
            "EPIC No": self.epic_no
        }




profile_objects = [Profile(data) for data in profiles]


data = []

for profile in profile_objects:
    profile_info = profile.get_profile_info()
    data.append({
        "Part S.No": profile_info["SL No"],
        "Voter Full Name": profile_info["Name"],
        "Relative's Name": profile_info["Relative Name"],
        "Relation Type": profile_info["Relation Type"],
        "Age": profile_info["Age"],
        "Gender": profile_info["Gender"],
        "House No": profile_info["Address"],
        "EPIC No": profile_info["EPIC No"]
    })

# Convert the list of dictionaries into a pandas DataFrame
df = pd.DataFrame(data)
df = df.sort_values(by="Part S.No", key=lambda x: pd.to_numeric(x, errors='coerce')).reset_index(drop=True)
# Save the DataFrame to an Excel file
df.to_excel("voter_data.xlsx", index=False)

print("Data exported successfully to voter_data.xlsx")

