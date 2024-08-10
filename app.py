from flask import Flask, render_template, request, redirect, url_for
import pytesseract
from PIL import Image
import os
import cv2  # OpenCV for image preprocessing

app = Flask(__name__)

# Ensure the folder to save uploaded files exists
UPLOAD_FOLDER = 'static/uploads/'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def preprocess_image(image_path):
    # Load the image using OpenCV in grayscale mode
    img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    
    # Apply Gaussian Blur to reduce noise
    img = cv2.GaussianBlur(img, (5, 5), 0)
    
    # Apply adaptive thresholding to make text more distinct
    img = cv2.adaptiveThreshold(img, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                cv2.THRESH_BINARY, 11, 2)
    
    # Save the processed image temporarily
    processed_image_path = 'static/uploads/processed_image.png'
    cv2.imwrite(processed_image_path, img)
    
    return processed_image_path

@app.route('/', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        file = request.files['image']
        if file:
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
            file.save(filepath)
            
            # Preprocess the image before OCR
            processed_filepath = preprocess_image(filepath)
            
            # Use Tesseract to extract text from the processed image
            text = pytesseract.image_to_string(Image.open(processed_filepath))
            return render_template('edit.html', text=text, image_url=filepath)
    return render_template('upload.html')

@app.route('/save', methods=['POST'])
def save():
    edited_text = request.form['edited_text']
    with open('saved_transcriptions.txt', 'a') as f:
        f.write(edited_text + '\n\n')
    return redirect(url_for('upload'))

if __name__ == '__main__':
    app.run(debug=True)
