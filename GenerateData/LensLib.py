import numpy as np 
import matplotlib.pyplot as plt 
from subprocess import call
from sys import exit
from random import random
import os
np.random.seed(2527)

def fits2data(filename):
	from astropy.io import fits
	hdulist = fits.open(filename)
	data = hdulist[0].data
	return data/np.amax(data)

def GenLensFile(filename, Ngal, mass, width, posX, posY):
	for i in range(Ngal):
		if i==0:
			call("echo %1.3e %1.3f %1.3f %1.3f > %s"%(mass[i], width[i], posX[i], posY[i], filename), shell=True)
		else:
			call("echo %1.3e %1.3f %1.3f %1.3f >> %s"%(mass[i], width[i], posX[i], posY[i], filename), shell=True)

def GenSourceFile(Nsources, sourceX, sourceY, sourceR, filename='sources.gs'):
	for i in range(Nsources):
		if i==0:
			call("echo sources/add/circle %i %1.3f %1.3f 1 %1.3f > %s"%(i, sourceX[i], sourceY[i], sourceR[i], filename), shell=True)
		else:
			call("echo sources/add/circle %i %1.3f %1.3f 1 %1.3f >> %s"%(i, sourceX[i], sourceY[i], sourceR[i], filename), shell=True)

def LensParams(Ngal=5, xmin=-5, xmax=5, ymin=-5, ymax=5, minmass=11.5, maxmass=11.7):
	posX = np.random.uniform(xmin/2, xmax/2, Ngal)
	posY = np.random.uniform(ymin/2, ymax/2, Ngal)
	mass = 10**np.random.uniform(minmass, maxmass, Ngal)
	width = np.random.uniform(0, (xmax-xmin)/20.0, Ngal)
	return [mass, width, posX, posY]

def SourceParams(Nsources, Ngal, makelens, posX, posY):
	if makelens:
		source_distance = 0.0
	else:
		source_distance = 2.0

	ind = np.random.choice(Ngal, Nsources, replace=False)
	sourcesX = np.zeros((Nsources))
	sourcesY = np.zeros((Nsources))
	for i in range(Nsources):
		sourcesX[i] = np.random.normal(loc=posX[ind[i]]+source_distance, scale=0.5)
		sourcesY[i] = np.random.normal(loc=posY[ind[i]]+source_distance, scale=0.5)
	sourcesR = np.random.normal(loc=0.2, scale=0.05, size=Nsources)
	return [sourcesX, sourcesY, sourcesR]

def GenMainFile(zl, zs, xmin=-5, xmax=5, ymin=-5, ymax=5, xpix=32, ypix=32, \
	filename="gen.gs", lensfilename="lens.gs", sourcefilename="sources.gs"):

	call("echo lens/new/mplummers z\(%1.3f\) %s > %s"%(zl, lensfilename, filename), shell=True)
	call("echo lensplane/new/local %1.2f %1.2f %1.2f %1.2f %1.2f %1.2f >> %s"%(xmin, ymin, xmax, ymax, xpix, ypix, filename), shell=True)

	call("echo lensplane/plotdens/fits lens.fits %1.2f %1.2f %1.2f %1.2f %1.2f %1.2f >> %s"%(xmin, ymin, xmax, ymax, xpix, ypix, filename), shell=True)

	call("echo srcplane/new z\(%1.3f\) zz\(%1.3f,%1.3f\) >> %s"%(zs, zl, zs, filename), shell=True)
	call("echo imgplane/new/local %1.3f %1.3f %1.3f %1.3f %i %i >> %s"%(xmin, ymin, xmax, ymax, xpix+1, ypix+1, filename), shell=True)

	call("echo import %s >> %s"%(sourcefilename, filename), shell=True)
	call("echo imgplane/plot/fits imgplane.fits >> %s"%filename, shell=True)

def GenAllFiles(Ngal, Nsources, makelens, zl=0.5, zs=1.0,\
			xmin=-5, xmax=5, ymin=-5, ymax=5, xpix=32, ypix=32):

	[mass, width, posX, posY] = LensParams(Ngal)
	GenLensFile("lens.gs", Ngal, mass, width, posX, posY)
	[sourcesX, sourcesY, sourcesR] = SourceParams(Nsources, Ngal, makelens, posX, posY)
	GenSourceFile(Nsources, sourcesX, sourcesY, sourcesR)
	GenMainFile(zl, zs, xmin, xmax, ymin, ymax, xpix, ypix)


def GetImages(Ngal, Nsources, makelens, LensFactor=1.0, ImgFactor=1.0, zl=0.5, zs=1.0,\
			xmin=-5, xmax=5, ymin=-5, ymax=5, xpix=32, ypix=32):

	GenAllFiles(Ngal, Nsources, makelens, zl, zs, xmin, xmax, ymin, ymax, xpix, ypix)
	call(["graleshell", "gen.gs"])
	img = fits2data('imgplane.fits')/ImgFactor
	lens = fits2data('lens.fits')/LensFactor
	return [img, lens]

