#Bastian Rothenburger
import torch
import torch.nn as nn
import torch.nn.functional as F



class ResidualBlock(nn.Module):

    def __init__(self, in_channels, out_channels, stride=1):
        """
        Create residual block with two conv layers.

        Parameters:
            - in_channels (int): Number of input channels.
            - out_channels (int): Number of output channels.
            - stride (int): Stride for first convolution.

        """
        super().__init__()
        ############################################################
        ###                  START OF YOUR CODE                  ###
        ############################################################
        
        # layers as described in the task
        self.conv1 = nn.Conv2d(in_channels, out_channels, 3, padding=1,stride=stride, bias=False)
        self.conv2 = nn.Conv2d(out_channels,out_channels, 3, padding=1, stride=1, bias=False)
        self.skipconv = nn.Conv2d(in_channels, out_channels, 1,bias=False)
        self.spatialBatch1 = nn.BatchNorm2d(out_channels)
        self.spatialBatch2 = nn.BatchNorm2d(out_channels)

        ############################################################
        ###                   END OF YOUR CODE                   ###
        ############################################################


    def forward(self, x):
        """
        Compute the forward pass through the residual block.

        Parameters:
            - x (torch.Tensor): Input.

        Returns:
            - out (torch.tensor): Output.

        """
        ############################################################
        ###                  START OF YOUR CODE                  ###
        ############################################################
        
        # foward pass as described in the task
        #save skip for matching dimensions if needed
        skip = x
        x = F.relu(self.spatialBatch1(self.conv1(x)))
        x = self.spatialBatch2(self.conv2(x))
        
        #dimension mathing of skip connection if needed
        if x.shape != skip.shape:
            skip = self.skipconv(skip)
        x += skip 
                         
        out = F.relu(x)

        ############################################################
        ###                   END OF YOUR CODE                   ###
        ############################################################
        return out



class ResNet(nn.Module):

    def __init__(self):
        """
        Creates a residual network.
        """
        super().__init__()
        ############################################################
        ###                  START OF YOUR CODE                  ###
        ############################################################
        #params=3*3*3*3=81
        self.conv1 = nn.Conv2d(3, 3, 3, padding=1,stride=1, bias=False)
        #params=3*2=6
        self.spatialBatch1 = nn.BatchNorm2d(3)
        
        #params=3*10*3*3+10*10*3*3+10*2*2+3*10=1240
        self.Res2 = ResidualBlock(3,10)
        #params=10*14*3*3+14*14*3*3+14*2*2+10*14=3220
        self.Res3 = ResidualBlock(10,14)
        
        #params=14*38*3*3+38*38*3*3+38*2*2+14*38=18468
        self.Res6 = ResidualBlock(14,38)
        
        
        
        
        
        
        
        self.pool1 = nn.AvgPool2d(4)
        #params=2432*10+10=24330
        self.fc1 = nn.Linear(3112960, 100)
        ############################################################
        ###                   END OF YOUR CODE                   ###
        ############################################################


    def forward(self, x):
        """
        Compute the forward pass through the network.

        Parameters:
            - x (torch.Tensor): Input.

        Returns:
            - out (torch.Tensor): Output.

        """
        ############################################################
        ###                  START OF YOUR CODE                  ###
        ############################################################
        #some arichtecture
        x=F.relu(self.spatialBatch1(self.conv1(x)))
        
        x=self.Res2.forward(x)
        x=torch.nn.functional.dropout(x, p=0.1)
        x=self.Res3.forward(x)
        x=torch.nn.functional.dropout(x, p=0.2)
        
        
        x=self.Res6.forward(x)
        x=torch.nn.functional.dropout(x, p=0.4)
        
        
        
        x=self.pool1(x)
        
        x = torch.flatten(x, 1)
        x=self.fc1(x)
        
        out = x

        ############################################################
        ###                   END OF YOUR CODE                   ###
        ############################################################
        return out





