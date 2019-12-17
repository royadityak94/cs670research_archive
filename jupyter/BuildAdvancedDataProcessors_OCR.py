import numpy as np
import os
import io
from matplotlib.image import imread
import xml.etree.ElementTree as ET 
from AdvancedDataPreprocessing import TransformDataset
import matplotlib.pyplot as plt

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

def create_new_xml_file(base, file, new_base, type):
    xml_file = file[:len(file)-4] + '.xml' 
    tree = ET.parse(os.path.join(base, xml_file))
    tree.write(os.path.join(new_base, type+xml_file), encoding='utf8')
    

bases = {'datasets/neocr_dataset/OCR/':400}
for base in bases.keys():
    new_base = '/'.join(base.split('/')[:-2]) + '/noises'
    dict_files, files_idx = get_mapped(base)
    existing_files = list(set([dict_files.get(idx).split('_')[-1] for idx in files_idx ]))
    
    print ("Iterating for Base = {}".format(base))
    
    MAX_ITR = int(bases.get(base))
    applicants = ['perform_swirl_transformation', 'add_shot_noise', 'add_gaussian_noise', 'add_impulse_noise', 'add_glass_blur', 'add_gaussian_blur']
    severity_list = [2, 4, 6]
    exclusion = []
    
    seen = []
    
    for itr in range(MAX_ITR):     
        if files_idx[0] in existing_files: 
            print ("Continuing...")
            continue
        
        file = dict_files.get(files_idx[0])
        content = imread(os.path.join(base, file))
        try:
            for applicant in applicants:
                for severity in severity_list:
                    new_image = TransformDataset().return_function(applicant, content, severity)
                    prefix = '%s_%s_' % (applicant, severity)
                    plt.imsave(os.path.join(new_base, prefix+file), new_image)

            new_image = TransformDataset().return_function('random_image_eraser', content)
            plt.imsave(os.path.join(new_base, 'random_image_eraser_'+file), new_image)
        except:
            continue
        
        print ("Completed Iteration = {}".format(itr))