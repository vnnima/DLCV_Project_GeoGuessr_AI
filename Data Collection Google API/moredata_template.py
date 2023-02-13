import google_streetview.api
import google_streetview.helpers
from PIL import Image
from numpy import genfromtxt

"""Define number of pictures to download
Set source path for coordinate data in an csv file. Lat long should be separated by commas
Set path to determine where to save the files
Set a valid api key
"""
######################################################
###edit:
######################################################
num_pictures = 10  #choose number of pictures to download
source_path = r"F:\Users\basti\Documents\Goethe Uni\DLCV Projekt\valid_streetview.csv"
my_data = genfromtxt(source_path, delimiter=',')

path = r"D:\Projekt to split\Projekt\Folder 1\Folder8"

your_api_key = "your api key"

####################################################

####################################################

for j in range(num_pictures):

	lat = str(my_data[j+1,0])
	long = str(my_data[j+1,1])
	# Define parameters for street view api
	params = [{
		'size': '640x512', # max 640x640 pixels
		'location': lat+","+long,
		'fov':'90',
		'heading': '0',
		'pitch': '0',
		'key': your_api_key
		},
		{
		'size': '640x512', # max 640x640 pixels
		'location': lat+","+long,
		'fov':'90',
		'heading': '90',
		'pitch': '0',
		'key': your_api_key
		},
		{
		'size': '640x512', # max 640x640 pixels
		'location': lat+","+long,
		'fov':'90',
		'heading': '180',
		'pitch': '0',
		'key': your_api_key
		},
		{
		'size': '640x512', # max 640x640 pixels
		'location': lat+","+long,
		'fov':'90',
		'heading': '270',
		'pitch': '0',
		'key': your_api_key
		}]


	# Create a results object
	results = google_streetview.api.results(params)

	# Download images to directory 'downloads'
	results.download_links('downloads')

	new_image = Image.new('RGB',(2560, 512), (250,250,250))
	for i in range(4):
		new_image.paste(Image.open('downloads/gsv_'+str(i)+'.jpg'),(640*i,0))
	new_image.save(path+"\img_"+lat+","+long+".jpg","JPEG")