#!/usr/bin/env python3

from keys import ml_servicekey_wrongobject, ml_servicekey_hole, ml_servicekey_scratch
from ml_interface import MLFoundationClient, DefectCode
from database_interface import DBClient
from image_interface import ImageDBClient
import os
import sys
import time

# parameters for the global script
SLEEPTIME = 2 # seconds
APPROVED_EXTENSIONS = [".jpg", ".jpeg"]

def process_image_ml(img_path):
    defectWrongObject = clientWrongObject.modelPredictOne(
            img_path, "wrong_object","WrongObjectModel", DefectCode.WrongProduct)
    defectHole = clientHole.modelPredictOne(
            img_path, "hole","HoleModel", DefectCode.Hole)
    defectScratch = clientScratch.modelPredictOne(
            img_path, "scratch","ScratchModel", DefectCode.Scratch)
    return [defectWrongObject, defectHole, defectScratch]


def process_images(img_path, img_path2):
    # open the images
    # img = open(img_path, "rb")
    # img2 = open(img_path2, "rb")

    # get the keys for the image uploading
    key = im_client.upload(img_path)
    key2 = im_client.upload(img_path2)

    # call the ML models
    defects_lst = process_image_ml(img_path)
    defects_lst2 = process_image_ml(img_path2)
    defects = set(defects_lst + defects_lst2)

    #make the json
    imageInfo= {
        'image1' : key,
        'image2' : key2,
        'defects' : defects
    }
    print(imageInfo)

    db_client.saveMachineLearningResult(imageInfo, productExists=False)


db_client = DBClient()
#ml_client = MLFoundationClient(ml_key, offline = True)
im_client = ImageDBClient()
clientWrongObject = MLFoundationClient(ml_servicekey_wrongobject)
clientHole = MLFoundationClient(ml_servicekey_hole)
clientScratch = MLFoundationClient(ml_servicekey_scratch)

if __name__ == "__main__":
    """
    start the main program loop
    """
    files = []
    while 1:
        curr_files = os.listdir(sys.argv[1])
        new_files = [x for x in curr_files if x not in files and
                     any([x.endswith(ext) for ext in APPROVED_EXTENSIONS])]
        if len(new_files) >= 2:
            process_images(new_files[0], new_files[1])
            files += new_files[:2]
        print (new_files)
        time.sleep(SLEEPTIME)
