import pygame, Z80
from pygame.locals import *


xscale = 1
yscale = 1


SCREEN_WIDTH=256*xscale; SCREEN_HEIGHT=192*yscale
CENTER_X=SCREEN_WIDTH/2; CENTER_Y=SCREEN_HEIGHT/2

sat = 238
norm = 128

black = (0,0,0)
blue = (0,0,norm)
red = (norm, 0, 0)
magenta = (norm, 0, norm)
green = (0, norm, 0)
cyan = (0, norm, norm)
yellow = (norm, norm, 0)
white = (norm, norm, norm)

brightColors = [(0,0,0),(0,0,sat),(sat,0,0),(sat,0,sat),(0,sat,0),(0,sat,sat),(sat,sat,0),(sat,sat,sat),
black,blue,red,magenta,green,cyan,yellow,white]


borderWidth = 20   # absolute, not relative to pixelScale
pixelScale  = 1    # scales pixels in main screen, not border

nPixelsWide = 256
nPixelsHigh = 192
nCharsWide  = 32
nCharsHigh  = 24

firstAttr = (nPixelsHigh*nCharsWide)
lastAttr  = firstAttr + (nCharsHigh*nCharsWide)

first = -1
FIRST = -1
last = range((nPixelsHigh+nCharsHigh)*nCharsWide)
next = range((nPixelsHigh+nCharsHigh)*nCharsWide)


buf_start = 16384
buf_end = 22527
buf_length = buf_end - buf_start + 1
attr_start = 22528
attr_end = 23295


def refreshWholeScreen():
	for i in xrange(firstAttr): 
		next[ i ] = i-1
		last[ i ] = (~mem[ i+16384 ]) & 0xff
	for i in range (firstAttr, lastAttr):
		next[ i ] = -1
		last[ i ] = mem[ i+16384 ]
	first = firstAttr - 1;
	FIRST = -1

def init():
	global screen, screen_map
	pygame.init()
	screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))#, pygame.FULLSCREEN)
	pygame.display.set_caption("ZX Spectrum")
	pygame.mouse.set_cursor((8,8), (0,0), (0,)*(64/8), (0,)*(64/8)) #Pygame trick, no visible cursor
	screen_map = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
	pygame.display.flip()
	return


def fill_screen_map():
	global screen, Z80
	set_at = screen.set_at
	mem = Z80.mem
	for addr in xrange(buf_start, buf_end + 1):
		y = ((addr & 0x00e0) >> 2) + ((addr&0x0700) >> 8) +((addr&0x1800) >> 5)
		sx = (addr & 0x1f) << 3

		#ax = (sx >> 5)
		#ay = (y >> 6) + (y >> 5)#y / 24 = y/64 + y/32 #(64-32=24)
		#attr = mem[buf_start +16384 + (ay<<5) + ax] #(ay << 5) + ax]

		attr = mem[ 22528 + (addr&0x1f) + ((y>>3)*32)]
		bright = ((attr>>3) & 0x08)
		ink = ((attr   ) & 0x07) | bright
		pap = ((attr>>3) & 0x07) | bright

		byte = mem[addr]

		if (1 << 7) & byte: color = ink
		else: color = pap
		set_at((sx, y), brightColors[color])
		sx += 1
		if (1 << 6) & byte: color = ink
		else: color = pap
		set_at((sx, y), brightColors[color])
		sx += 1
		if (1 << 5) & byte: color = ink
		else: color = pap
		set_at((sx, y), brightColors[color])
		sx += 1
		if (1 << 4) & byte: color = ink
		else: color = pap
		set_at((sx, y), brightColors[color])
		sx += 1
		if (1 << 3) & byte: color = ink
		else: color = pap
		set_at((sx, y), brightColors[color])
		sx += 1
		if (1 << 2) & byte: color = ink
		else: color = pap
		set_at((sx, y), brightColors[color])
		sx += 1
		if (1 << 1) & byte: color = ink
		else: color = pap
		set_at((sx, y), brightColors[color])
		sx += 1
		if 1 & byte: color = ink
		else: color = pap
		set_at((sx, y), brightColors[color])

		#for bit in xrange(8):
		#	if (1 << (7-bit)) & byte:
		#		color = brightColors[ink]
		#	else:
		#		color = brightColors[pap]
		#	x = sx + bit
		#	#rect = (x*xscale, y*yscale, xscale, yscale)
		#	#screen.fill(color, rect)
		#	set_at((x,y),color)

def update():
	pygame.display.flip()

def close():
	pygame.quit()

def get_frame_as_array():
	fill_screen_map()
	return pygame.surfarray.array3d(screen)

