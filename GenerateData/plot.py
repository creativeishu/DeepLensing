import numpy as np 
import matplotlib.pyplot as plt 
from subprocess import call
from sys import exit
from random import random
import os
np.random.seed(123224)

Ngal = 10

xmin = -2
xmax = 2
ymin = -2
ymax = 2
minmass = 11.5
maxmass = 12

posX = np.random.uniform(xmin/2, xmax/2, Ngal)
posY = np.random.uniform(ymin/2, ymax/2, Ngal)

mass = 10**np.random.uniform(minmass, maxmass, Ngal)
width = np.random.uniform(0, (xmax-xmin)/20.0, Ngal)

def GenLensFile(filename="lens.gs"):
	for i in range(Ngal):
		if i==0:
			call("echo %1.3e %1.3f %1.3f %1.3f > %s"%(mass[i], width[i], posX[i], posY[i], filename), shell=True)
		else:
			call("echo %1.3e %1.3f %1.3f %1.3f >> %s"%(mass[i], width[i], posX[i], posY[i], filename), shell=True)

def GenMainFile(filename="gen.gs", lensfilename="lens.gs", Dl=500.0, Ds=1500.0, Dls=800.0,\
			xmin=-2, xmax=2, ymin=-2, ymax=2, xpix=512, ypix=512, sourceX=0.2, sourceY=0.3, sourceR=0.05):
	call("echo lens/new/mplummers %1.2f %s > %s"%(Dl, lensfilename, filename), shell=True)
	call("echo srcplane/new %1.3f %1.3f >> %s"%(Ds, Dls, filename), shell=True)
	call("echo imgplane/new/local %1.3f %1.3f %1.3f %1.3f %i %i >> %s"%(xmin, ymin, xmax, ymax, xpix, ypix, filename), shell=True)
	call("echo sources/add/circle 0 %1.3f %1.3f 1 %1.3f >> %s"%(sourceX, sourceY, sourceR, filename), shell=True)
	call("echo imgplane/plot/gnuplot imgplane.gnuplot yes no no no X Y no >> %s"%filename, shell=True)

GenLensFile()
GenMainFile(sourceX=posX[0], sourceY=posY[0], sourceR=1.0)
print "Files generated, now running..."
call(["graleshell", "gen.gs"])

imgdata = np.genfromtxt('imgplane.gnuplot', skip_header=7, skip_footer=1)
print np.shape(imgdata)

plt.figure(figsize=(7,7))
plt.scatter(posX, posY, s=(mass/1e11)**2, color='k')
plt.scatter(imgdata[:,0], imgdata[:,1], s=imgdata[:,2]*100, color='r')
plt.xlim(xmin, xmax)
plt.ylim(ymin, ymax)
plt.savefig('test.jpg')
plt.show()
