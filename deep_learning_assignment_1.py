# -*- coding: utf-8 -*-
"""Deep Learning Assignment 1.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1_TXy9kMMXmpmotoR6HlxAr8SvW4oBv8V
"""

#importing essential libraries

import numpy as np
import matplotlib.pyplot as plt
from sklearn.metrics import accuracy_score
from keras.datasets import fashion_mnist
from keras.utils import to_categorical

#loading the datasets

(x_training_set, y_training_set), (x_testing_set, y_testing_set) = fashion_mnist.load_data()

#storing different classes in a list

classes = ['T-shirt/top', 'Trouser', 'Pullover', 'Dress', 'Coat', 'Sandal', 'Shirt', 'Sneaker', 'Bag', 'Ankle boot']

#function definition to plot the one image from different classes

def plot_img(images, labels, classes):
  image_list = [] #list to store one image from each class
  class_num = len(classes)

  for i in range(class_num):
    indx = np.where(labels == i)[0][0]
    image_list.append(images[indx])

  #plotting the images

  plt.figure(figsize = (10,10))
  for i in range(class_num):
    plt.subplot(5,5,i+1)
    plt.xticks([])
    plt.yticks([])
    plt.grid(False)
    plt.imshow(image_list[i], cmap=plt.cm.binary)
    plt.xlabel(classes[i])
  plt.show()


#calling the function

plot_img(x_training_set, y_training_set, classes)

#splitting the data for cross validation

x_validation_set = x_training_set[50000:]
y_validation_set = y_training_set[50000:]     # validation set has 10000 data

x_training_set = x_training_set[:50000]
y_training_set = y_training_set[:50000]


#vactorising the data

x_training_set = x_training_set.reshape(x_training_set.shape[0], 784)  #28x28 pixels = 784
x_testing_set = x_testing_set.reshape(x_testing_set.shape[0], 784)
x_validation_set = x_validation_set.reshape(x_validation_set.shape[0], 784)

#normalising the data

x_train = x_training_set/255  # since, pixel range from 0 to 255
x_test = x_testing_set/255
x_valid = x_validation_set/255

#one hot encoding for labels to represent categorical variables as numerical values

y_train = to_categorical(y_training_set)
y_test = to_categorical(y_testing_set)
y_valid = to_categorical(y_validation_set)


#default_x_train = x_train
#default_y_train = y_train

# some useful functions

#for hidden layer
def sigmoid(x):
  return 1 / (1 + np.exp(-x))

def relu(x):
  return (x>0)*(x)

def tanh(x):
  return np.tanh(x)

def gradient_sigmoid(x):
  return sigmoid(x) * (1 - sigmoid(x))

def gradient_tanh(x):
  return 1 - np.tanh(x) ** 2

def gradient_relu(x):
  return np.where(x > 0, 1, 0)

#for output layer
def softmax(x):
  exponents = np.exp(x - np.max(x, axis=1, keepdims=True))
  return exponents / np.sum(exponents, axis=1, keepdims=True)

'''
#loss function(cross-entropy)
def loss_func(x,y):
  L = -np.mean(np.sum(x * np.log(y), axis=1))
  return L'''

# loss function (cross-entropy)
def loss_func(x, y):
    epsilon = 1e-10  # small epsilon value to avoid log overflow
    clipped_y = np.clip(y, epsilon, 1 - epsilon)  # clip predicted probabilities
    L = -np.mean(np.sum(x * np.log(clipped_y), axis=1))
    return L


#function to choose the activation functions

def choose_activation(x, activation_function):
  if activation_function == 'sigmoid':
    return sigmoid(x)

  elif activation_function == 'tanh':
    return tanh(x)

  elif activation_function == 'relu':
    return relu(x)


#function for derivatives

def activation_derivative(x, activation_function):
    if activation_function == 'sigmoid':
        return gradient_sigmoid(x)
    elif activation_function == 'relu':
        return gradient_relu(x)
    elif activation_function == 'tanh':
        return gradient_tanh(x)
    else:
        raise ValueError("Invalid activation function. Please choose from 'sigmoid', 'relu', or 'tanh'.")

#class definition