def GetImage(Ngal, Nsources, makelens, LensFactor=1.0, ImgFactor=1.0):
	[img, lens] = GetImages(Ngal, Nsources, makelens)
	return img+lens

def GetMultiChannelImage(Ngal, Nsources, makelens, Nchannel=3, LF=[1.5, 1.0, 0.5], IF=[0.5, 1.0, 1.5], \
						zl = 0.5, zs=1.0):
	[img, lens] = GetImages(Ngal, Nsources, makelens, zl=zl, zs=zs)
	nimg = np.ndarray((Nchannel, len(img), len(img)))
	for i in range(Nchannel):
		nimg[i] = lens*LF[i] + img*IF[i]
	return nimg

def GetSamples(Nsamples, Ngal, Nsources, makelens):
	data = []
	for i in range(Nsamples):
		data.append(GetImage(Ngal, Nsources, makelens))
	return np.array(data)

def MakeTrainingSample(NsamplesTrue, NsamplesFalse, Ngal, Nsources):
	data = []
	for i in range(NsamplesFalse):
		data.append(GetImage(Ngal, Nsources, False))
	for j in range(NsamplesTrue):
		data.append(GetImage(Ngal, Nsources, True))

	data = np.array(data)

	Y0 = np.zeros((NsamplesFalse), dtype=int)
	Y1 = np.ones((NsamplesTrue), dtype=int)

	Y = np.concatenate((Y0,Y1))

	arr = np.arange(NsamplesTrue+NsamplesFalse)
	np.random.shuffle(arr)

	xtrain = data[arr]
	ytrain = Y[arr]
	print "Shape of X_train: ", np.shape(xtrain)
	print "Shape of Y_train: ", np.shape(ytrain)
	return [xtrain, ytrain]


def MakeMultiChannelSample(NsamplesTrue=10, NsamplesFalse=5, Nchannel=3, Ngal=1, \
						Nsources=1, LF=[1.5, 1.0, 0.5], IF=[0.5, 1.0, 1.5], \
						SingleRedshift=True, zl=0.5, zs=1.0):
	data = []
	if SingleRedshift:
		for i in range(NsamplesFalse):
			XX = GetMultiChannelImage(Ngal, Nsources, False, Nchannel, LF, IF, zl, zs)
			data.append(XX)
		for j in range(NsamplesTrue):
			YY = GetMultiChannelImage(Ngal, Nsources, True, Nchannel, LF, IF, zl, zs)
			data.append(YY)
	else:
		zl = np.random.normal(zl, 0.1, NsamplesTrue+NsamplesFalse)
		zs = np.random.normal(zs, 0.2, NsamplesTrue+NsamplesFalse)
		for i in range(NsamplesFalse):
			XX = GetMultiChannelImage(Ngal, Nsources, False, Nchannel, LF, IF, zl[i], zs[i])
			data.append(XX)
		for j in range(NsamplesTrue):
			YY = GetMultiChannelImage(Ngal, Nsources, True, Nchannel, LF, IF, \
									zl[NsamplesFalse+j], zs[NsamplesFalse+j])
			data.append(YY)		

	data = np.array(data)

	Y0 = np.zeros((NsamplesFalse), dtype=int)
	Y1 = np.ones((NsamplesTrue), dtype=int)

	Y = np.concatenate((Y0,Y1))

	arr = np.arange(NsamplesTrue+NsamplesFalse)
	np.random.shuffle(arr)

	xtrain = data[arr]
	ytrain = Y[arr]

	[xtrain, ytrain] = DeleteNaN(xtrain, ytrain)

	print "Shape of X_train: ", np.shape(xtrain)
	print "Shape of Y_train: ", np.shape(ytrain)
	return [xtrain, ytrain]


def DeleteNaN(X_train, y_train):
   # search for nan elements
   X_check_nan = np.isnan(X_train[:,0, 0, 0])
   ind_nan = np.where(X_check_nan == True)[0]

   # remove Nan elements
   if len(ind_nan) > 0:
       X_train = np.delete(X_train, ind_nan, axis=0)
       y_train = np.delete(y_train, ind_nan, axis=0)

   return X_train, y_train

#==========================================================

if __name__=="__main__":

	[xtrain, ytrain] = MakeMultiChannelSample(5000, 5000, 3, 1, 1, [1.0/2.3, 1, 2.3], [2.3, 1, 1.0/2.3], SingleRedshift=False)
	np.save('xtrain.npy', xtrain)
	np.save('ytrain.npy', ytrain)


	# [xtrain, ytrain] = MakeTrainingSample(2500,2500,2,1)
	# np.save('xtrain.npy', xtrain)
	# np.save('ytrain.npy', ytrain)

	# img = GetImage(10, 2, False)

	# data_true = GetSamples(20, 1, 1, True)
	# np.save('data_true.npy', data_true)

	# data_false = GetSamples(20, 1, 1, False)
	# np.save('data_false.npy', data_false)

	# d = GetImage(3, 2, True)
	# plt.imshow(d, cmap='Greys')
	# plt.show()




	
