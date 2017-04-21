import sys, os
import Z80, video, load
import numpy as np

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

def save_state(path='state_dump'):
	f = open(path, 'w')
	# **Main registers
	f.write(str(Z80._A) + str('\n'))
	f.write(str(Z80._HL) + str('\n'))
	f.write(str(Z80._B) + str('\n'))
	f.write(str(Z80._C) + str('\n'))
	f.write(str(Z80._DE) + str('\n'))
	f.write(str(Z80.fS) + str('\n'))
	f.write(str(Z80.fZ) + str('\n'))
	f.write(str(Z80.f5) + str('\n'))
	f.write(str(Z80.fH) + str('\n'))
	f.write(str(Z80.f3) + str('\n'))
	f.write(str(Z80.fPV) + str('\n'))
	f.write(str(Z80.fN) + str('\n'))
	f.write(str(Z80.fC) + str('\n'))
	# ** Alternate registers
	f.write(str(Z80._AF_) + str('\n'))
	f.write(str(Z80._HL_) + str('\n'))
	f.write(str(Z80._BC_) + str('\n'))
	f.write(str(Z80._DE_) + str('\n'))
	# ** Index registers - ID used as temporary for ix/iy
	f.write(str(Z80._IX) + str('\n'))
	f.write(str(Z80._IY) + str('\n'))
	f.write(str(Z80._ID) + str('\n'))
	# ** Stack Pointer and Program Counter
	f.write(str(Z80._SP) + str('\n'))
	f.write(str(Z80._PC) + str('\n'))
	# ** Interrupt and Refresh registers
	f.write(str(Z80._I) + str('\n'))
	f.write(str(Z80._R) + str('\n'))
	f.write(str(Z80._R7) + str('\n'))
	# ** Interrupt flip-flops
	f.write(str(Z80._IFF1) + str('\n'))
	f.write(str(Z80._IFF2) + str('\n'))
	f.write(str(Z80._IM) + str('\n'))
	# ** Memory
	x =np.array(Z80.mem)
	np.savetxt(path + '_mem', x)
	#mem = [0] * 65536
	f.close()

def load_state(path):
	# global _A, _HL, _B, _C,_DE, fS, fZ,f5, fH,f3,fPV,fN,fC,_AF_,\
	#     _HL_,_BC_,_DE_, _IX, _IY, _ID,_SP,_PC,_I, _R, _R7,_IFF1,_IFF2,_IM, mem
	f = open(path, 'r')
	l =f.readlines()
	# **Main registers
	Z80._A = int(l[0])
	Z80._HL = int(l[1])
	Z80._B = int(l[2])
	Z80._C = int(l[3])
	Z80._DE = int(l[4])
	Z80.fS = l[5]== 'True'
	Z80.fZ = l[6]== 'True'
	Z80.f5 = l[7]== 'True'
	Z80.fH = l[8]== 'True'
	Z80.f3 = l[9]== 'True'
	Z80.fPV =l[10]== 'True'
	Z80.fN = l[11]== 'True'
	Z80.fC = l[12]== 'True'
	# ** Alternate registers
	Z80._AF_ = int(l[13])
	Z80._HL_ = int(l[14])
	Z80._BC_ = int(l[15])
	Z80._DE_ = int(l[16])
	# ** Index registers - ID used as temporary for ix/iy
	Z80._IX = int(l[17])
	Z80._IY = int(l[18])
	Z80._ID = int(l[19])
	# ** Stack Pointer and Program Counter
	Z80._SP = int(l[20])
	Z80._PC = int(l[21])
	# ** Interrupt and Refresh registers
	Z80._I = int(l[22])
	Z80._R = int(l[23])
	Z80._R7 = int(l[24])
	# ** Interrupt flip-flops
	Z80._IFF1 = l[25] == 'True'
	Z80._IFF2 = l[26] == 'True'
	Z80._IM = int(l[27])
	# ** Memory
	x= np.loadtxt(path + '_mem')
	Z80.mem = x.astype(int)
	f.close()