class Network:
    def __init__(self, neuron_sizes, weight_initialiser, activation_function, momentum, beta1, beta2):

        self.train_loss_sgd = []
        self.train_loss_momentum = []


        self.total_layers = len(neuron_sizes)
        self.momentum = momentum
        #self.weight_initialiser = weight_initialiser
        self.activation_function = activation_function
        self.beta1 = beta1
        self.beta2 = beta2
        self.epsilon = 1e-8

        # Initializing the weights and biases
        # After initializing, store weights and biases in separate lists
        if weight_initialiser == 'xavier':
            if activation_function != 'relu':
                self.Weights = [-1/np.sqrt(neuron_sizes[i])+np.random.randn(neuron_sizes[i], neuron_sizes[i+1])*2/np.sqrt(neuron_sizes[i]) for i in range(self.total_layers-1)]
                self.biases = [-1/np.sqrt(neuron_sizes[i])+np.random.randn(1, neuron_sizes[i+1])*2/np.sqrt(neuron_sizes[i]) for i in range(self.total_layers-1)]
            else:
                self.Weights = [np.random.randn(neuron_sizes[i], neuron_sizes[i+1])*(np.sqrt(2/(neuron_sizes[i]))) for i in range(self.total_layers-1)]
                self.biases = [np.random.randn(1, neuron_sizes[i+1])*(np.sqrt(2/(neuron_sizes[i]))) for i in range(self.total_layers-1)]
        else:
            self.Weights = [np.random.randn(neuron_sizes[i], neuron_sizes[i+1]) for i in range(self.total_layers-1)]
            self.biases = [np.random.randn(1, neuron_sizes[i+1])*0.05 for i in range(self.total_layers-1)]

        # Initializing momentum weights and biases
        self.Weights_moment = [np.zeros_like(x) for x in self.Weights]
        self.biases_moment = [np.zeros_like(x) for x in self.biases]

        # Initializing Nesterov momentum adjusted weights and biases
        self.momentum_adjusted_Weights = None
        self.momentum_adjusted_biases = None


        # Initializing for adam optimizer
        self.Weights_moment_adam1 = [np.zeros_like(x) for x in self.Weights]
        self.biases_moment_adam1 = [np.zeros_like(x) for x in self.biases]
        self.Weights_moment_adam2 = [np.zeros_like(x) for x in self.Weights]  #rmsprop
        self.biases_moment_adam2 = [np.zeros_like(x) for x in self.biases]   #rmsprop


        # Initializing for nadam optimizer
        self.Weights_moment_nadam1 = [np.zeros_like(x) for x in self.Weights]
        self.biases_moment_nadam1 = [np.zeros_like(x) for x in self.biases]
        self.Weights_moment_nadam2 = [np.zeros_like(x) for x in self.Weights]
        self.biases_moment_nadam2 = [np.zeros_like(x) for x in self.biases]





    # Defining function for forward propagation
    def forward_prop(self, X):
        self.pre_activations_A = [None]*(self.total_layers)  # List to store the pre-activations
        self.activations_H = [X]  # List to store the activations

        for i in range(self.total_layers-1):
            self.pre_activations_A[i+1] = np.dot(self.activations_H[i], self.Weights[i]) + self.biases[i]
            if i == self.total_layers-2:  # For output layer: activation function = softmax
                h = softmax(self.pre_activations_A[i+1])
                self.activations_H.append(h)
            else:  # For hidden layers: activation function = sigmoid
                h = choose_activation(self.pre_activations_A[i+1], self.activation_function)
                #h = sigmoid(self.pre_activations_A[i+1])
                self.activations_H.append(h)
        return self.activations_H[-1]

    #defining the training method for stochastic gradient method
    def train_sgd(self, x_train, y_train, learning_rate_eta, total_epochs, batch_size):
        for epoch in range(total_epochs):
            loss_epo = 0
            accuracy = 0
            for i in range(0, x_train.shape[0], batch_size):
                # Forward pass
                Xbatch = x_train[i:i+batch_size]
                Ybatch = y_train[i:i+batch_size]
                y_predicted = self.forward_prop(Xbatch)

                #calculate loss
                loss = loss_func(Ybatch, y_predicted)
                loss_epo = loss_epo+loss

                #calculate accuracy
                acc = accuracy_score(np.argmax(y_predicted, axis=1), np.argmax(Ybatch, axis=1))
                accuracy = accuracy + acc

                # Applying backpropagation algorithm
                loss_gradient = y_predicted - Ybatch
                for j in range(self.total_layers - 1, 0, -1):
                    gradient_W = np.dot(self.activations_H[j-1].T, loss_gradient)
                    gradient_b = np.sum(loss_gradient, axis=0, keepdims=True)
                    if j > 1:
                        derivative_activation = activation_derivative(self.pre_activations_A[j-1], self.activation_function)
                        loss_gradient = np.dot(loss_gradient, self.Weights[j-1].T) * derivative_activation
                        #loss_gradient = np.dot(loss_gradient, self.Weights[j-1].T) * (self.activations_H[j-1] * (1 - self.activations_H[j-1]))

                    #updation of parameters
                    self.Weights[j-1] = self.Weights[j-1] - learning_rate_eta * gradient_W
                    self.biases[j-1] = self.biases[j-1] - learning_rate_eta * gradient_b


            #computing average train accuracy
            training_accuracy = accuracy / (x_train.shape[0] / batch_size)
            print(f'Epoch Number {epoch+1}, training accuracy: {training_accuracy:.4f}')
            wandb.log({'train-accuracy':training_accuracy*100})


            #computing average epoch loss
            loss_epo = loss_epo / (x_train.shape[0] / batch_size)
            print(f'Epoch Number {epoch+1}, training loss: {loss_epo:.4f}')
            wandb.log({'train-loss':loss_epo})
            #self.train_loss_sgd.append(loss_epo)
            '''
            #computing training loss
            train_loss = loss_func(y_train, y_predicted)
            print(f'Epoch Number {epoch+1}, training loss: {valid_accuracy:.4f}')'''

            #computing accuracy on validation set
            y_valid_predicted = self.forward_prop(x_valid)
            valid_accuracy = accuracy_score(np.argmax(y_valid_predicted, axis=1), np.argmax(y_valid, axis=1))
            print(f'Epoch Number {epoch+1}, validation accuracy: {valid_accuracy:.4f}')
            wandb.log({'val_accuracy':valid_accuracy*100})
            wandb.log({'epoch':epoch+1})

            #computing validation loss
            val_loss = loss_func(y_valid, y_valid_predicted)
            print(f'Epoch Number {epoch+1}, validation loss: {val_loss:.4f}')
            wandb.log({'val-loss':val_loss})


        #checking the efficiency of the model by passing test set
        y_test_predicted = self.forward_prop(x_test)
        test_accuracy = accuracy_score(np.argmax(y_test_predicted, axis = 1), np.argmax(y_test, axis = 1))
        print(f'Test Accuracy: {test_accuracy:.4f}')

    # Defining the momentum-based gradient descent training method
    def train_momentum(self, x_train, y_train, learning_rate_eta, total_epochs, batch_size):
        for epoch in range(total_epochs):
            loss_epo = 0
            accuracy = 0
            for i in range(0, x_train.shape[0], batch_size):

                #performing the forward pass
                Xbatch = x_train[i:i+batch_size]
                Ybatch = y_train[i:i+batch_size]
                y_predicted = self.forward_prop(Xbatch)

                #calculate loss
                loss = loss_func(Ybatch, y_predicted)
                loss_epo = loss_epo+loss

                #calculate accuracy
                acc = accuracy_score(np.argmax(y_predicted, axis=1), np.argmax(Ybatch, axis=1))
                accuracy = accuracy + acc

                #performing the back-propagation
                loss_gradient = y_predicted - Ybatch
                for j in range(self.total_layers - 1, 0, -1):
                    gradient_W = np.dot(self.activations_H[j-1].T, loss_gradient)
                    gradient_b = np.sum(loss_gradient, axis=0, keepdims=True)
                    if j > 1:
                        derivative_activation = activation_derivative(self.pre_activations_A[j-1], self.activation_function)
                        loss_gradient = np.dot(loss_gradient, self.Weights[j-1].T) * derivative_activation
                        #loss_gradient = np.dot(loss_gradient, self.Weights[j-1].T) * (self.activations_H[j-1] * (1 - self.activations_H[j-1]))

                    #updation of momentum
                    self.Weights_moment[j-1] = self.momentum * self.Weights_moment[j-1] + learning_rate_eta * gradient_W
                    self.biases_moment[j-1] = self.momentum * self.biases_moment[j-1] + learning_rate_eta * gradient_b

                    #updation of parameters
                    self.Weights[j-1] = self.Weights[j-1] - self.Weights_moment[j-1]
                    self.biases[j-1] = self.biases[j-1] - self.biases_moment[j-1]

            #computing average train accuracy
            training_accuracy = accuracy / (x_train.shape[0] / batch_size)
            print(f'Epoch Number {epoch+1}, training accuracy: {training_accuracy:.4f}')
            wandb.log({'train-accuracy':training_accuracy*100})


            #computing average epoch(training loss) loss
            loss_epo = loss_epo / (x_train.shape[0] / batch_size)
            print(f'Epoch Number {epoch+1}, training loss: {loss_epo:.4f}')
            wandb.log({'train-loss':loss_epo})
            #self.train_loss_sgd.append(loss_epo)

            #computing accuracy on validation set
            y_valid_predicted = self.forward_prop(x_valid)
            valid_accuracy = accuracy_score(np.argmax(y_valid_predicted, axis=1), np.argmax(y_valid, axis=1))
            print(f'Epoch Number {epoch+1}, validation accuracy: {valid_accuracy:.4f}')
            wandb.log({'val_accuracy':valid_accuracy*100})
            wandb.log({'epoch':epoch+1})

            #computing validation loss
            val_loss = loss_func(y_valid, y_valid_predicted)
            print(f'Epoch Number {epoch+1}, validation loss: {val_loss:.4f}')
            wandb.log({'val-loss':val_loss})

        #checking the efficiency of the model by passing test set
        y_test_predicted = self.forward_prop(x_test)
        test_accuracy = accuracy_score(np.argmax(y_test_predicted, axis = 1), np.argmax(y_test, axis = 1))
        print(f'Test Accuracy: {test_accuracy:.4f}')

    #defining the training method for nesterov accelerated gradient descent method
    def train_nag(self, x_train, y_train, learning_rate_eta, total_epochs, batch_size):
        for epoch in range(total_epochs):
            loss_epo = 0
            accuracy = 0
            for i in range(0, x_train.shape[0], batch_size):
                #performing forward pass
                Xbatch = x_train[i:i+batch_size]
                Ybatch = y_train[i:i+batch_size]

                # Nesterov accelerated gradient descent: lookahead
                '''
                self.momentum_adjusted_Weights = [self.Weights[j-1] - self.momentum * self.Weights_moment[j-1] for j in range(self.total_layers - 1, 0, -1)]
                self.momentum_adjusted_biases = [self.biases[j-1] - self.momentum * self.biases_moment[j-1] for j in range(self.total_layers - 1, 0, -1)]'''

                self.momentum_adjusted_Weights = [self.Weights[j] - self.momentum * self.Weights_moment[j] for j in range(self.total_layers-1)]
                self.momentum_adjusted_biases = [self.biases[j] - self.momentum * self.biases_moment[j] for j in range(self.total_layers-1)]
                '''
                print(self.momentum_adjusted_Weights[-1].shape)
                print(self.momentum_adjusted_Weights[-2].shape)
                print(self.momentum_adjusted_Weights[-3].shape)'''

                y_predicted = self.forward_prop(Xbatch)


                #calculate loss
                loss = loss_func(Ybatch, y_predicted)
                loss_epo = loss_epo+loss

                #calculate accuracy
                acc = accuracy_score(np.argmax(y_predicted, axis=1), np.argmax(Ybatch, axis=1))
                accuracy = accuracy + acc


                #performing back propagation
                loss_gradient = y_predicted - Ybatch
                for j in range(self.total_layers - 1, 0, -1):
                    gradient_W = np.dot(self.activations_H[j-1].T, loss_gradient)
                    gradient_b = np.sum(loss_gradient, axis=0, keepdims=True)
                    if j > 1:
                        #derivative_activation = 1 - self.activations_H[j-1] ** 2
                        derivative_activation = activation_derivative(self.pre_activations_A[j-1], self.activation_function)
                        loss_gradient = np.dot(loss_gradient, self.momentum_adjusted_Weights[j-1].T) * derivative_activation

                        #loss_gradient = np.dot(loss_gradient, self.momentum_adjusted_Weights[j-1].T) * (self.activations_H[j-1] * (1 - self.activations_H[j-1]))

                    self.Weights[j-1] = self.momentum_adjusted_Weights[j-1] - learning_rate_eta * gradient_W
                    self.biases[j-1] = self.momentum_adjusted_biases[j-1] - learning_rate_eta * gradient_b


            #computing average train accuracy
            training_accuracy = accuracy / (x_train.shape[0] / batch_size)
            print(f'Epoch Number {epoch+1}, training accuracy: {training_accuracy:.4f}')
            wandb.log({'train-accuracy':training_accuracy*100})


            #computing average epoch(training loss) loss
            loss_epo = loss_epo / (x_train.shape[0] / batch_size)
            print(f'Epoch Number {epoch+1}, training loss: {loss_epo:.4f}')
            wandb.log({'train-loss':loss_epo})
            #self.train_loss_sgd.append(loss_epo)

            #computing accuracy on validation set
            y_valid_predicted = self.forward_prop(x_valid)
            valid_accuracy = accuracy_score(np.argmax(y_valid_predicted, axis=1), np.argmax(y_valid, axis=1))
            print(f'Epoch Number {epoch+1}, validation accuracy: {valid_accuracy:.4f}')
            wandb.log({'val_accuracy':valid_accuracy*100})
            wandb.log({'epoch':epoch+1})

            #computing validation loss
            val_loss = loss_func(y_valid, y_valid_predicted)
            print(f'Epoch Number {epoch+1}, validation loss: {val_loss:.4f}')
            wandb.log({'val-loss':val_loss})

        #checking the efficiency of the model by passing test set
        y_test_predicted = self.forward_prop(x_test)
        test_accuracy = accuracy_score(np.argmax(y_test_predicted, axis = 1), np.argmax(y_test, axis = 1))
        print(f'Test Accuracy: {test_accuracy:.4f}')



    def train_adam(self, x_train, y_train, learning_rate_eta, total_epochs, batch_size):
      for epoch in range(total_epochs):
        loss_epo = 0
        accuracy = 0
        for i in range(0, x_train.shape[0], batch_size):
          #performing forward pass
          Xbatch = x_train[i:i+batch_size]
          Ybatch = y_train[i:i+batch_size]
          y_predicted = self.forward_prop(Xbatch)

          #calculate loss
          loss = loss_func(Ybatch, y_predicted)
          loss_epo = loss_epo + loss

          #calculate accuracy
          acc = accuracy_score(np.argmax(y_predicted, axis=1), np.argmax(Ybatch, axis=1))
          accuracy = accuracy + acc

          #backpropagation
          loss_gradient = y_predicted-Ybatch
          for j in range(self.total_layers-1, 0, -1):
            gradient_W = np.dot(self.activations_H[j-1].T, loss_gradient)
            gradient_b = np.sum(loss_gradient, axis=0, keepdims=True)

            if j > 1:
              derivative_activation = activation_derivative(self.pre_activations_A[j-1], self.activation_function)
              loss_gradient = np.dot(loss_gradient, self.Weights[j-1].T)*derivative_activation

            #compute 1st momentum term
            self.Weights_moment_adam1[j-1] = self.beta1 * self.Weights_moment_adam1[j-1] + (1-self.beta1) * gradient_W
            self.biases_moment_adam1[j-1] = self.beta1 * self.biases_moment_adam1[j-1] + (1-self.beta1) * gradient_b

            #compute 2nd moment term
            self.Weights_moment_adam2[j-1] = self.beta2 * self.Weights_moment_adam2[j-1] + (1-self.beta2) * np.square(gradient_W)
            self.biases_moment_adam2[j-1] = self.beta2 * self.biases_moment_adam2[j-1] + (1-self.beta2) * np.square(gradient_b)

            #corrected terms in 1st moment
            corrected_weight_adam1 = self.Weights_moment_adam1[j-1] / (1-self.beta1 ** (epoch+1))
            corrected_bias_adam1 = self.biases_moment_adam1[j-1] / (1-self.beta1 ** (epoch+1))

            #corrected terms in 2nd moment
            corrected_weight_adam2 = self.Weights_moment_adam2[j-1] / (1-self.beta2 ** (epoch+1))
            corrected_bias_adam2 = self.biases_moment_adam2[j-1] / (1-self.beta2 ** (epoch+1))

            #updating weights and biases
            self.Weights[j-1] = self.Weights[j-1] - learning_rate_eta * corrected_weight_adam1 / (np.sqrt(corrected_weight_adam2)+self.epsilon)
            self.biases[j-1] = self.biases[j-1] - learning_rate_eta * corrected_bias_adam1 / (np.sqrt(corrected_bias_adam2)+self.epsilon)


        #computing average train accuracy
        training_accuracy = accuracy / (x_train.shape[0] / batch_size)
        print(f'Epoch Number {epoch+1}, training accuracy: {training_accuracy:.4f}')
        wandb.log({'train-accuracy':training_accuracy*100})



        #computing average epoch(training loss) loss
        loss_epo = loss_epo / (x_train.shape[0] / batch_size)
        print(f'Epoch Number {epoch+1}, training loss: {loss_epo:.4f}')
        wandb.log({'train-loss':loss_epo})


        #computing accuracy on validation set
        y_valid_predicted = self.forward_prop(x_valid)
        valid_accuracy = accuracy_score(np.argmax(y_valid_predicted, axis=1), np.argmax(y_valid, axis=1))
        print(f'Epoch Number {epoch+1}, validation accuracy: {valid_accuracy:.4f}')
        wandb.log({'val_accuracy':valid_accuracy*100})
        wandb.log({'epoch':epoch+1})

        #computing validation loss
        val_loss = loss_func(y_valid, y_valid_predicted)
        print(f'Epoch Number {epoch+1}, validation loss: {val_loss:.4f}')
        wandb.log({'val-loss':val_loss})

      #checking the efficiency of the model by passing test set
      y_test_predicted = self.forward_prop(x_test)
      #return y_test_predicted

      test_accuracy = accuracy_score(np.argmax(y_test_predicted, axis = 1), np.argmax(y_test, axis = 1))
      print(f'Test Accuracy: {test_accuracy:.4f}')



    def train_rmsprop(self, x_train, y_train, learning_rate_eta, total_epochs, batch_size):
      for epoch in range(total_epochs):
        loss_epo = 0
        accuracy = 0
        for i in range(0, x_train.shape[0], batch_size):
          Xbatch = x_train[i:i+batch_size]
          Ybatch = y_train[i:i+batch_size]
          y_predicted = self.forward_prop(Xbatch)

          #calculate loss
          loss = loss_func(Ybatch, y_predicted)
          loss_epo = loss_epo + loss

          #calculate accuracy
          acc = accuracy_score(np.argmax(y_predicted, axis=1), np.argmax(Ybatch, axis=1))
          accuracy = accuracy + acc

          #backpropagation
          loss_gradient = y_predicted-Ybatch
          for j in range(self.total_layers-1, 0, -1):
            gradient_W = np.dot(self.activations_H[j-1].T, loss_gradient)
            gradient_b = np.sum(loss_gradient, axis=0, keepdims=True)

            if j > 1:
              derivative_activation = activation_derivative(self.pre_activations_A[j-1], self.activation_function)
              loss_gradient = np.dot(loss_gradient, self.Weights[j-1].T)*derivative_activation
            '''
            #compute 1st momentum term
            self.Weights_moment_adam1[j-1] = self.beta1 * self.Weights_moment_adam1[j-1] + (1-self.beta1) * gradient_W
            self.biases_moment_adam1[j-1] = self.beta1 * self.biases_moment_adam1[j-1] + (1-self.beta1) * gradient_b'''

            #compute moment term
            self.Weights_moment_adam2[j-1] = self.beta2 * self.Weights_moment_adam2[j-1] + (1-self.beta2) * np.square(gradient_W)
            self.biases_moment_adam2[j-1] = self.beta2 * self.biases_moment_adam2[j-1] + (1-self.beta2) * np.square(gradient_b)
            '''
            #corrected terms in 1st moment
            corrected_weight_adam1 = self.Weights_moment_adam1[j-1] / (1-self.beta1 ** (epoch+1))
            corrected_bias_adam1 = self.biases_moment_adam1[j-1] / (1-self.beta1 ** (epoch+1))

            #corrected terms in 2nd moment
            corrected_weight_adam2 = self.Weights_moment_adam2[j-1] / (1-self.beta2 ** (epoch+1))
            corrected_bias_adam2 = self.biases_moment_adam2[j-1] / (1-self.beta2 ** (epoch+1))'''

            #updating weights and biases
            '''
            self.Weights[j-1] = self.Weights[j-1] - learning_rate_eta * corrected_weight_adam1 / (np.sqrt(corrected_weight_adam2)+self.epsilon)
            self.biases[j-1] = self.biases[j-1] - learning_rate_eta * corrected_bias_adam1 / (np.sqrt(corrected_bias_adam2)+self.epsilon)'''

            self.Weights[j-1] = self.Weights[j-1] - learning_rate_eta * gradient_W / (np.sqrt(self.Weights_moment_adam2[j-1]) + self.epsilon)
            self.biases[j-1] = self.biases[j-1] - learning_rate_eta * gradient_b / (np.sqrt(self.biases_moment_adam2[j-1]) + self.epsilon)

        #computing average train accuracy
        training_accuracy = accuracy / (x_train.shape[0] / batch_size)
        print(f'Epoch Number {epoch+1}, training accuracy: {training_accuracy:.4f}')
        wandb.log({'train-accuracy':training_accuracy*100})


        #computing average epoch(training loss) loss
        loss_epo = loss_epo / (x_train.shape[0] / batch_size)
        print(f'Epoch Number {epoch+1}, training loss: {loss_epo:.4f}')
        wandb.log({'train-loss':loss_epo})
        #self.train_loss_sgd.append(loss_epo)

        #computing accuracy on validation set
        y_valid_predicted = self.forward_prop(x_valid)
        valid_accuracy = accuracy_score(np.argmax(y_valid_predicted, axis=1), np.argmax(y_valid, axis=1))
        print(f'Epoch Number {epoch+1}, validation accuracy: {valid_accuracy:.4f}')
        wandb.log({'val_accuracy':valid_accuracy*100})
        wandb.log({'epoch':epoch+1})

        #computing validation loss
        val_loss = loss_func(y_valid, y_valid_predicted)
        print(f'Epoch Number {epoch+1}, validation loss: {val_loss:.4f}')
        wandb.log({'val-loss':val_loss})

      #checking the efficiency of the model by passing test set
      y_test_predicted = self.forward_prop(x_test)
      test_accuracy = accuracy_score(np.argmax(y_test_predicted, axis = 1), np.argmax(y_test, axis = 1))
      print(f'Test Accuracy: {test_accuracy:.4f}')



    def train_nadam(self, x_train, y_train, learning_rate_eta, total_epochs, batch_size):
      for epoch in range(total_epochs):
        loss_epo = 0
        accuracy = 0
        for i in range(0, x_train.shape[0], batch_size):
          Xbatch = x_train[i:i+batch_size]
          Ybatch = y_train[i:i+batch_size]
          y_predicted = self.forward_prop(Xbatch)

          #calculate loss
          loss = loss_func(Ybatch, y_predicted)
          loss_epo = loss_epo + loss

          #calculate accuracy
          acc = accuracy_score(np.argmax(y_predicted, axis=1), np.argmax(Ybatch, axis=1))
          accuracy = accuracy + acc

          #backpropagation
          loss_gradient = y_predicted-Ybatch
          for j in range(self.total_layers-1, 0, -1):
            gradient_W = np.dot(self.activations_H[j-1].T, loss_gradient)
            gradient_b = np.sum(loss_gradient, axis=0, keepdims=True)

            if j > 1:
              derivative_activation = activation_derivative(self.pre_activations_A[j-1], self.activation_function)
              loss_gradient = np.dot(loss_gradient, self.Weights[j-1].T)*derivative_activation

            #compute 1st momentum term
            self.Weights_moment_nadam1[j-1] = self.beta1 * self.Weights_moment_nadam1[j-1] + (1-self.beta1) * gradient_W
            self.biases_moment_nadam1[j-1] = self.beta1 * self.biases_moment_nadam1[j-1] + (1-self.beta1) * gradient_b

            #compute 2nd moment term
            self.Weights_moment_nadam2[j-1] = self.beta2 * self.Weights_moment_nadam2[j-1] + (1-self.beta2) * np.square(gradient_W)
            self.biases_moment_nadam2[j-1] = self.beta2 * self.biases_moment_nadam2[j-1] + (1-self.beta2) * np.square(gradient_b)

            #corrected terms in 1st moment
            corrected_weight_nadam1 = self.Weights_moment_nadam1[j-1] / (1-self.beta1 ** (epoch+1))
            corrected_bias_nadam1 = self.biases_moment_nadam1[j-1] / (1-self.beta1 ** (epoch+1))

            #corrected terms in 2nd moment
            corrected_weight_nadam2 = self.Weights_moment_nadam2[j-1] / (1-self.beta2 ** (epoch+1))
            corrected_bias_nadam2 = self.biases_moment_nadam2[j-1] / (1-self.beta2 ** (epoch+1))

            #netsrov momentum update
            momentum_updated_weight = self.beta1*corrected_weight_nadam1 + ((1-self.beta1)*gradient_W) / (1 - self.beta1**(epoch+1))
            momentum_updated_bias = self.beta1 * corrected_bias_nadam1 + ((1-self.beta1)*gradient_b) / (1 - self.beta1**(epoch+1))

            #updating weights and biases
            self.Weights[j-1] = self.Weights[j-1] - learning_rate_eta * momentum_updated_weight / (np.sqrt(corrected_weight_nadam2)+self.epsilon)
            self.biases[j-1] = self.biases[j-1] - learning_rate_eta * momentum_updated_bias / (np.sqrt(corrected_bias_nadam2)+self.epsilon)

        #computing average train accuracy
        training_accuracy = accuracy / (x_train.shape[0] / batch_size)
        print(f'Epoch Number {epoch+1}, training accuracy: {training_accuracy:.4f}')
        wandb.log({'train-accuracy':training_accuracy*100})


        #computing average epoch(training loss) loss
        loss_epo = loss_epo / (x_train.shape[0] / batch_size)
        print(f'Epoch Number {epoch+1}, training loss: {loss_epo:.4f}')
        #self.train_loss_sgd.append(loss_epo)
        wandb.log({'train-loss':loss_epo})

        #computing accuracy on validation set
        y_valid_predicted = self.forward_prop(x_valid)
        valid_accuracy = accuracy_score(np.argmax(y_valid_predicted, axis=1), np.argmax(y_valid, axis=1))
        print(f'Epoch Number {epoch+1}, validation accuracy: {valid_accuracy:.4f}')
        wandb.log({'val_accuracy':valid_accuracy*100})
        wandb.log({'epoch':epoch+1})

        #computing validation loss
        val_loss = loss_func(y_valid, y_valid_predicted)
        print(f'Epoch Number {epoch+1}, validation loss: {val_loss:.4f}')
        wandb.log({'val-loss':val_loss})

      #checking the efficiency of the model by passing test set
      y_test_predicted = self.forward_prop(x_test)
      test_accuracy = accuracy_score(np.argmax(y_test_predicted, axis = 1), np.argmax(y_test, axis = 1))
      print(f'Test Accuracy: {test_accuracy:.4f}')

