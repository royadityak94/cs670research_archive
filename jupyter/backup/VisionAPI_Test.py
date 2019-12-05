import argparse
from google.oauth2 import service_account
from google.cloud import vision
import matplotlib.pyplot as plt
import cv2
import io
import re
import numpy as np
import os
import xml.etree.ElementTree as ET 
from joblib import Parallel, delayed
import multiprocessing
from utilities.score_computors import are_sentences_alike


dir_path = 'datasets/KAIST/English/'
MAX_TRAINING = 4 #5

def extract_clean_str(original_str):
    return re.sub('[^a-zA-Z0-9]+', ' ', original_str, flags=re.UNICODE).lower().strip().replace(' ', '')

def get_mapped(path):
    key_map, dict_idx = {}, 0
    for r, _, f in os.walk(dir_path):
        for file in f:
            if '.JPG' in file or '.jpg' in file:
                key_map[dict_idx] = file
                dict_idx += 1
    idxs = list(key_map.keys())          
    shuffled_idxs = np.random.randint(0, len(idxs), len(idxs))
    return key_map, shuffled_idxs

def fetch_from_xml(path, file):
    tree = ET.parse(os.path.join(path, file)).getroot()  
    return extract_clean_str(''.join([e.attrib['char'] for e in tree.iter(tag='character')]))

def compute_text_recognition(file):
    cutoff=0.6
    #print ("Iterating for file = {}".format(file))
    xml_file = file[:len(file)-4] + '.xml' 
    if not os.path.exists(os.path.join(dir_path, xml_file)):
        return False
    ground_truth_str = fetch_from_xml(dir_path, xml_file)
    if len(ground_truth_str) == 0:
        return False
    with io.open(os.path.join(dir_path, file), 'rb') as image_file:
        content = (image_file.read())
    image = vision.types.Image(content=content)
    text_detection_response = vision_client.text_detection(image=image)
    detected_str = extract_clean_str(text_detection_response.full_text_annotation.text)
    if are_sentences_alike(detected_str, ground_truth_str, cutoff) and len(detected_str) != 0:
        #correct_pred += 1
        return True
    else:
        return False
    
