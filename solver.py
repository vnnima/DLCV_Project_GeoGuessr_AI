#Bastian Rothenburger
import torch
import torch.nn as nn
from torch.utils.data import DataLoader
from tqdm.notebook import tnrange
from haversine import haversine


class Solver:
    
    def __init__(self, model, data, **kwargs):
        """
        Creates a solver for classification.

        Parameters:
            - model (nn.Module):
                  Model to be trained.
            - data (dict):
                  Training and validation datasets.
                  Dictionary with keys `train` for training set and `val` for validation set.
            - loss (str):
                  Class name of the loss function to be optimized.
                  [Default: 'CrossEntropyLoss']
            - loss_config (dict|None):
                  Dictionary with keyword arguments for calling the loss function.
                  [Default: {}]
            - optimizer (str):
                  Class name of the optimizer to be used.
                  [Default: 'SGD']
            - optimizer_config (dict):
                  Dictionary with keyword arguments for calling for the optimizer.
                  Model parameters don't have to be passed explicitly.
                  [Default: {'lr': 1e-2}]
            - batch_size (int):
                  Number of samples per minibatch.
                  [Default: 128]
            - num_train_samples (int):
                  Number of training samples to be used for evaluation.
                  [Default: 1000]
            - num_val_samples (int|None):
                  Number of validation samples to be used for evaluation.
                  If parameter is `None`, all samples in the given validation set are used.
                  [Default: None]
            - scheduler (str|None):
                  Class name of the learning rate scheduler to be used.
                  If parameter is not given or `None`, no scheduler is used.
                  [Default: None]
            - scheduler_config (dict):
                  Dictionary with keyword arguments to provide for the scheduler.
                  The optimizer is passed in automatically.
                  [Default: {}]

        """
        self.model = model

        # Train on the GPU if possible.
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        print(self.device)
        # Store training and validation data.
        self.data_train = data['train']
        self.data_val = data['val']

        # Define default values for parameters.
        defaults = {
            'loss': 'CrossEntropyLoss',
            'loss_config': {},
            'optimizer': 'SGD',
            'optimizer_params': {'lr': 1e-2},
            'batch_size': 2,
            'num_train_samples': 1000,
            'num_val_samples': None,
            'scheduler': None,
            'scheduler_config': {}
        }

        # Get given argument or take default value.
        values = defaults | kwargs

        # Create loss function.
        loss = getattr(nn, values.pop('loss'))
        self.loss = loss(**values.pop('loss_config'))

        # Create optimizer.
        optimizer = getattr(torch.optim, values.pop('optimizer'))
        self.optimizer = optimizer(model.parameters(), **values.pop('optimizer_params'))

        # Scheduler is optional.
        self.scheduler = values.pop('scheduler')

        # Create scheduler if necessary.
        if self.scheduler:
            scheduler = getattr(torch.optim.lr_scheduler, self.scheduler)
            self.scheduler = scheduler(self.optimizer, **values.pop('scheduler_config'))

        # Store remaining arguments.
        self.__dict__ |= values

        # Some attributes for bookkeeping.
        self.epoch = 0
        self.num_epochs = 0
        self.loss_history = []
        self.train_acc = []
        self.val_acc = []


    def save(self, path):
        """
        Save model and training state to disk.

        Parameters:
            - path (str): Path to store checkpoint.

        """
        checkpoint = {
            'model': self.model.state_dict(),
            'optimizer': self.optimizer.state_dict(),
            'epoch': self.epoch,
            'num_epochs': self.num_epochs,
            'loss_history': self.loss_history,
            'train_acc': self.train_acc,
            'val_acc': self.val_acc
        }

        # Save learning rate scheduler state if defined.
        if self.scheduler:
            checkpoint['scheduler'] = self.scheduler.state_dict()

        # Save checkpoint to disk.
        torch.save(checkpoint, path)


    def load(self, path):
        """
        Load checkpoint from disk.

        Parameters:
            - path (str): Path to checkpoint.

        """
        checkpoint = torch.load(path)

        # Load model and optimizer state.
        self.model.load_state_dict(checkpoint.pop('model'))
        self.optimizer.load_state_dict(checkpoint.pop('optimizer'))

        # Load learning rate scheduler state if defined.
        if self.scheduler:
            self.scheduler.load_state_dict(checkpoint.pop('scheduler'))

        # Load the remaining attributes.
        self.__dict__ |= checkpoint


    def test(self, dataset, num_samples=None):
        """
        Compute the accuracy of the model.

        Takes an optional parameter that allows to specify the
        number of samples to use for testing. If not given the
        whole dataset is used.

        Parameters:
            - dataset (torch.Tensor): Dataset for testing.
            - num_samples (int|None): Number of data points to use from dataset.

        Returns:
            - accuracy (float): Percentage of correct predictions.

        """
        self.model.to(self.device)
        self.model.eval()
        ############################################################
        ###                  START OF YOUR CODE                  ###
        ############################################################
        #random sampling variant from machine learning one
        dataset_size = len(dataset)
        if num_samples is not None and num_samples < dataset_size:
            dataset, _ =torch.utils.data.random_split(dataset, [num_samples,dataset_size - num_samples])
        #use data loader as in the example provided above
        dataloader = torch.utils.data.DataLoader(
            dataset,
            batch_size=self.batch_size,
            shuffle=False
        )
        
        total = 0
        correct = 0
        #dont calculate gradients
        with torch.no_grad():
            #treat labels ands inputs seperatly 
            for i, (inputs, labels) in enumerate(dataloader):
                #put relevant stuff to cuda (if available)
                inputs = inputs.to(self.device)
                labels = labels.to(self.device)
                #compute forward pass
                outputs = self.model(inputs)
                #find prdiction by highest score
                predicted = torch.argmax(outputs.data, 1)
                #keep track of prediction performance

                #l= havers(centroid[predicted], ground_tru[input]
                total += labels.size(0)
                correct += (predicted == labels).sum().item()
        #evaluate accuracy         
        accuracy = 100* correct/total

        ############################################################
        ###                   END OF YOUR CODE                   ###
        ############################################################
        self.model.train()

        return accuracy


    def train(self, num_epochs=10):
        """
        Train the model for given number of epochs.

        Parameters:
            - num_epochs (int): Number of epochs to train.

        Returns:
            - history (dict):
                - loss: Training set loss per epoch.
                - train_acc: Training set accuracy per epoch.
                - val_acc: Validation set accuracy per epoch.

        """
        self.model.to(self.device)
        self.num_epochs += num_epochs
        ############################################################
        ###                  START OF YOUR CODE                  ###
        ############################################################
        
        #dataloader as in example
        dataloader = torch.utils.data.DataLoader(
            self.data_train,
            batch_size=self.batch_size,
            shuffle=True
        )
        #init best accuracy
        best_val_acc = 0
        best_params = None
        #show training progress
        """for epoch in (pbar := tnrange(num_epochs)): 
            self.epoch += 1
            #for gpu?
            #loss_history = torch.empty(len(dataloader))
            loss_history = []"""
        loss_history = []           
            #self.model.train()
        for i, müll in enumerate(dataloader):
            torch.cuda.empty_cache()
            inputs = müll['image'].to(self.device)
            labels = müll['cluster'].long().to(self.device)
            print('was soll der mist')    
                #forward pass
            outputs = self.model(inputs)

                #loss and gradient computation
            loss = self.loss(outputs, labels)
            loss.backward()
                
                #update parameters 
            self.optimizer.step()
            self.optimizer.zero_grad()
                
            
                #store loss history
            loss_history.append(loss.item())
            torch.cuda.empty_cache()
            

        self.loss_history.append(sum(loss_history)/i)

            #see training accuracy and store it
        train_acc =self.test(self.data_train, num_samples=self.num_train_samples)
        self.train_acc.append(train_acc)
            #see validation accuracy and store it
        val_acc =self.test(self.data_val, num_samples=self.num_val_samples)
        self.val_acc.append(val_acc)
            
            #apply scheduler if given
        if self.scheduler is not None:
            self.scheduler.step()
        
        #track loss history per epoch
        train_loss = torch.mean(loss_history).item()
        self.loss_history.append(train_loss)
            
            #safe the model if it is better than previous one
        if val_acc>best_val_acc:
            best_val_acc = val_acc
            self.save("./models/bestmodel")
        #pbar.set_description(f'Validation accuracy: {val_acc:5.2f}%')
    
        #initalize best model
        
        self.load("./models/bestmodel")
               
                           

        ############################################################
        ###                   END OF YOUR CODE                   ###
        ############################################################
        return {
            'loss': self.loss_history,
            'train_acc': self.train_acc,
            'val_acc': self.val_acc
        }



