"""
The formular for determining the points is score = 5000 * exp(-distance / sigma) where sigma is a factor
of the size of the map in comparison to the whole world times 2000. Standard for sigma is therefore 2000.

Avg dist 4000: ~676P
Avg dist 3000: ~1115P
Avg dist 2000: ~1840P 
Avg dist 1500: ~2361P
Avg dist 1000: ~3032P
Avg dist 500: ~3894P
Avg dist 440: ~4012P
"""

import torch
from math import radians, cos, sin, asin, sqrt

class GeoGuessrLoss(torch.nn.Module):
    def __init__(self):
        super(GeoGuessrLoss, self).__init__();

    def forward_old(self, predictions, target):
        # https://www.geeksforgeeks.org/program-distance-two-points-earth/
        # Dlat = lat_pred - lat_tar
        lat_pred = torch.deg2rad(torch.max(torch.min(predictions[:, 0], 90*torch.ones_like(predictions[:, 0])), -90*torch.ones_like(predictions[:, 0])))
        lon_pred = torch.deg2rad(torch.max(torch.min(predictions[:, 1], 180*torch.ones_like(predictions[:, 1])), -180*torch.ones_like(predictions[:, 1])))
        dlat = torch.deg2rad(torch.max(torch.min(target[:, 0], 90*torch.ones_like(target[:, 0])), -90*torch.ones_like(target[:, 0]))) - lat_pred
        dlon = torch.deg2rad(torch.max(torch.min(target[:, 1], 180*torch.ones_like(target[:, 1])), -180*torch.ones_like(target[:, 1]))) - lon_pred
        

        #print("L_pred:", lon_pred[0], lat_pred[0])
        #print("L_tar:", lon_tar[0], lat_tar[0])
        #print("D: ", dlon[0], dlat[0])
        a = torch.pow(torch.sin(dlat / 2),2) + torch.cos(lat_pred) * torch.cos(lon_pred) * torch.pow(torch.sin(dlon / 2),2)
        a = torch.sqrt(torch.abs(a)) # EPSILON is needed, so that a is not zero
        a = 2 * torch.arcsin(torch.max(torch.min(a, torch.ones_like(dlon)), - torch.ones_like(dlon)))  # Result between 1 and -1
        #print(loss)

        loss_value = torch.mean(6371 * a)
        return loss_value
    
    def forward(self, predictions, target):
        # https://www.movable-type.co.uk/scripts/latlong.html
        lat_pred = predictions[:,0] * torch.pi/180
        lat_tar = target[:,0] * torch.pi/180
        dlat = (target[:,0] - predictions[:,0]) * torch.pi/180
        dlon = (target[:,1] - predictions[:,1]) * torch.pi/180

        a = torch.sin(dlat/2) * torch.sin(dlat/2) + torch.cos(lat_pred) * torch.cos(lat_tar) * torch.sin(dlon/2) * torch.sin(dlon/2)
        c = 2 * torch.atan2(torch.sqrt(a), torch.sqrt(1 - a))

        d = c * 6371
        loss_value = torch.mean(d)
        return loss_value