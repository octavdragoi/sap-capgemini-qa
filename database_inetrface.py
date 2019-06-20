
import requests

#Change this to the Access point that we are going to use in Production

URL_SERVICE = 'https://kkzqqs6qiqbstcyhinspection-ba-srv.cfapps.eu10.hana.ondemand.com/odata/v2/DatabaseServices'

# Entry Points for tables
PRODUCT_END_POINT = 'Products'

IMAGE_END_POINT = 'Images'

PRODUCT_DEFECT_END_POINT = 'Products_Defects'


# Dictionary wich maps the name of a defect to its corresponding ID in the database, this will be stored in the
# database separately through a csv file . 

# Feel free to modify the key texts to the ones you use in the ML service

DEFECTS_CODE ={
	
	'No Defect':0,
	'Wrong Product':1,
	'Scratch': 2,
	'Dent': 3,
	'Stain': 4,
	'Hole': 5
}

#class DBClient:

def insertImageInfo(image_storage_path):
	access_point = '{base_service}/{end_point}'.format(base_service=URL_SERVICE,end_point=IMAGE_END_POINT)

	r = requests.get(access_point, params={'select':'ID'})

	print(r.text)

	body = {
		'ID':34,
		'url':image_storage_path
	}

	r = requests.post(access_point, json=body)

	if r.status_code!=201:
		print(r.status_code)
		raise RuntimeError("Error in Webservice")
	return r.text





print(insertImageInfo('someURL'))