# Profile Detection Using OCR

This project is designed to perform Optical Character Recognition (OCR) on images or PDFs using Python. The script leverages libraries like PaddleOCR, OpenCV, and PIL to extract and process text from visual data.

## Prerequisites

Ensure you have Python installed (version 3.x recommended).

## Installation

To set up the environment and install the required libraries, follow these steps:

1. Clone the repository:

    ```bash
    git clone https://github.com/Debdut0122/detect-profile-data-using-OCR.git
    ```

2. Navigate to the project directory:

    ```bash
    cd detect-profile-data-using-OCR
    ```

3. Install the necessary Python packages using pip:

    ```bash
    pip install pandas re pdf2image opencv-python paddlepaddle paddleocr pillow
    ```

    Alternatively, you can install all the libraries from the `requirements.txt` file if provided:

    ```bash
    pip install -r requirements.txt
    ```

## Libraries Used

- **pandas**: For exporting the output to an `.xlsx` file.
- **re**: For regular expression operations.
- **pdf2image**: To convert PDF files into images.
- **cv2 (OpenCV)**: For image processing.
- **PaddleOCR**: For Optical Character Recognition (OCR).
- **PIL (Pillow)**: For image handling.
- **warnings**: To manage warnings in the script.
- **logging**: For controlling logging behavior.

## How to Run the Script

1. Make sure all the necessary libraries are installed.

2. Run the script:

    ```bash
    python3 task.py
    ```

The script will process the images or PDFs and output the extracted text.
