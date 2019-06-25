# test custom deployed model
import requests
import json

# class automatically authorizes, on init
class MLFoundationClient:
    def __init__(self, skey):
        self.skey = skey
        self.auth_header = self.authenticate(skey)

    # authentication gets the Bearer token. this runs automatically on init
    # so that future callbacks work as well
    def authenticate(self, skey):
        auth_url = "{}/oauth/token?grant_type=client_credentials".format(skey["url"])
        r = requests.get(auth_url, auth = (skey["clientid"], skey["clientsecret"]))
        if r.status_code != 200:
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
    
    #pass through all models
    def modelPredictAll(self, image_path, image):
        img= self.imageClassified(image_path)
       
        
        #WrongObjectModel
        wrongObject = self.modelPredict(image,"WrongObjectModel")
        if (wrongObject["predictions"][0]["results"][0]["label"]=="right_object"):
            img.wrongObject_score = wrongObject["predictions"][0]["results"][0]["score"]
        else:
            img.wrongObject_score = wrongObject["predictions"][0]["results"][1]["score"]
        if (img.wrongObject_score >0.5):
            img.defects = []
        else:
            img.defects = ["Wrong Object"]
        
        
        #WrongObject means it does not go through the other models
        if (not img.defects):  
            #HoleModel
            hole = self.modelPredict(image,"HoleModel")
            if (hole["predictions"][0]["results"][0]["label"]=="hole"):
                img.hole_score = hole["predictions"][0]["results"][0]["score"]
            else:
                img.hole_score = hole["predictions"][0]["results"][1]["score"]
            if (img.hole_score >0.5):
                img.defects.append("Hole")

            #DentModel
            dent = self.modelPredict(image,"DentModel")
            if (dent["predictions"][0]["results"][0]["label"]=="dent"):
                img.dent_score = dent["predictions"][0]["results"][0]["score"]
            else:
                img.dent_score = dent["predictions"][0]["results"][1]["score"]
            if (img.dent_score >0.5):
                img.defects.append("Dent")

            
            
            #StainModel
            stain = self.modelPredict(image,"StainModel")
            if (stain["predictions"][0]["results"][0]["label"]=="stain"):
                img.stain_score = stain["predictions"][0]["results"][0]["score"]
            else:
                img.stain_score = stain["predictions"][0]["results"][1]["score"]
            if (img.stain_score >0.5):    
                img.defects.append("Stain")


            #ScratchModel
            scratch = self.modelPredict(image,"ScratchModel")
            if (scratch["predictions"][0]["results"][0]["label"]=="scratch"):
                img.scratch_score = scratch["predictions"][0]["results"][0]["score"]
            else:
                img.scratch_score = scratch["predictions"][0]["results"][1]["score"]
            if (img.scratch_score >0.5):
                img.defects.append("Scratch")
        
        return img
    
    #predicts 2 images

    def predictPair(self, path1, image1, path2, image2):
        img1= self.modelPredictAll(path1,image1)
        img2= self.modelPredictAll(path2,image2)
        
        pair= self.pairOfImages(img1,img2)
        return pair.convertToJSON()
        
        
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
    
    
    
    #Class of 1 Image
    class imageClassified:
        def __init__(self, image_path):
            self.image_path = image_path
    
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


