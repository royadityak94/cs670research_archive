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
from utilities.pythonDB import writeToDB_label, recordsExists_label

stopwords = set(stpword.words('english'))
wordNetLemma = WordNetLemmatizer()

def extract_clean_list(original_list):
    cleaned = list(set([wordNetLemma.lemmatize(obj_item.lower().strip()) for item in original_list for obj_item in item.split() if obj_item not in stopwords]))
    return [item.strip() for item in [re.sub('[^a-zA-Z0-9]+', ' ', item, flags=re.UNICODE) for item in cleaned]]

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

def get_captions(base_path, annotation_file):
    with open(os.path.join(base_path, annotation_file)) as json_file:
        caption_file = json.load(json_file)
    captions, mapped_annotation = {}, {}

    for annotation in caption_file['annotations']:
        mapped_annotation[annotation['image_id']] = annotation['caption']

    for image in caption_file['images']:
        captions[image['file_name']] = mapped_annotation.get(image['id'])
    return captions

class DetectLabels():
    def __init__(self, base, file, max_labels=30):
        
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
        self.max_labels = max_labels
        
    def return_function(self, name):
        dataset = self.base.split('/')[1]
        self.label = name + '-noisy'
        if recordsExists_label(self.file, dataset, self.label, self.severity, self.noise_type):
            return
        
        status, score =  getattr(self, 'if_' + name)()
        compute_time = time() - self.start
        self.label = name + '-noisy'
        
        if score != 0:
            score1, score2, score3 = score[0], score[1], score[2]
        else:
            score1, score2, score3 = 0.0, 0.0, 0.0
        
        bag = (self.file, dataset, self.label, self.severity, self.noise_type, status, score1, score2, score3, compute_time, self.actual_str, self.detected_str)
        writeToDB_label(bag)
        
    def compute_ground_truth(self):
        ''' Status = {-1:'API Error', -2: 'Ground Truth Empty', 0: 'All Correct'}, Return = Ground Truth, Status
        '''
        ground_truth_str = captions.get(self.file)
        
        if ground_truth_str is None or len(ground_truth_str) == 0:
            return '', -2
        else:
            ground_truth_str = extract_clean_list(ground_truth_str.lower().split(' '))
            self.actual_str = ground_truth_str
            return ground_truth_str, 0
    
    def if_gc(self):
        ground_truth, xml_status = self.compute_ground_truth()
        if xml_status != 0: return xml_status, 0
        
        try:
            vision_client = vision.ImageAnnotatorClient()
            image = vision.types.Image(content=self.content)
            text_detection_response = vision_client.label_detection(image=image)
            detected_label = extract_clean_list([str(label.description).lower() for label in text_detection_response.label_annotations])
            score1 = matching_label_score(detected_label, ground_truth, 1)
            score2 = matching_label_score(detected_label, ground_truth, 2)
            score3 = matching_label_score(detected_label, ground_truth, 3)
            score = [score1, score2, score3]
            
            self.detected_str = detected_label
            return 0, score
        except:
            return -1, 0
            
    def if_aws(self):
        ground_truth, xml_status = self.compute_ground_truth()
        if xml_status != 0: return xml_status, 0
        
        try:
            imgobj = {'Bytes': self.content}
            client=boto3.client('rekognition', region_name='us-east-1')
            response=client.detect_labels(Image=imgobj, MaxLabels=self.max_labels)
            detected_label = [label['Name'] for label in response['Labels']]
            score1 = matching_label_score(detected_label, ground_truth, 1)
            score2 = matching_label_score(detected_label, ground_truth, 2)
            score3 = matching_label_score(detected_label, ground_truth, 3)
            score = [score1, score2, score3]
            
            self.detected_str = detected_label
            return 0, score
        except:
            return -1, 0
        
    def if_azure(self):
        ground_truth, xml_status = self.compute_ground_truth()
        if xml_status != 0: return xml_status, 0
        
        try:
            subscription_key = os.environ['COMPUTER_VISION_SUBSCRIPTION_KEY']
            endpoint = os.environ['COMPUTER_VISION_ENDPOINT']
            ocr_url = endpoint + "vision/v2.1/describe"
            headers = {'Ocp-Apim-Subscription-Key': subscription_key, 'Content-Type': 'application/octet-stream'}
            params = {'maxCandidates': self.max_labels}
            response = requests.post(ocr_url, headers=headers, params=params, data=self.content).json()
            detected_label = response['description']['tags']
            score1 = matching_label_score(detected_label, ground_truth, 1)
            score2 = matching_label_score(detected_label, ground_truth, 2)
            score3 = matching_label_score(detected_label, ground_truth, 3)
            score = [score1, score2, score3]
            
            self.detected_str = detected_label
            return 0, score
        except:
            return -1, 0
        
annotation_dir_path = 'datasets/image_labeling/annotations'
train_dir_path = 'datasets/image_labeling/noises'
captions_validation = get_captions(annotation_dir_path, 'captions_val2017.json')
captions = get_captions(annotation_dir_path, 'captions_train2017.json')
captions.update(captions_validation)
del captions_validation

dict_files, files_idx = get_mapped(train_dir_path)
shuffled_idx = np.random.randint(0, len(files_idx), len(files_idx))[:6000]

for idx in shuffled_idx:
    file_name = dict_files.get(idx)
    print ("Iterating for File Name = {}".format(file_name))
    DetectLabels(train_dir_path, file_name).return_function('azure')
