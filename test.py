from __future__ import print_function

import pylab as pl
import subprocess as sb
import numpy as np
import sys

from keras.datasets import cifar10
from keras.preprocessing.image import ImageDataGenerator
from keras.models import Sequential
from keras.layers.core import Dense, Dropout, Activation, Flatten
from keras.layers.convolutional import Convolution2D, MaxPooling2D
from keras.optimizers import SGD
from keras.utils import np_utils

import theano


batch_size = 32
nb_train_samples = 2000
nb_test_samples = 20
nb_classes = 2
nb_epoch = 10
data_augmentation = False

# input image dimensions
img_rows, img_cols = 32, 32
chan_min = 0
chan_max = 3
img_channels = chan_max - chan_min

dir_data = "GenerateData/"

f_xtrain = dir_data + "xtrain.npy"
f_ytrain = dir_data + "ytrain.npy"

# read from file
X_train_tmp = np.load(f_xtrain)
y_train_tmp = np.load(f_ytrain).astype(int)
X_check_nan = np.isnan(X_train_tmp[:, 0, 0])
ind_nan = np.where(X_check_nan == True)[0]
print("number of Nan images:", len(ind_nan))

# remove Nan elements
X_train_tmp = np.delete(X_train_tmp, ind_nan, axis=0)
y_train_tmp = np.delete(y_train_tmp, ind_nan, axis=0)

# sub-select
X_train = X_train_tmp[:nb_train_samples, :, :]
y_train = y_train_tmp[:nb_train_samples]
X_test = X_train_tmp[nb_train_samples:nb_train_samples+nb_test_samples, :, :]
y_test = y_train_tmp[nb_train_samples:nb_train_samples+nb_test_samples]

# add dimension
# X_train = np.expand_dims(X_train, axis=1)
# X_test = np.expand_dims(X_test, axis=1)
# y_train = np.expand_dims(y_train, axis=1)
# y_test = np.expand_dims(y_test, axis=1)

# Measure limits
print(np.min(X_train), np.max(X_train))

# X_train *= 100.
# X_test *= 100.
print(np.min(X_train), np.max(X_train))


'''
dir_data = "./data/sim/SIMGEOM0/"

f_xtrain = dir_data + "mysim_img.npy"
f_ytrain = dir_data + "mysim_lab.npy"

X_train_tmp = np.load(f_xtrain)
y_train_tmp = np.load(f_ytrain)

X_train = X_train_tmp[:nb_train_samples, :, :, :]
y_train = y_train_tmp[:nb_train_samples, :]
X_test = X_train_tmp[nb_train_samples:nb_train_samples+nb_test_samples, :, :, :]
y_test = y_train_tmp[nb_train_samples:nb_train_samples+nb_test_samples, :]
'''
print("dimension", np.shape(y_train))
check_test = np.where(y_train[:] == 0)[0]
print(len(check_test))
check_test = np.where(y_train[:] == 1)[0]
print(len(check_test))
# for i in np.arange(len(X_train[:, 0, 0, 0])):
#    print(np.min(X_train[i, 0, :, :]), np.max(X_train[i, 0, :, :]), y_train[i, 0])

'''
# the data, shuffled and split between train and test sets
(X_train, y_train), (X_test, y_test) = cifar10.load_data()

X_train = X_train[:nb_train_samples, chan_min:chan_max, :, :]
y_train = y_train[:nb_train_samples, :]

X_test = X_test[:nb_test_samples, chan_min:chan_max, :, :]
y_test = y_test[:nb_test_samples, :]
'''

print('X_train shape:', X_train.shape)
print(X_train.shape[0], 'train samples')
print(X_test.shape[0], 'test samples')

# convert class vectors to binary class matrices
Y_train = np_utils.to_categorical(y_train, nb_classes)
Y_test = np_utils.to_categorical(y_test, nb_classes)

model = Sequential()

model.add(Convolution2D(32, 3, 3, border_mode='same',
                        input_shape=(img_channels, img_rows, img_cols)))
convout1 = Activation('relu')
model.add(convout1)
model.add(Convolution2D(32, 3, 3))
model.add(Activation('relu'))
model.add(MaxPooling2D(pool_size=(2, 2)))
model.add(Dropout(0.25))

model.add(Convolution2D(64, 3, 3, border_mode='same'))
model.add(Activation('relu'))
model.add(Convolution2D(64, 3, 3))
model.add(Activation('relu'))
model.add(MaxPooling2D(pool_size=(2, 2)))
model.add(Dropout(0.25))

model.add(Flatten())
model.add(Dense(512))
model.add(Activation('relu'))
model.add(Dropout(0.5))
model.add(Dense(nb_classes))
model.add(Activation('softmax'))

# let's train the model using SGD + momentum (how original).
sgd = SGD(lr=0.01, decay=1e-6, momentum=0.9, nesterov=True)
model.compile(loss='categorical_crossentropy',
              optimizer=sgd,
              metrics=['accuracy'])


X_train = X_train.astype('float32')
X_test = X_test.astype('float32')
# X_train /= 255
# X_test /= 255
print(np.min(X_train), np.max(X_train))

if not data_augmentation:
    print('Not using data augmentation.')
    model.fit(X_train, Y_train,
              batch_size=batch_size,
              nb_epoch=nb_epoch,
              validation_data=(X_test, Y_test),
              shuffle=True)
else:
    print('Using real-time data augmentation.')

    # this will do preprocessing and realtime data augmentation
    datagen = ImageDataGenerator(
        featurewise_center=False,  # set input mean to 0 over the dataset
        samplewise_center=False,  # set each sample mean to 0
        featurewise_std_normalization=False,  # divide inputs by std of the dataset
        samplewise_std_normalization=False,  # divide each input by its std
        zca_whitening=False,  # apply ZCA whitening
        rotation_range=0,  # randomly rotate images in the range (degrees, 0 to 180)
        width_shift_range=0.1,  # randomly shift images horizontally (fraction of total width)
        height_shift_range=0.1,  # randomly shift images vertically (fraction of total height)
        horizontal_flip=True,  # randomly flip images
        vertical_flip=False)  # randomly flip images

    # compute quantities required for featurewise normalization
    # (std, mean, and principal components if ZCA whitening is applied)
    datagen.fit(X_train)

    # fit the model on the batches generated by datagen.flow()
    model.fit_generator(datagen.flow(X_train, Y_train,
                        batch_size=batch_size),
                        samples_per_epoch=X_train.shape[0],
                        nb_epoch=nb_epoch,
                        validation_data=(X_test, Y_test))


# measure output
class_test_obs = model.predict_classes(X_test, batch_size=batch_size)
print("class test true:", y_test.reshape(class_test_obs.shape))
print("class test obse:", class_test_obs)
proba = model.predict_proba(X_test, batch_size=batch_size)

'''
# set up data
index = 0
convout1_f = theano.function([model.get_input_at(0)],
                             convout1.get_output_at(0))
X = X_test[index:index+1]
C1 = convout1_f(X)
C1 = np.squeeze(C1)

# plot figures
pl.figure(figsize=(15, 15))
pl.title('convout1')
plotters.nice_imshow(pl.gca(), plotters.make_mosaic(C1, 6, 6))  # , cmap=cm.binary)
f_save = "test_activation.png"
pl.savefig(f_save)
sb.call("open " + f_save, shell=True)
pl.close()

'''