!pip install wandb

import wandb
import numpy as np
from types import SimpleNamespace
import random

wandb.login(key='cd7a6c2259e8886dc269bbf6f0f9e55089d3beeb')

# You need to define a config file in the form of dictionary or yaml
sweep_config = {
    'method': 'random',
    'name' : 'sweep test12',
    'metric': {
      'name': 'val_accuracy',
      'goal': 'maximize'
    },
    'parameters': {
        'epochs': {
            'values': [5,10]
        },
        'hidden_layers':{
            'values':[3,4,5]
        },
        'optimizer': {
            'values':[ 'sgd', 'momentum', 'nesterov', 'adam', 'nadam', 'rmsprop']
        },
         'hidden_size':{
            'values':[32,64,128]
        },
        'batch_size': {
            'values':[16,32,64]
        },
        'learning_rate': {
            'values':[1e-3, 1e-4]
        },
        'weight_init': {
           'values' :['random', 'xavier']
        },
        'activation': {
            'values': ['sigmoid', 'relu','tanh']
        },
        'weight_decay': {
            'values': [0]
        },
    }
}

sweep_id = wandb.sweep(sweep=sweep_config, project='Deep_Learning_Assignment1')

def main():
    '''
    WandB calls main function each time with differnet combination.

    We can retrive the same and use the same values for our hypermeters.

    '''


    with wandb.init(entity = 'prabhat-kumar') as run:

        run_name="-ac_"+wandb.config.activation+"-hs"+str(wandb.config.hidden_size)+'-wi'+wandb.config.weight_init+'-hl'+str(wandb.config.hidden_layers)+'-op'+wandb.config.optimizer+'-ep'+str(wandb.config.epochs)+'lr'+str(wandb.config.learning_rate)+'bs'+str(wandb.config.batch_size) +'wd'+str(wandb.config.weight_decay)
        wandb.run.name=run_name

        model = Network([784,wandb.config.hidden_size,10], wandb.config.weight_init, wandb.config.activation, 0.9, 0.9, 0.999)

        if wandb.config.optimizer == 'nesterov':
          model.train_nag(x_train, y_train, wandb.config.learning_rate, wandb.config.epochs, wandb.config.batch_size)
        if wandb.config.optimizer == 'momentum':
          model.train_momentum(x_train, y_train, wandb.config.learning_rate, wandb.config.epochs, wandb.config.batch_size)
        if wandb.config.optimizer == 'sgd':
          model.train_sgd(x_train, y_train, wandb.config.learning_rate, wandb.config.epochs, wandb.config.batch_size)
        if wandb.config.optimizer == 'adam':
          model.train_adam(x_train, y_train, wandb.config.learning_rate, wandb.config.epochs, wandb.config.batch_size)
        if wandb.config.optimizer == 'rmsprop':
          model.train_rmsprop(x_train, y_train, wandb.config.learning_rate, wandb.config.epochs, wandb.config.batch_size)
        if wandb.config.optimizer == 'nadam':
          model.train_nadam(x_train, y_train, wandb.config.learning_rate, wandb.config.epochs, wandb.config.batch_size)

