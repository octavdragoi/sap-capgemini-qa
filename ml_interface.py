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
    def get_data_endpoint(self):
        url = "{}/api/v2/image/retraining/storage".format(
                self.skey["serviceurls"]["JOB_SUBMISSION_API_URL"])
        r = requests.get(url, headers = self.auth_header)
        return r.json()

    # this runs the custom deployed model. upload an image and get back the prediction results
    def model_predict(self, image_path, model_name, version = 1):
        url = "{}/models/{}/versions/{}".format(
                self.skey["serviceurls"]["IMAGE_CLASSIFICATION_URL"],
                model_name, version)
        files = {'files' : open(image_path, 'rb')}
        r = requests.post(url, files = files, headers = self.auth_header)
        return r.json()
    
    #pass through all models
    def model_predict_all(self, image_path):
        img= self.imageClassified(image_path)
        
        #WrongObjectModel
        wrongObject = self.model_predict(image_path,"WrongObjectModel")
        if (wrongObject["predictions"][0]["results"][0]["label"]=="right_object"):
            img.wrongObject_score = wrongObject["predictions"][0]["results"][0]["score"]
        else:
            img.wrongObject_score = wrongObject["predictions"][0]["results"][1]["score"]
        if (img.wrongObject_score >0.5):
            img.wrongObject = 0
        else:
            img.wrongObject = 1
        
        
        #WrongObject means it does not go through the other models
        if (img.wrongObject ==0):  
            #HoleModel
            hole = self.model_predict(image_path,"HoleModel")
            if (hole["predictions"][0]["results"][0]["label"]=="hole"):
                img.hole_score = hole["predictions"][0]["results"][0]["score"]
            else:
                img.hole_score = hole["predictions"][0]["results"][1]["score"]
            if (img.hole_score >0.5):
                img.hole = 1
            else:
                img.hole = 0
            #DentModel
            dent = self.model_predict(image_path,"DentModel")
            if (dent["predictions"][0]["results"][0]["label"]=="dent"):
                img.dent_score = dent["predictions"][0]["results"][0]["score"]
            else:
                img.dent_score = dent["predictions"][0]["results"][1]["score"]
            if (img.dent_score >0.5):
                img.dent = 1
            else:
                img.dent = 0
            #StainModel
            stain = self.model_predict(image_path,"StainModel")
            if (stain["predictions"][0]["results"][0]["label"]=="stain"):
                img.stain_score = stain["predictions"][0]["results"][0]["score"]
            else:
                img.stain_score = stain["predictions"][0]["results"][1]["score"]
            if (img.stain_score >0.5):
                img.stain = 1
            else:
                img.stain = 0

            #ScratchModel
            scratch = self.model_predict(image_path,"ScratchModel")
            if (scratch["predictions"][0]["results"][0]["label"]=="scratch"):
                img.scratch_score = scratch["predictions"][0]["results"][0]["score"]
            else:
                img.scratch_score = scratch["predictions"][0]["results"][1]["score"]
            if (img.scratch_score >0.5):
                img.scratch = 1
            else:
                img.scratch = 0
        else:
            img.scratch = 0
            img.dent = 0
            img.hole = 0
            img.stain = 0
            img.scratch_score = 0
            img.dent_score = 0
            img.hole_score = 0
            img.stain_score = 0
        
        return img
        

    # list all trained models
    def model_list(self):
        url = "{}/models".format(self.skey["serviceurls"]["IMAGE_RETRAIN_API_URL"])
        r = requests.get(url, headers = self.auth_header)
        return r.json()

    # list only deployed models
    def model_list_deployed(self):
        url = "{}/deployments".format(self.skey["serviceurls"]["IMAGE_RETRAIN_API_URL"])
        r = requests.get(url, headers = self.auth_header)
        return r.json()
    
    class imageClassified:
        def __init__(self, image_path):
            self.image_path = image_path
        
        def convertToJSON(self):
            if (self.stain + self.scratch + self.hole+ self.wrongObject + self.dent == 0):
                fine = 1
            else:
                fine = 0
            x = {
                "path": self.image_path,
                "WrongObject" : self.wrongObject,
                "Hole" : self.hole,
                "Dent" : self.dent,
                "Stain": self.stain,
                "Scrach": self.scratch      
            }
            return json.dumps(x)

