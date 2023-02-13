# source: https://github.com/k4yp/geosolvr/blob/main/data/data.py


import requests
import json
import random
import wget
import os
import pandas as pd




global_image_num = 0

class Colors:
    BOLD = '\033[1m'
    FAIL = '\033[91m'
    SUCCESS = '\033[92m'
    WARNING = '\033[93m'
    END = '\033[0m'

class Generate:
    def __init__(self, num_images, output_file, api_key, threads):
        self.num_images = num_images
        self.output_file = output_file
        self.api_key = api_key
        self.threads = threads

        # gets last index of a csv file
        
        global global_image_num

        

        epoch = 0

        while epoch < num_images:
            coordinates = self.random_coordinates()
            metadata = self.check_streetview(coordinates[0], coordinates[1])

            if metadata != False:
                lat = metadata['location']['lat']
                lng = metadata['location']['lng']

                

                print(f'{Colors.SUCCESS} progress [{round(((global_image_num) / (num_images * threads)) * 100, 1)}%]{Colors.END} streetview found in \n{lat},{lng}')
                
                global_image_num += 1

                

                with open(output_file, 'a') as f:
                    f.write(f'{lat},{lng}\n')
                
                epoch += 1

    # returns random coordinats -> List[float, float]  
    def random_coordinates(self):
        lat = random.uniform(-10, -45)
        lng = random.uniform(180, 112)

        return [lat, lng]

    # checks if streetview exists -> Dict or False
    def check_streetview(self, lat, lng):
        metadata = requests.get(f'https://maps.googleapis.com/maps/api/streetview/metadata?size=640x640&location={lat},{lng}&radius=4096&key={self.api_key}').text
        metadata = json.loads(metadata)

        if metadata['status'] == 'OK' and metadata['copyright'] == '© Google':
            return metadata

        return False
    
    

Generate(2000,r'F:\Users\basti\Documents\australia.csv',"your key",2)