wandb.agent(sweep_id, function=main,count=2) # calls main function for count number of times.
wandb.finish()

"""## For best combination"""

# You need to define a config file in the form of dictionary or yaml
sweep_config = {
    'method': 'random',
    'name' : 'sweep test19',
    'metric': {
      'name': 'val_accuracy',
      'goal': 'maximize'
    },
    'parameters': {
        'epochs': {
            'values': [10]
        },
        'hidden_layers':{
            'values':[5]
        },
        'optimizer': {
            'values':[ 'adam']
        },
         'hidden_size':{
            'values':[128]
        },
        'batch_size': {
            'values':[16]
        },
        'learning_rate': {
            'values':[1e-3]
        },
        'weight_init': {
           'values' :['xavier']
        },
        'activation': {
            'values': ['tanh']
        },
        'weight_decay': {
            'values': [0]
        },
    }
}

sweep_id = wandb.sweep(sweep=sweep_config, project='Deep_Learning_Assignment1')

import seaborn as sns
import itertools

def plot_confusion_matrix(cm, classes, normalize=False, title='Confusion matrix', cmap=plt.cm.Blues):

    if normalize:
        cm = cm.astype('float') / cm.sum(axis=1)[:, np.newaxis]
        print("confusion matrix")
    else:
        print('Confusion matrix, without normalization')

    plt.figure(figsize=(8, 6))
    plt.imshow(cm, interpolation='nearest', cmap=cmap)
    plt.title(title)
    plt.colorbar()
    tick_marks = np.arange(len(classes))
    plt.xticks(tick_marks, classes, rotation=45)
    plt.yticks(tick_marks, classes)

    fmt = '.2f' if normalize else 'd'
    thresh = cm.max() / 2.
    for i, j in itertools.product(range(cm.shape[0]), range(cm.shape[1])):
        plt.text(j, i, format(cm[i, j], fmt),
                 horizontalalignment="center",
                 color="white" if cm[i, j] > thresh else "black")

    plt.tight_layout()
    plt.ylabel('True label')
    plt.xlabel('Predicted label')

