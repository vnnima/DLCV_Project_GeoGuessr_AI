import torch
import torch.nn as nn
from torch.utils.data import DataLoader
from tqdm.notebook import tnrange



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
            - use_amp (bool)
                  Allows switching between default precision and mixed precision without
                  [Default: True]

        """
        self.model = model

        # Train on the GPU if possible.
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

        # Store training and validation data.
        self.data_train = data['train']
        self.data_val = data['val']

        # Define default values for parameters.
        defaults = {
            'loss': 'CrossEntropyLoss',
            'loss_config': {},
            'optimizer': 'SGD',
            'optimizer_config': {'lr': 1e-2},
            'batch_size': 128,
            'num_train_samples': 1000,
            'num_val_samples': None,
            'scheduler': None,
            'scheduler_config': {},
            'use_amp' : True
        }

        # Get given argument or take default value.
        values = defaults | kwargs

        # Create loss function.
        loss = getattr(nn, values.pop('loss'))
        self.loss = loss(**values.pop('loss_config'))

        # Create optimizer.
        optimizer = getattr(torch.optim, values.pop('optimizer'))
        self.optimizer = optimizer(model.parameters(), **values.pop('optimizer_config'))

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
        ###########################################################
            
        dataloader = DataLoader(dataset, batch_size=self.batch_size, num_workers=4) 
        correct = 0
        i = 0
        total = len(dataloader.dataset)
        with torch.no_grad():
            for data in dataloader:
                inputs, labels = data
                # Compute the ouputs (forward pass)
                outputs = self.model(inputs)
                # Get the predicted label
                pred = torch.max(outputs.data, 1)[1]
                # Count the number of correct predictions
                correct += (pred == labels).sum().item()
                
                # If we reach num_samples we break out
                if not num_samples is None:
                    if i >= num_samples:
                        break
        
        accuracy = 100 * correct / total

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

        scaler = torch.cuda.amp.GradScaler(enabled=self.use_amp)
        dataloader = torch.utils.data.DataLoader(
            self.data_train,
            batch_size=self.batch_size,
            shuffle=True
        )
        
        for epoch in (pbar := tnrange(self.num_epochs)): #
            running_loss = 0
            
            for i, batch in enumerate(dataloader, 0):
                with torch.autocast(device_type='cuda', dtype=torch.float16, enabled=self.use_amp):
                    # Convert images (input) to float because it is a ByteTensor. Why is it a ByteTensor?
                    inputs, labels = batch["image"].float(), batch["geohash"].float()

                    # Move the data to the device
                    inputs = inputs.to(self.device)
                    labels = labels.to(self.device)
                    
                    # Perform the forward pass
                    outputs = self.model(inputs)

                    # Compute the loss with the given loss function
                    loss = self.loss(outputs, labels)

                # Reset the gradients to zero for every batch
                self.optimizer.zero_grad()
                
                # Perform the backward pass
                scaler.scale(loss).backward()
                
                # Update the weights using the gradient computed in the backward pass
                scaler.step(self.optimizer)
                
                scaler.update()

                running_loss += loss.item()
            
            self.epoch += 1
            self.loss_history.append(running_loss / len(dataloader))
            
            # Store the train and validation accuarcy for every epoch
            train_accuracy = self.test(self.data_train)
            self.train_acc.append(train_accuracy)
            
            val_accuracy = self.test(self.data_val, self.num_val_samples)
            self.val_acc.append(val_accuracy)
            
            # Check if this is the best accuarcy we have seen so far
            if val_accuracy >= max(self.val_acc):
                self.save("./models/best_model.pt")
                
            
            self.scheduler.step()
            
            pbar.set_description(f'Epoch: {self.epoch}  Val. Accuracy: {val_accuracy:.5f}')
        
        # Load the best model
        self.load("./models/best_model.pt")
        

        ############################################################
        ###                   END OF YOUR CODE                   ###
        ############################################################
        return {
            'loss': self.loss_history,
            'train_acc': self.train_acc,
            'val_acc': self.val_acc
        }


