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

def GenMainFile(filename="gen.gs", lensfilename="lens.gs", sourcefilename="sources.gs", zl=0.5, zs=1.0,\
			xmin=-5, xmax=5, ymin=-5, ymax=5, xpix=32, ypix=32):

	call("echo lens/new/mplummers z\(%1.2f\) %s > %s"%(zl, lensfilename, filename), shell=True)
	call("echo lensplane/new/local %1.2f %1.2f %1.2f %1.2f %1.2f %1.2f >> %s"%(xmin, ymin, xmax, ymax, xpix, ypix, filename), shell=True)
	# call("echo lensplane/plotdens/gnuplot lens.gnuplot %1.2f %1.2f %1.2f %1.2f %1.2f %1.2f no no >> %s"%(xmin, ymin, xmax, ymax, xpix, ypix, filename), shell=True)
	# call("echo exec \'gnuplot lens.gnuplot > lens.eps \' >>%s"%filename, shell=True)
	call("echo lensplane/plotdens/fits lens.fits %1.2f %1.2f %1.2f %1.2f %1.2f %1.2f >> %s"%(xmin, ymin, xmax, ymax, xpix, ypix, filename), shell=True)

	call("echo srcplane/new z\(%1.3f\) zz\(%1.3f,%1.3f\) >> %s"%(zs, zl, zs, filename), shell=True)
	call("echo imgplane/new/local %1.3f %1.3f %1.3f %1.3f %i %i >> %s"%(xmin, ymin, xmax, ymax, xpix+1, ypix+1, filename), shell=True)

	call("echo import %s >> %s"%(sourcefilename, filename), shell=True)

	# call("echo imgplane/plot/gnuplot imgplane.gnuplot yes yes no no X Y yes >> %s"%filename, shell=True)
	# call("echo exec \"gnuplot imgplane.gnuplot > imgplane.eps\" >>%s"%filename, shell=True)
	call("echo imgplane/plot/fits imgplane.fits >> %s"%filename, shell=True)

def GenAllFiles(Ngal, Nsources, makelens):
	[mass, width, posX, posY] = LensParams(Ngal)
	GenLensFile("lens.gs", Ngal, mass, width, posX, posY)
	[sourcesX, sourcesY, sourcesR] = SourceParams(Nsources, Ngal, makelens, posX, posY)
	GenSourceFile(Nsources, sourcesX, sourcesY, sourcesR)
	GenMainFile()


def GetImages(Ngal, Nsources, makelens):
	GenAllFiles(Ngal, Nsources, makelens)
	call(["graleshell", "gen.gs"])
	img = fits2data('imgplane.fits')#/2.0
	lens = fits2data('lens.fits')
	return [img, lens]

def GetImage(Ngal, Nsources, makelens):
	[img, lens] = GetImages(Ngal, Nsources, makelens)
	return img+lens

def GetSamples(Nsamples, Ngal, Nsources, makelens):
	data = []
	for i in range(Nsamples):
		data.append(GetImage(Ngal, Nsources, makelens))
		# plt.imshow(data[i], cmap='Greys')
		# plt.colorbar()
		# plt.show()
	return np.array(data)

def MakeTrainingSample(NsamplesTrue, NsamplesFalse, Ngal, Nsources):
	data = []
	for i in range(NsamplesFalse):
		data.append(GetImage(Ngal, Nsources, False))
	for j in range(NsamplesTrue):
		data.append(GetImage(Ngal, Nsources, True))

	data = np.array(data)

	Y0 = np.zeros((NsamplesFalse))
	Y1 = np.ones((NsamplesTrue))

	Y = np.concatenate((Y0,Y1))

	arr = np.arange(NsamplesTrue+NsamplesFalse)
	np.random.shuffle(arr)

	xtrain = data[arr]
	ytrain = Y[arr]
	print "Shape of X_train: ", np.shape(xtrain)
	print "Shape of Y_train: ", np.shape(ytrain)
	return [xtrain, ytrain]


#==========================================================

if __name__=="__main__":

	[xtrain, ytrain] = MakeTrainingSample(500,500,10,2)
	np.save('xtrain.npy', xtrain)
	np.save('ytrain.npy', ytrain)

	# img = GetImage(10, 2, False)

	# data_true = GetSamples(20, 10, 2, True)
	# np.save('data_true.npy', data_true)

	# data_false = GetSamples(20, 10, 2, False)
	# np.save('data_false.npy', data_false)

	# d = GetImage(3, 2, True)
	# plt.imshow(d, cmap='Greys')
	# plt.show()




	
