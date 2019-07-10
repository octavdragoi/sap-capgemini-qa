# test custom deployed model
import requests
import json
from enum import Enum


class DefectCode(Enum):
    NoDefect=6
    WrongProduct=5
    Scratch= 3
    Dent=4
    Stain=2
    Hole=1

# class automatically authorizes, on init
class MLFoundationClient:
    def __init__(self, skey, offline = False):
        self.skey = skey
        self.offline = offline
        if not self.offline:
            self.auth_header = self.authenticate(skey)

    # authentication gets the Bearer token. this runs automatically on init
    # so that future callbacks work as well
    def authenticate(self, skey):
        auth_url = "{}/oauth/token?grant_type=client_credentials".format(skey["url"])
        r = requests.get(auth_url, auth = (skey["clientid"], skey["clientsecret"]))
        if r.status_code != 200:
            print (r.text)
            raise RuntimeError("Authentication failed!")
        auth_header = {"Authorization" : "Bearer " + r.json()["access_token"]}
        return auth_header

    # these details should be plugged in MinIO for the data upload and training part
    def getDataEndpoint(self):
        url = "{}/api/v2/image/retraining/storage".format(
                self.skey["serviceurls"]["JOB_SUBMISSION_API_URL"])
        r = requests.get(url, headers = self.auth_header)
        return r.json()

    # this runs the custom deployed model. upload an image and get back the prediction results
    def modelPredict(self, image_path, model_name, version = 1):
        url = "{}/models/{}/versions/{}".format(
                self.skey["serviceurls"]["IMAGE_CLASSIFICATION_URL"],
                model_name, version)
        files = {'files' : open(image_path, 'rb')}
        r = requests.post(url, files = files, headers = self.auth_header)
        return r.json()
    
    #parses the Result from a json
    def parseResult(self,json,label):
        print (json)
        if (json["predictions"][0]["results"][0]["label"]==label):
            return json["predictions"][0]["results"][0]["score"]
        else:
            return json["predictions"][0]["results"][1]["score"]
    
    
    
    #pass through one model and parse result
    
    def modelPredictOne(self, image, label, model, enum):
        defects = []
        if self.offline:
            return defects
        json = self.modelPredict(image,model)
        jsonScore = self.parseResult(json,label)        
        
        if ( jsonScore > 0.5 ):
            defects.append(enum)
        return defects

        
        
        
    #pass through all models
    def modelPredictAll(self, image):
        img=[]
        if self.offline:
            return img
        
        #WrongObjectModel
        wrongObject = self.modelPredict(image,"WrongObjectModel")
        wrongObjectScore = self.parseResult(wrongObject,"wrong_object")
        if ( wrongObjectScore > 0.5 ):
            img.append(DefectCode.WrongProduct)
    
        #WrongObject means it does not go through the other models
        if (not img):  
            #HoleModel
            hole = self.modelPredict(image,"HoleModel")
            holeScore = self.parseResult(hole, "hole")
            if (holeScore >0.5):
                img.append(DefectCode.Hole)

            #DentModel
            dent = self.modelPredict(image,"DentModel")
            dentScore = self.parseResult(dent,"dent")
            if (dentScore >0.5):
                img.append(DefectCode.Dent)

                        
            #StainModel
            stain = self.modelPredict(image,"StainModel")
            stainScore = self.parseResult(stain,"stain")
            if (stainScore >0.5):    
                img.append(DefectCode.Stain)

            #ScratchModel
            scratch = self.modelPredict(image,"ScratchModel")
            scratchScore = self.parseResult(scratch, "scratch")
            if (scratchScore >0.5):
                img.append(DefectCode.Scratch)
        
        return img
    
    '''
    #predicts 2 images
    
    def predictPair(self, path1, image1, path2, image2):
        img1= self.modelPredictAll(path1,image1)
        img2= self.modelPredictAll(path2,image2)
        
        pair= self.pairOfImages(img1,img2)
        return pair.convertToJSON()
    '''    
        
    # list all trained models
    def modelList(self):
        url = "{}/models".format(self.skey["serviceurls"]["IMAGE_RETRAIN_API_URL"])
        r = requests.get(url, headers = self.auth_header)
        return r.json()

    # list only deployed models
    def modelListDeployed(self):
        url = "{}/deployments".format(self.skey["serviceurls"]["IMAGE_RETRAIN_API_URL"])
        r = requests.get(url, headers = self.auth_header)
        return r.json()
    
    
    '''
    #Class of 1 Image
    class imageClassified:
    
    #Pair of Images that convert into JSON
    
    class pairOfImages:
        
        def __init__(self, image1, image2):
            self.image1=image1
            self.image2=image2
        
        def convertToJSON(self):
            x = {
                "image1":{
                    "path" : self.image1.image_path,
                    "defects" : self.image1.defects
                },
                "image2":{
                    "path" : self.image2.image_path,
                    "defects" : self.image2.defects
                }
                
            }
            
            
            return json.dumps(x)
    '''

