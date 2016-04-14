import numpy as np 
import matplotlib.pyplot as plt 
from subprocess import call
from sys import exit
from random import random
import os
np.random.seed(123224)

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

def LensParams(Ngal=5, xmin=-10, xmax=10, ymin=-10, ymax=10, minmass=11.0, maxmass=11.5):
	posX = np.random.uniform(xmin/2, xmax/2, Ngal)
	posY = np.random.uniform(ymin/2, ymax/2, Ngal)
	mass = 10**np.random.uniform(minmass, maxmass, Ngal)
	width = np.random.uniform(0, (xmax-xmin)/20.0, Ngal)
	return [mass, width, posX, posY]

def SourceParams(Nsources, Ngal, makelens, posX, posY):
	if makelens:
		source_distance = 0.01
	else:
		source_distance = 1.0

	ind = np.random.choice(Ngal, Nsources, replace=False)
	sourcesX = np.zeros((Nsources))
	sourcesY = np.zeros((Nsources))
	for i in range(Nsources):
		sourcesX[i] = np.random.normal(loc=posX[ind[i]], scale=source_distance)
		sourcesY[i] = np.random.normal(loc=posY[ind[i]], scale=source_distance)
	sourcesR = np.random.normal(loc=0.5, scale=0.1, size=Nsources)
	return [sourcesX, sourcesY, sourcesR]

def GenMainFile(filename="gen.gs", lensfilename="lens.gs", sourcefilename="sources.gs", zl=0.5, zs=1.0,\
			xmin=-10, xmax=10, ymin=-10, ymax=10, xpix=32, ypix=32):

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
	img = fits2data('imgplane.fits')
	lens = fits2data('lens.fits')
	return [img, lens]

def GetImage(Ngal, Nsources, makelens):
	[img, lens] = GetImages(Ngal, Nsources, makelens)
	return img+lens

def GetSamples(Nsamples, Ngal, Nsources, makelens):
	data = []
	for i in range(Nsamples):
		data.append(GetImage(Ngal, Nsources, makelens))
	return np.array(data)

#==========================================================

if __name__=="__main__":
	data = GetSamples(10, 10, 2, True)
	print np.shape(data)







	
