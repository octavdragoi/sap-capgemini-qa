# test custom deployed model
import requests

# class automatically authorizes, on init
class MLFoundationClient:
    def __init__(self, skey):
        self.skey = skey
        self.auth_header = self.authenticate(skey)

    def authenticate(self, skey):
        auth_url = "{}/oauth/token?grant_type=client_credentials".format(skey["url"])
        r = requests.get(auth_url, auth = (skey["clientid"], skey["clientsecret"]))
        if r.status_code != 200:
            raise RuntimeError("Authentication failed!")
        auth_header = {"Authorization" : "Bearer " + r.json()["access_token"]}
        return auth_header

    # this runs the custom deployed model. upload an image and get back the prediction results
    def model_predict(self, image_path, model_name, version = 1):
        url = "{}/models/{}/versions/{}".format(self.skey["serviceurls"]["IMAGE_CLASSIFICATION_URL"],
                                               model_name, version)
        files = {'files' : open(image_path, 'rb')}
        r = requests.post(url, files = files, headers = self.auth_header)
        return r.json()

    def model_list_deployed(self):
        url = "{}/deployments".format(self.skey["serviceurls"]["IMAGE_RETRAIN_API_URL"])
        r = requests.get(url, headers = self.auth_header)
        return r.json()
