import boto3
import io
import re
import numpy as np
import os
import xml.etree.ElementTree as ET 
from google.cloud import vision
import requests
from nltk.corpus import stopwords as stpword
from nltk.stem import WordNetLemmatizer
import json
from nltk.corpus import stopwords as stpword
from nltk.stem import WordNetLemmatizer
from utilities.image_description_scoring import matching_label_score
from time import time
from utilities.pythonDB import writeToDB, recordsExists
from utilities.score_computors import jaccard_similarity

def get_mapped(path):
    key_map, dict_idx = {}, 0
    for r, _, f in os.walk(path):
        for file in f:
            if '.JPG' in file or '.jpg' in file:
                key_map[dict_idx] = file
                dict_idx += 1
    idxs = list(key_map.keys())          
    shuffled_idxs = np.random.randint(0, len(idxs), len(idxs))
    return key_map, shuffled_idxs

def extract_clean_str(original_str):
    original_str = original_str.replace('<br/>', '')
    return re.sub('[^a-zA-Z0-9]+', ' ', original_str, flags=re.UNICODE).lower().strip().replace(' ', '')

def fetch_from_xml(path, file):
    tree = ET.parse(os.path.join(path, file)).getroot()  
    return extract_clean_str(''.join([e.attrib['char'] for e in tree.iter(tag='character')]))

class RegonizeText():
    def __init__(self, base, file): 
        with io.open(os.path.join(base, file), 'rb') as image_file:
            content = (image_file.read())
        self.content = content
        self.base, self.actual_str, self.detected_str = base, '', ''
        if 'img' in file:
            self.file = '_'.join(file.split('_')[-2:])
            if 'eraser' in file:
                self.severity, self.noise_type = -1, '_'.join(file.split('_')[1:-2])
            else:
                self.severity, self.noise_type = file.split('_')[-3], '_'.join(file.split('_')[1:-3])
        else:
            self.file = '_'.join(file.split('_')[-1:])
            if 'eraser' in file:
                self.severity, self.noise_type = -1, '_'.join(file.split('_')[1:-1])
            else:
                self.severity, self.noise_type = file.split('_')[-2], '_'.join(file.split('_')[1:-2])
        self.label = ''
        self.start = time()
        
    def return_function(self, name):
        dataset = dir_path.split('/')[1] 
        self.label = name + '-plain-OCR-noisy'
        if recordsExists(self.file, dataset, self.label, self.severity, self.noise_type):
            return
        
        status, score =  getattr(self, 'if_' + name)()
        compute_time = time() - self.start
        bag = (self.file, dataset, self.label, self.severity, self.noise_type, status, score, compute_time, self.actual_str, self.detected_str)
        writeToDB(bag)
    def compute_ground_truth(self):
        ''' 
            Status = {-1: 'XML File Missing', -2: 'Error in XML', -3: 'Ground Truth Empty', -4: 'API Error', 0: 'All Correct'} 
            Return = Ground Truth, Status
        
        '''
        xml_path = '/'.join(self.base.split('/')[:2]) + '/English'
        xml_file = self.file[:len(self.file)-4] + '.xml' 
        
        if not os.path.exists(os.path.join(xml_path, self.file)):
            return '', -1
        try:
            ground_truth_str = fetch_from_xml(xml_path, xml_file)
        except: 
            return '', -2
        
        if len(ground_truth_str) == 0:
            return '', -3
        else:
            self.actual_str = ground_truth_str
            return ground_truth_str, 0
        
    def if_aws(self):
        ground_truth, xml_status = self.compute_ground_truth()
        if xml_status != 0: return xml_status, 0
        
        try:
            imgobj = {'Bytes': self.content}
            client=boto3.client('rekognition', region_name='us-east-1')
            response=client.detect_text(Image=imgobj)
            detected_str = extract_clean_str(''.join([txt['DetectedText'] for txt in response['TextDetections'] \
                                                   if txt['Type']=='WORD']))
            self.detected_str = detected_str
            score = jaccard_similarity(detected_str, ground_truth)
            return 0, score
        except:
            return -4, 0
    
    def if_gc(self):
        ground_truth, xml_status = self.compute_ground_truth()
        if xml_status != 0: return xml_status, 0
        try:
            vision_client = vision.ImageAnnotatorClient()
            image = vision.types.Image(content=self.content)
            text_detection_response = vision_client.text_detection(image=image)
            detected_str = extract_clean_str(text_detection_response.full_text_annotation.text)
            self.detected_str = detected_str
            score = jaccard_similarity(detected_str, ground_truth)
            return 0, score
        except:
            return -4, 0
        
    def if_azure(self):
        ground_truth, xml_status = self.compute_ground_truth()
        if xml_status != 0: return xml_status, 0
        try:
            subscription_key, endpoint = os.environ['COMPUTER_VISION_SUBSCRIPTION_KEY'], os.environ['COMPUTER_VISION_ENDPOINT']
            ocr_url = endpoint + "vision/v2.1/ocr"
            headers = {'Ocp-Apim-Subscription-Key': subscription_key, 'Content-Type': 'application/octet-stream'}
            params = {'detectOrientation': 'true'}
            response = requests.post(ocr_url, headers=headers, params=params, data=self.content)
            response.raise_for_status()

            lines_info = [region["lines"] for region in response.json()["regions"]]
            detected_str = extract_clean_str(''.join([word_info['text'] for line in lines_info \
                                      for word_metadata in line for word_info in word_metadata["words"]]))
            self.detected_str = detected_str
            score = jaccard_similarity(detected_str, ground_truth)
            return 0, score
        except:
            return -4, 0

dir_path = 'datasets/KAIST/noises/'
dict_files, files_idx = get_mapped(dir_path)
shuffled_idx = np.random.randint(0, len(files_idx), len(files_idx))[:5000]

for idx in shuffled_idx:
    file_name = dict_files.get(idx)
    print ("Iterating for File Name = {}".format(file_name))
    RegonizeText(dir_path, file_name).return_function('gc')