from flask import Blueprint, Flask, render_template, request, send_from_directory, session, Response, current_app
import pandas as pd
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import csv
import os
import cv2
import base64
import json
import pickle
from werkzeug.utils import secure_filename
import numpy as np

objectDetection = Blueprint('views', __name__)

def detect_object(uploaded_image_path):
    # Loading image
    img = cv2.imread(uploaded_image_path)

    # Load Yolo
    yolo_weight = "website/data/model/yolov3.weights"
    yolo_config = "website/data/model/yolov3.cfg"
    coco_labels = "website/data/model/coco.names"
    net = cv2.dnn.readNet(yolo_weight, yolo_config)

    classes = []
    with open(coco_labels, "r") as f:
        classes = [line.strip() for line in f.readlines()]

    # Defining desired shape
    fWidth = 320
    fHeight = 320

    # Resize image in OpenCV
    img_resized = cv2.resize(img, (fWidth, fHeight))

    height, width, channels = img.shape

    # Convert image to Blob
    blob = cv2.dnn.blobFromImage(img_resized, 1 / 255, (fWidth, fHeight), (0, 0, 0), True, crop=False)
    # Set input for YOLO object detection
    net.setInput(blob)

    # Find names of all layers
    layer_names = net.getLayerNames()
    # Find names of three output layers
    output_layers = [layer_names[i - 1] for i in net.getUnconnectedOutLayers()]

    # Send blob data to forward pass
    outs = net.forward(output_layers)

    # Generating random color for all 80 classes
    colors = np.random.uniform(0, 255, size=(len(classes), 3))

    # Extract information on the screen
    class_ids = []
    confidences = []
    boxes = []
    labels = {}

    for out in outs:
        for detection in out:
            # Extract score value
            scores = detection[5:]
            # Object id
            class_id = np.argmax(scores)
            # Confidence score for each object ID
            confidence = scores[class_id]
            # Extract values to draw bounding box
            center_x = int(detection[0] * width)
            center_y = int(detection[1] * height)
            w = int(detection[2] * width)
            h = int(detection[3] * height)
            # Rectangle coordinates
            x = int(center_x - w / 2)
            y = int(center_y - h / 2)
            boxes.append([x, y, w, h])
            confidences.append(float(confidence))
            class_ids.append(class_id)

            label = str(classes[class_id])
            confidence_label = float(confidence)
            if label in labels:
                # Append confidence score if the label already exists
                labels[label].append(confidence_label)
            else:
                # Create a new entry in the dictionary if the label doesn't exist
                labels[label] = [confidence_label]

    # Apply non-maximum suppression to remove overlapping bounding boxes
    indices = cv2.dnn.NMSBoxes(boxes, confidences, score_threshold=0.5, nms_threshold=0.4)

    # Draw bounding boxes and labels on the original, untransformed image
    font = cv2.FONT_HERSHEY_TRIPLEX
    for i in indices:
        x, y, w, h = boxes[i]
        label = str(classes[class_ids[i]])
        confidence_label = int(confidences[i] * 100)
        color = colors[class_ids[i]]
        cv2.rectangle(img, (x, y), (x + w, y + h), color, 2)
        cv2.putText(img, f'{label}, {confidence_label}', (x - 25, y + 75), font, 3, color, 2)

    # Write output image (object detection output)
    output_image_path = os.path.join(current_app.config['UPLOAD_FOLDER'], 'output_image.jpg')
    cv2.imwrite(output_image_path, img)

    return output_image_path, labels

@objectDetection.route('/',  methods=("POST", "GET"))
def uploadFile():
    if request.method == 'POST':
        uploaded_img = request.files['uploaded-file']
        img_filename = secure_filename(uploaded_img.filename)
        uploaded_img.save(os.path.join(current_app.config['UPLOAD_FOLDER'], img_filename))
 
        session['uploaded_img_file_path'] = os.path.join(current_app.config['UPLOAD_FOLDER'], img_filename)
        session['uploaded_img_file_name'] = img_filename
        
        output_image_name = session.get('uploaded_img_file_name', None)
        return render_template('show_image.html', filename = output_image_name)
    return render_template('index.html', message ="Please upaload the image!")
    
@objectDetection.route('/detect_object')
def detectObject():
    uploaded_image_path = session.get('uploaded_img_file_path', None)
    output_image_path , _ = detect_object(uploaded_image_path)
    print(output_image_path)
    return render_template('show_image.html', filename = "output_image.jpg")

@objectDetection.after_request
def add_header(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response