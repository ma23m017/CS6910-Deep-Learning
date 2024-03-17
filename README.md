##

The given code defines a neural network class and also includes the methods for training the network using various optimization algorithms.

First of all I have imported all the essentials libraries and also, imported in some other places wherever is required.

Here, for loading the fashion mnist data I have used 'fashion_mnist.load_data()' function. This dataset contains the grayscale images of fashion items.

I have splitted the data set into training, testing and validation data. Training to train the model, validation to validate, whether model is working in proper way or not and test data set to test the working of the model on unseen new data.

I also have done some necessary operations on the data like one hot encoding and normalising. Then I have defined the essential functions required for this program. I have written code that defines the activation functions and their derivatives, loss function i.e. cross-entropy(as I have not included the mean squared error loss function).

Then I have defined a class that has some parameters, like list that contains size of neurons in each layer, momentum value, beta1, beta2, weight initialiser and activation functions. Inside the class with the help of constructor I initialised some values like weights and biases for various optimisers like mgd, adam, nadam, rmsprop. Then inside the class I have made a member function of the class named 'forward_prop' which helps in performing the forward propagation. This function returns the value as vector or matrix which depends on the argument that we pass in this function. But in this propgarma we have bassed the data as batches so the input and output will be in batch i.e. matrix.

Then I have made the function that trains the model and performs backpropagation for various optimisers. Here we have used six optimisers which are sgd, mgd, nesterov accelerated gradient descen, adam, nadam and rmsprop. I have not made the separate function for back propagation, instead in a single function, inside that funcction I am running the epochs and in each epoch whole training data set is being passed in small small batches. Forward propagation function is being invoked here which take these batches as arguments. For taking these batches I have used loop in the range of batch size. After that inside that loop itself I am performing backpropagation but without any help of any function i.e. I have written code directly here for back propagation. After that I have written code for updating the weights and biases. I have used the similar kind of approach for other optimizers also. Inside this training function I have printed accuracies and losses. Finally I have connected my code with wandb.
