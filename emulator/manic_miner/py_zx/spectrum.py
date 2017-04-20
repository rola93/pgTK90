import sys, os
import Z80, load

#comentar o descomentar segun sistema operativo
import video as video #run on ubuntu
#import videoAle as video #run on mac


def execute():
	Z80.execute()

def put_key(k):
	Z80.put_key(k)

def render():
	video.update()

def close():
	video.close()
	reload(Z80)

def program_counter(value):
	Z80.PC(value)

def get_frame_as_array():
	return video.get_frame_as_array()

def initialize(game_romfile, iterruption_freccuency_mhz=3.5):
	video.init()
	Z80.Z80(iterruption_freccuency_mhz) #MhZ
	dir_path = os.path.dirname(os.path.realpath(__file__))
	_load_rom(dir_path + '/48-modified.rom')
	Z80.reset()
	Z80.outb( 254, 0xff, 0 ) #white border on startup

	sys.setcheckinterval(255) #we don't use threads, kind of speed up
	load.loadZ80(game_romfile)

def _load_rom(romfile):
	rom = open(romfile, 'rb').read()
	#rom = test_programm()
	for index,item in enumerate(rom):
		op = ord(item)
		#op = item
		Z80.mem[index] = (op+256)&0xff
	print 'Loaded %d bytes of ROM' % (len(rom))