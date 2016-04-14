lens/new/mplummers z(0.50) lens.gs
lensplane/new/local -10.00 -10.00 10.00 10.00 32.00 32.00
lensplane/plotdens/fits lens.fits -10.00 -10.00 10.00 10.00 32.00 32.00
srcplane/new z(1.000) zz(0.500,1.000)
imgplane/new/local -10.000 -10.000 10.000 10.000 33 33
import sources.gs
imgplane/plot/fits imgplane.fits
