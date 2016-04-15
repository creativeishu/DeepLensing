lens/new/mplummers z(0.50) lens.gs
lensplane/new/local -10.00 -10.00 10.00 10.00 200.00 200.00
lensplane/plotdens/fits lens.fits -10.00 -10.00 10.00 10.00 200.00 200.00
lensplane/plotdens/gnuplot lens.gnuplot -10.00 -10.00 10.00 10.00 200.00 200.00 no yes
exec "gnuplot lens.gnuplot > lens.eps"


srcplane/new z(1.000) zz(0.500,1.000)
imgplane/new/local -10.000 -10.000 10.000 10.000 201 201
import sources.gs
imgplane/plot/fits imgplane.fits
imgplane/plot/gnuplot imgplane.gnuplot yes yes yes yes X Y yes 
exec "gnuplot imgplane.gnuplot > imgplane.eps"
