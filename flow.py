#!/usr/bin/env python3

from keys import ml_servicekey_wrongobject, ml_servicekey_hole, ml_servicekey_dent
from ml_interface import MLFoundationClient, DefectCode
from database_interface import DBClient
from image_interface import ImageDBClient
import os
import sys
import time
from PIL import Image
import functools

# parameters for the global script
SLEEPTIME = 2 # seconds
APPROVED_EXTENSIONS = [".jpg", ".jpeg"]
STANDARD_IMG_SIZE = (1440, 1920)

exif_orientation_tag = 0x0112
exif_transpose_sequences = [                   # Val  0th row  0th col
    [],                                        #  0    (reserved)
    [],                                        #  1   top      left
    [Image.FLIP_LEFT_RIGHT],                   #  2   top      right
    [Image.ROTATE_180],                        #  3   bottom   right
    [Image.FLIP_TOP_BOTTOM],                   #  4   bottom   left
    [Image.FLIP_LEFT_RIGHT, Image.ROTATE_90],  #  5   left     top
    [Image.ROTATE_270],                        #  6   right    top
    [Image.FLIP_TOP_BOTTOM, Image.ROTATE_90],  #  7   right    bottom
    [Image.ROTATE_90],                         #  8   left     bottom
]

def resize_image(img_path):
    """"
    This function checks if the image is of the right size, and if not, it resizes
    it. It also overwrites the original picture, so make sure you have a backup
    somewhere else!
    """
    img = Image.open(img_path)
    if img.size != STANDARD_IMG_SIZE:
        print ("Image size {} differs from standard {}, resizing...".format(
            img.size, STANDARD_IMG_SIZE))
        try:
            seq = exif_transpose_sequences[img._getexif()[exif_orientation_tag]]
        except Exception:
            pass
        else:
            img = functools.reduce(type(img).transpose, seq, img)
        img.thumbnail(STANDARD_IMG_SIZE, Image.ANTIALIAS)
        img.save(img_path, "JPEG")

def process_image_ml(img_path):
    defectWrongObject = clientWrongObject.modelPredictOne(
            img_path, "wrong_object","WrongObjectModel", DefectCode.WrongProduct)
    if (not defectWrongObject):
        defectHole = clientHole.modelPredictOne(
                img_path, "hole","HoleModel", DefectCode.Hole)
        defectDent = clientDent.modelPredictOne(
                img_path, "dent","DentModel", DefectCode.Dent)
        defects = [defectWrongObject, defectHole, defectDent]
    else:
        defects = [defectWrongObject]
    return [x[0] for x in defects if len(x) > 0]

def process_images(img_path, img_path2):
    # open the images
    # img = open(img_path, "rb")
    # img2 = open(img_path2, "rb")

    # resize images
    resize_image(img_path)
    resize_image(img_path2)

    # get the keys for the image uploading
    key = im_client.upload(img_path)
    key2 = im_client.upload(img_path2)

    # call the ML models
    defects_lst = process_image_ml(img_path)
    defects_lst2 = process_image_ml(img_path2)
    defects = list(set(defects_lst + defects_lst2))

    #make the json
    imageInfo= {
        'image1' : key,
        'image2' : key2,
        'defects' : defects
    }
    print(imageInfo)

    db_client.saveMachineLearningResult(imageInfo)

    # remove the files after upload
    os.remove(img_path)
    os.remove(img_path2)



db_client = DBClient()
#ml_client = MLFoundationClient(ml_key, offline = True)
im_client = ImageDBClient()
clientWrongObject = MLFoundationClient(ml_servicekey_wrongobject)
clientHole = MLFoundationClient(ml_servicekey_hole)
clientDent = MLFoundationClient(ml_servicekey_dent)

if __name__ == "__main__":
    """
    Start the main program loop.
    Run in terminal as "./flow.py <input_dir>".
    The script will watch over the directory, and when it sees two new images
    it will run the whole algorithm.
    """
    files = []
    while 1:
        curr_files = os.listdir(sys.argv[1])
        new_files = [x for x in curr_files if x not in files and
                     any([x.endswith(ext) for ext in APPROVED_EXTENSIONS])]
        if len(new_files) >= 2:
            process_images(
                    os.path.join(sys.argv[1], new_files[0]),
                    os.path.join(sys.argv[1], new_files[1]))
            files += new_files[:2]
        else:
            time.sleep(SLEEPTIME)
        print (new_files)
