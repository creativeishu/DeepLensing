lens/new/mplummers z(0.712) lens.gs
lensplane/new/local -5.00 -5.00 5.00 5.00 32.00 32.00
lensplane/plotdens/fits lens.fits -5.00 -5.00 5.00 5.00 32.00 32.00
srcplane/new z(0.961) zz(0.712,0.961)
imgplane/new/local -5.000 -5.000 5.000 5.000 33 33
import sources.gs
imgplane/plot/fits imgplane.fits
