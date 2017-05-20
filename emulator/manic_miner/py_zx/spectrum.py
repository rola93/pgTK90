import sys, os
import Z80, load
import pickle
import copy

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

def initialize(game_romfile, iterruption_freccuency_mhz=3.5, crop=(0, 0, 0, 0)):
	video.init(crop=crop)
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

def save_array_state(path=None):
	core_state = []
	# **Main registers
	core_state.append(Z80._A)#0
	core_state.append(Z80._HL)#1
	core_state.append(Z80._B)#2
	core_state.append(Z80._C)#3
	core_state.append(Z80._DE)#4
	core_state.append(Z80.fS)#5
	core_state.append(Z80.fZ)#6
	core_state.append(Z80.f5)#7
	core_state.append(Z80.fH)#8
	core_state.append(Z80.f3)#9
	core_state.append(Z80.fPV)#10
	core_state.append(Z80.fN)#11
	core_state.append(Z80.fC)#12
	# ** Alternate registers
	core_state.append(Z80._AF_)#13
	core_state.append(Z80._HL_)#14
	core_state.append(Z80._BC_)#15
	core_state.append(Z80._DE_)#16
	# ** Index registers - ID used as temporary for ix/iy
	core_state.append(Z80._IX)#17
	core_state.append(Z80._IY)#18
	core_state.append(Z80._ID)#19
	# ** Stack Pointer and Program Counter
	core_state.append(Z80._SP)#20
	core_state.append(Z80._PC)#21
	# ** Interrupt and Refresh registers
	core_state.append(Z80._I)#22
	core_state.append(Z80._R)#23
	core_state.append(Z80._R7)#24
	# ** Interrupt flip-flops
	core_state.append(Z80._IFF1)#25
	core_state.append(Z80._IFF2)#26
	core_state.append(Z80._IM)#27

	# ** Memory
	core_state.append(Z80.mem)#28

	if path:
		with open(path, "wb") as fp:  # Pickling
			pickle.dump(core_state, fp)

	return core_state


def load_array_state_from_file(path='state_dump'):
	with open(path, "rb") as fp:  # Unpickling
		b = pickle.load(fp)
	return  b

def load_array_state(core_state_read_only):
	# global _A, _HL, _B, _C,_DE, fS, fZ,f5, fH,f3,fPV,fN,fC,_AF_,\
	#     _HL_,_BC_,_DE_, _IX, _IY, _ID,_SP,_PC,_I, _R, _R7,_IFF1,_IFF2,_IM, mem
	# **Main registers
	core_state = copy.deepcopy(core_state_read_only)
	Z80._A = core_state[0]
	Z80._HL = core_state[1]
	Z80._B = core_state[2]
	Z80._C = core_state[3]
	Z80._DE = core_state[4]
	Z80.fS = core_state[5]
	Z80.fZ = core_state[6]
	Z80.f5 = core_state[7]
	Z80.fH = core_state[8]
	Z80.f3 = core_state[9]
	Z80.fPV = core_state[10]
	Z80.fN = core_state[11]
	Z80.fC = core_state[12]
	# ** Alternate registers
	Z80._AF_ = core_state[13]
	Z80._HL_ = core_state[14]
	Z80._BC_ = core_state[15]
	Z80._DE_ = core_state[16]
	# ** Index registers - ID used as temporary for ix/iy
	Z80._IX = core_state[17]
	Z80._IY = core_state[18]
	Z80._ID = core_state[19]
	# ** Stack Pointer and Program Counter
	Z80._SP = core_state[20]
	Z80._PC = core_state[21]
	# ** Interrupt and Refresh registers
	Z80._I = core_state[22]
	Z80._R = core_state[23]
	Z80._R7 = core_state[24]
	# ** Interrupt flip-flops
	Z80._IFF1 = core_state[25]
	Z80._IFF2 = core_state[26]
	Z80._IM = core_state[27]
	# ** Memory
	Z80.mem = (core_state[28])