def haversine(pred_cent:tuple, ground_tru: tuple):

  """
  Calculate the Haversine distance between two coordinates.
  
  Args:
    coord1 (tuple): The first coordinate, given as a tuple of (latitude, longitude).
    coord2 (tuple): The second coordinate, given as a tuple of (latitude, longitude).
  
  Returns:
    float: The Haversine distance between the two coordinates, in kilometers.
  """
  return haversine(pred_cent, ground_tru)


def haversine_backward(pred, target):
  """
  Calculate the gradients of the Haversine distance loss with respect to the predicted coordinates.
  
  Args:
    pred (torch.Tensor): The predicted coordinates, given as a tensor of shape (batch_size, 2).
    target (torch.Tensor): The target coordinates, given as a tensor of shape (batch_size, 2).
  
  Returns:
    torch.Tensor: The gradients of the Haversine distance loss with respect to the predicted coordinates, given as a tensor of shape (batch_size, 2).
  """
  # Convert the predicted and target coordinates to radians
  pred_rad = torch.deg2rad(pred)
  target_rad = torch.deg2rad(target)
  
  # Calculate the Haversine distance between the predicted and target coordinates
  lat1, lon1 = pred_rad[:, 0], pred_rad[:, 1]
  lat2, lon2 = target_rad[:, 0], target_rad[:, 1]
  a = torch.sin((lat2 - lat1) / 2)**2 + torch.cos(lat1) * torch.cos(lat2) * torch.sin((lon2 - lon1) / 2)**2
  c = 2 * torch.atan2(torch.sqrt(a), torch.sqrt(1 - a))
  distance = 6371 * c  # 6371 is the radius of the Earth in kilometers
  
  # Calculate the gradients of the Haversine distance loss with respect to the predicted coordinates
  grads = torch.zeros_like(pred)
  grads[:, 0] = (torch.cos(lat2) * torch.sin(lon2 - lon1) - torch.sin(lat2) * torch.cos(lat1) * torch.cos(lon2 - lon1)) / torch.sqrt(1 - a)
  grads[:, 1] = (torch.cos(lat1) * torch.sin(lat2) - torch.sin(lat1) * torch.cos(lat2) * torch.cos(lon2 - lon1)) / torch.sqrt(1 - a)
  
  return grads
