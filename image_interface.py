import requests

URL_SERVICE = "https://quality-assurance-image-service.cfapps.eu10.hana.ondemand.com"

class ImageDBClient:
    def __init__(self):
        pass

    # returns the code to the newly created image
    def upload(self, image_path):
        files = {'image' : open(image_path, 'rb')}
        r = requests.post(URL_SERVICE, files = files)
        if r.status_code != 201:
            print (r.text)
            raise RuntimeError("Upload failed!")
        return r.text

    # returns the image in binary form, from the request
    def download(self, image_id):
        r = requests.get(URL_SERVICE, params = {"key" : image_id})
        if r.status_code != 200:
            print (r.text)
            raise RuntimeError("Download failed!")
        return r.content
