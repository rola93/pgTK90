#!/bin/sh
echo "make_gif.sh <nombre_final> <archivo.ogv>"
echo "Por defecto: <nombre_final>=out <archivo.ogv>=out.ogv"

mplayer -ao null ${2:-out.ogv} -vo jpeg:outdir=${1:-out}
convert ${1:-out}/* ${1:-out}.gif
rm -r ${1:-out}

# https://askubuntu.com/questions/107726/how-to-create-animated-gif-images-of-a-screencast

# http://www.ubuntu-guia.com/2009/07/grabar-escritorio-en-ubuntu-904.html

