
import requests
from random import randint
import urllib.parse
import datetime


#Change this to the Access point that we are going to use in Production

URL_SERVICE = 'https://kkzqqs6qiqbstcyhinspection-ba-srv.cfapps.eu10.hana.ondemand.com/odata/v2/DatabaseServices'

# Entry Points for tables
PRODUCT_END_POINT = 'Products'

IMAGE_END_POINT = 'Images'

PRODUCT_DEFECT_END_POINT = 'Products_Defects'


# Dictionary wich maps the name of a defect to its corresponding ID in the database, this will be stored in the
# database separately through a csv file . 

# Feel free to modify the key texts to the ones you use in the ML service


# Headers to set the response as a json format
DEFAULT_HEADERS={"Content-Type":"application/json", "Accept":"application/json"}

# Parameters to send to the get petition to obtain the current max id
PARAMS_MAX_ID = urllib.parse.urlencode({
	'$select':'ID',
	'$orderby':"ID desc",
	'$top':1
}, quote_via=urllib.parse.quote)


class DBClient:
	def __init__(self, skey):
		self.skey = skey
	"""
		Obtains from the json response the max id
		Returns the next in the sequence
	"""
	def getNextID(self, json):
		if len(json['d']['results'])==0:
			return 1
		else:
			return json['d']['results'][0]['ID']+1

	"""
	Interface to insert info of the product. Note that the date must be in the format 2019-06-20T17:49:12.536Z
	Returns the service response and the newly generated product ID
	"""
	def insertProduct(self, capture_date, factoryID=randint(0,3)):
		access_point = '{base_service}/{end_point}'.format(base_service=URL_SERVICE,end_point=PRODUCT_END_POINT)

		r = requests.get(access_point, headers=DEFAULT_HEADERS, params=PARAMS_MAX_ID)

		ID = self.getNextID(r.json())

		body = {
			'ID':ID,
			'capture_date':capture_date,
			'factory_ID': factoryID
		}

		r = requests.post(access_point, json=body, headers=DEFAULT_HEADERS)

		if r.status_code!=201:
			print(r.json())
			raise RuntimeError("Error in Webservice")
		return r.json(), ID

	"""
	Interface to insert info of the image.
	Returns the service response
	"""
	def insertImage(self, productID, image_storage_path):
		access_point = '{base_service}/{end_point}'.format(base_service=URL_SERVICE,end_point=IMAGE_END_POINT)
		
		r = requests.get(access_point, headers=DEFAULT_HEADERS, params=PARAMS_MAX_ID)

		ID = self.getNextID(r.json())

		body = {
			'ID': ID,
			'url':image_storage_path,
			'product_ID':productID,
		}

		r = requests.post(access_point, json=body, headers=DEFAULT_HEADERS)

		if r.status_code!=201:
			print(r.json())
			raise RuntimeError("Error in Webservice")
		return r.json()


	"""
	Interface to insert info of the product and defect relationship.
	Returns the service response
	"""
	def insertProductsDefects(self, productID, defectID):
		access_point = '{base_service}/{end_point}'.format(base_service=URL_SERVICE,end_point=PRODUCT_DEFECT_END_POINT)

		r = requests.get(access_point, headers=DEFAULT_HEADERS, params=PARAMS_MAX_ID)

		ID = self.getNextID(r.json())

		body = {
			'ID':ID,
			'product_ID':productID,
			'defect_ID':defectID

		}

		r = requests.post(access_point, json=body, headers=DEFAULT_HEADERS)

		if r.status_code!=201:
			print(r.json())
			raise RuntimeError("Error in Webservice")
		return r.json()

    
	"""
	Interface to insert info of the product and defect relationship.
	Returns the service response
	"""
	def saveMachineLearningResult(self, imageInfo, productExists=False):
        try:
            date = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")
            
            newProduct, newProductID = self.insertProduct(date)
            
            imageStoragePath1 = imageInfo['image1']

            imageStoragePath2 = imageInfo['image2']

            self.insertImage(productID=newProductID,image_storage_path=imageStoragePath1)
            self.insertImage(productID=newProductID,image_storage_path=imageStoragePath2)
            
            #Here change to the model tested
            
            if not imageInfo['defects']:
                newProdDefRel = self.insertProductsDefects(productID=newProductID, defectID=0)
            else:
                for defect in imageInfo['defects']:
                    defectID = defect.value
                    newProdDefRel = self.insertProductsDefects(productID=newProductID, defectID=defectID)

            print("New register inserted succesfully")
            return True
        except RuntimeError:
            print("Register Insertion has failed")
            
            return False




client = DBClient("dummy")

client.saveMachineLearningResult(None)



