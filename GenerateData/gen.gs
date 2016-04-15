lens/new/mplummers z(0.50) lens.gs
lensplane/new/local -5.00 -5.00 5.00 5.00 32.00 32.00
lensplane/plotdens/fits lens.fits -5.00 -5.00 5.00 5.00 32.00 32.00
srcplane/new z(1.000) zz(0.500,1.000)
imgplane/new/local -5.000 -5.000 5.000 5.000 33 33
import sources.gs
imgplane/plot/fits imgplane.fits