from sklearn.metrics import confusion_matrix
def main():
    '''
    WandB calls main function each time with differnet combination.

    We can retrive the same and use the same values for our hypermeters.

    '''


    with wandb.init(entity = 'prabhat-kumar') as run:

        run_name="-ac_"+wandb.config.activation+"-hs"+str(wandb.config.hidden_size)+'-wi'+wandb.config.weight_init+'-hl'+str(wandb.config.hidden_layers)+'-op'+wandb.config.optimizer+'-ep'+str(wandb.config.epochs)+'lr'+str(wandb.config.learning_rate)+'bs'+str(wandb.config.batch_size) +'wd'+str(wandb.config.weight_decay)
        wandb.run.name=run_name

        model = Network([784,wandb.config.hidden_size,10], wandb.config.weight_init, wandb.config.activation, 0.9, 0.9, 0.999)

        if wandb.config.optimizer == 'nesterov':
          model.train_nag(x_train, y_train, wandb.config.learning_rate, wandb.config.epochs, wandb.config.batch_size)
        if wandb.config.optimizer == 'momentum':
          model.train_momentum(x_train, y_train, wandb.config.learning_rate, wandb.config.epochs, wandb.config.batch_size)
        if wandb.config.optimizer == 'sgd':
          model.train_sgd(x_train, y_train, wandb.config.learning_rate, wandb.config.epochs, wandb.config.batch_size)
        if wandb.config.optimizer == 'adam':
          model.train_adam(x_train, y_train, wandb.config.learning_rate, wandb.config.epochs, wandb.config.batch_size)
        if wandb.config.optimizer == 'rmsprop':
          model.train_rmsprop(x_train, y_train, wandb.config.learning_rate, wandb.config.epochs, wandb.config.batch_size)
        if wandb.config.optimizer == 'nadam':
          model.train_nadam(x_train, y_train, wandb.config.learning_rate, wandb.config.epochs, wandb.config.batch_size)



        y_pred = np.argmax(model.forward_prop(x_test), axis=1)
        cm = confusion_matrix(np.argmax(y_test, axis=1), y_pred)
        print("Confusion Matrix:")
        print(cm)

        # Plot confusion matrix
        plot_confusion_matrix(cm, classes=['T-shirt/top', 'Trouser', 'Pullover', 'Dress', 'Coat', 'Sandal', 'Shirt', 'Sneaker', 'Bag', 'Ankle boot'], normalize=True,
                              title='confusion matrix')

wandb.agent(sweep_id, function=main,count=1) # calls main function for count number of times.
wandb.finish()