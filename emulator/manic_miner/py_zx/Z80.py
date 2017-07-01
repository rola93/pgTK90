tstatesPerInterrupt = 0

#Service for Python limitations
def iif(x, a, b):
	if x:
		return a
	else:
		return b

def xbits(a):
	for i in xrange(8):
		yeild ((a >> i) & 0x01)

#def byte(a): #from 32int to signed 8byte
#	if a > 127: 
#		return a - 256
#	return a

#another very fast version for signed Byte
def byte(a):
	return (a > 127) and (a - 256) or a
#---------------------------------

def Z80(clockFrequencyInMHz):
	global tstatesPerInterrupt
	#50Hz for main interrupt signal
	tstatesPerInterrupt = int((clockFrequencyInMHz * 1e6) / 50)

IM0 = 0
IM1 = 1
IM2 = 2

F_C  = 0x01
F_N  = 0x02
F_PV = 0x04
F_3  = 0x08
F_H  = 0x10
F_5  = 0x20
F_Z  = 0x40
F_S  = 0x80

PF = F_PV
p_ = 0

#Warning: TODO
parity = [False] * 256
for i in range(256):
	p = True
	for j in range(8):
		if ( (i & (1<<j)) != 0 ):
			p = not p
	parity[ i ] = p


#**Main registers
_A = 0; _HL = 0; _B = 0; _C = 0; _DE = 0
fS = False; fZ  = False; f5 = False; fH = False
f3 = False; fPV = False; fN = False; fC = False

#** Alternate registers
_AF_ = 0; _HL_ = 0; _BC_ = 0; _DE_ = 0;

#** Index registers - ID used as temporary for ix/iy 
_IX = 0; _IY = 0; _ID = 0

#** Stack Pointer and Program Counter
_SP = 0; _PC = 0

#** Interrupt and Refresh registers
_I = 0; _R = 0; _R7 = 0

#** Interrupt flip-flops
_IFF1 = True; _IFF2 = True
_IM = 2;

#** Memory
mem = [0] * 65536 

#** 16 bit register access
def AFget(): 
	return (_A << 8) | Fget()
def AF(word):
	A(word >> 8)
	F(word & 0xff)

def BCget():
	return (_B << 8) |_C
def BC(word):
	B(word >> 8)
	C(word & 0xff)

def  DEget(): return _DE
def DE( word ):
		global _DE
		_DE = word;


def  HLget(): return _HL
def HL( word ):
		global _HL
		_HL = word;


def  PCget() : return _PC
def PC( word ):
		global _PC
		_PC = word;


def  SPget(): return _SP
def SP( word ):
		global _SP
		_SP = word;


def  IDget(): return _ID
def ID( word ):
		global _ID
		_ID = word;


def  IXget(): return _IX
def IX( word ):
		global _IX
		_IX = word;


def  IYget(): return _IY
def IY( word ):
		global _IY
		_IY = word;



# 8 bit register access 
#def  Aget(): return _A
def A( bite ):	
		global _A
		_A = bite;


def Fget():
		return	iif(fS  , F_S  , 0)  |\
			iif(fZ  , F_Z  , 0)  |\
			iif(f5      , F_5  , 0)  |\
			iif(fH  , F_H  , 0)  |\
			iif(f3      , F_3  , 0)  |\
			iif(fPV , F_PV , 0)  |\
			iif(fN  , F_N  , 0)  |\
			iif(fC  , F_C  , 0)

def F( bite ):
		global fS, fZ, f5, fH, f3, fPV, fN, fC
		fS  = (bite & F_S)#  != 0;
		fZ  = (bite & F_Z)#  != 0;
		f5  = (bite & F_5)#  != 0;
		fH  = (bite & F_H)#  != 0;
		f3  = (bite & F_3)#  != 0;
		fPV = (bite & F_PV)# != 0;
		fN  = (bite & F_N)#  != 0;
		fC  = (bite & F_C)#  != 0;



#def  Bget(): return _B
def B( bite ):
		global _B
		_B = bite;

#def Cget(): return _C
def C( bite ):
		global _C
		_C = bite;


def  Dget(): return (_DE >> 8)
def D( bite ):
		global _DE
		_DE = (bite << 8) | (_DE & 0x00ff);

def  Eget(): return (_DE & 0xff)
def E( bite ):
		global _DE
		_DE = (_DE & 0xff00) | bite;


def  Hget(): return (_HL >> 8)
def H( bite ):
		global _HL
		_HL = (bite << 8) | (_HL & 0x00ff);

def  Lget(): return (_HL & 0xff)
def L( bite ):
		global _HL
		_HL = (_HL & 0xff00) | bite;


def  IDHget(): return (_ID >> 8) #not used
def IDH( bite ):
		global _ID
		_ID = (bite << 8) | (_ID & 0x00ff);

def  IDLget(): return (_ID & 0xff)
def IDL( bite ):
		global _ID
		_ID = (_ID & 0xff00) | bite;



# Memory refresh register 
def  R7(): return _R7
def  Rget(): return (_R & 0x7f) | _R7
def R( bite ):
		global _R, _R7
		_R  = bite;
		_R7 = bite & 0x80;


#def REFRESH (t)
#		global _R
#		_R += t



# Interrupt modes/register 
def  Iget(): return _I
def I( bite ):
		global _I
		_I = bite;


def IFF1get(): return _IFF1
def IFF1( iff1 ):
		global _IFF1
		_IFF1 = iff1;


def IFF2get(): return _IFF2
def IFF2( iff2 ):
		global _IFF2
		_IFF2 = iff2;


def IMget(): return _IM
def IM( im ):
		global _IM
		_IM = im;



# Flag access 
def setZ( f ):
	global fZ
	fZ = f
def setC( f ):
	global fC
	fC = f
def setS( f ):
	global fS
	fS = f
def setH( f ):
	global fH
	fH = f
def setN( f ):
	global fN
	fN = f
def setPV( f ):
	global fPV
	fPV = f
def set3( f ):
	global f3
	f3 = f
def set5( f ):
	global f5
	f5 = f

#def Zset(): return fZ
#def Cset(): return fC
#def Sset(): return fS
#def Hset(): return fH
#def Nset(): return fN
#def PVset(): return fPV


# Byte access 
def peekb( addr ):
		return mem[ addr ];

def pokeb( addr, newByte ):
		mem[ addr ] = newByte;



# Word access 
def pokew( addr, word ):
		#pokeb( addr, word & 0xff )
		mem[ addr ] = word & 0xff
		addr+=1
		#pokeb( addr & 0xffff, word >> 8 )
		mem[ addr & 0xffff ] = word >> 8

def peekw( addr ):
		t = peekb( addr );
		addr+=1
		return t | (peekb( addr & 0xffff ) << 8);



# Index register access 
def ID_d():
		#return ((IDget()+(byte)nxtpcb()) & 0xffff);
		return ((IDget()+byte(nxtpcb())) & 0xffff)



# Stack access 
def pushw( word ):
		sp = ((SPget()-2) & 0xffff);
		SP( sp );
		pokew( sp, word );

def popw():
		sp = SPget();
		t  = peekb( sp );
		sp+=1
		t |= (peekb( sp & 0xffff) << 8);
		sp += 1
		SP( sp & 0xffff );
		return t;

    

# Call stack 
def pushpc(): pushw( _PC  )
def poppc()  : PC( popw() )


# Program access 
#WARNING: old one version
#def nxtpcb():
#		pc = _PC 
#		t = peekb( pc )
#		pc += 1
#		PC( pc & 0xffff )
#		return t
def nxtpcb():
		global _PC
		t = mem[_PC]
		_PC += 1
		_PC = _PC & 0xffff
		return t

def nxtpcw():
		pc = _PC 
		t = peekb( pc )
		pc += 1
		t |= ( peekb( pc & 0xffff ) << 8 )
		pc += 1
		PC( pc & 0xffff )
		return t



# Reset all registers to power on state 
def reset():
		PC( 0 );
		SP( 0 );

		A( 0 );
		F( 0 );
		BC( 0 );
		DE( 0 );
		HL( 0 );

		exx();
		ex_af_af();

		A( 0 );
		F( 0 );
		BC( 0 );
		DE( 0 );
		HL( 0 );

		IX( 0 );
		IY( 0 );

		R( 0 );

		I( 0 );
		IFF1( False );
		IFF2( False );
		IM( IM0 );


def show_registers():
	#str = "A:%d\tL:%d\tPC:%d(%s)\tHL:%d\tHget:%d" % (_A, Lget(), _PC , hex(_PC ), _HL, Hget())
	str = "PC:%d(%s)\tHL:%d" % (_PC , hex(_PC ), _HL)
	print str

# IO ports 
def outb( port, bite, tstates ):
		#print "outb(PORT:%d, VAL:%d)" % (port, bite)
		pass


def inb2( port ):
		#print "inb(PORT:%d)" % port
		#print 'inb'
		return 0xff;

global keys_vector

def inb( port ):
	res = 0xff;
	k = keys_vector
	if ( (port & 0x0001) == 0 ):
		if ( (port & 0x8000) == 0 ) : res &= k[0]#_B_SPC
		if ( (port & 0x4000) == 0 ) : res &= k[1]#_H_ENT
		if ( (port & 0x2000) == 0 ) : res &= k[2]#_Y_P   
		if ( (port & 0x1000) == 0 ) : res &= k[3]#_6_0
		if ( (port & 0x0800) == 0 ) : res &= k[4]#_1_5   
		if ( (port & 0x0400) == 0 ) : res &= k[5]#_Q_T   
		if ( (port & 0x0200) == 0 ) : res &= k[6]#_A_G
		if ( (port & 0x0100) == 0 ) : res &= k[7]#_CAPS_V
	return(res)

def put_key(k):
    key_repr = ['NOOP', 'RIGHT', 'UP', 'LEFT', 'RIGHTUP', 'LEFTUP']
    global keys_vector
    keys_vector = [255, 255, 255, 255, 255, 255, 255, 255]

    if isinstance(k, int):
    	k = key_repr[k]

    if k == 'LEFT' or k == 'LEFTUP':
        keys_vector[4] -= 16

    if k == 'UP' or k == 'LEFTUP' or k == 'RIGHTUP':
        keys_vector[3] -= 8

    if k == 'RIGHT' or k == 'RIGHTUP':
        keys_vector[3] -= 4

# Z80 fetch/execute loop 
def execute():
	global _R
	local_tstates = -tstatesPerInterrupt; # -70000
	for _ in [0,1]:
		while ( local_tstates < 0):
			_R += 1 
			opcode = nxtpcb()
			if opcode == 0:    # NOP 
				local_tstates += ( 4 );
				continue
		
			if opcode == 8:    # EX AF,AF' 
				ex_af_af();
				local_tstates += ( 4 );
				continue
		
			if opcode == 16:    # DJNZ dis 
				b = qdec8( _B ) 
				B(b)
				if (b != 0):
					d = byte(nxtpcb())
					PC( (_PC +d)&0xffff )
					local_tstates += ( 13 )
				else :
					PC( inc16( _PC  ) )
					local_tstates += ( 8 )
				continue
		
			if opcode == 24: # JR dis 
				d = byte(nxtpcb())
				PC( (_PC +d)&0xffff )
				local_tstates += ( 12 )
				continue
		
			#WARNING: Rom doesnt work properly ! VM 2005   Java byte must be -128...+127
			# UPDATE: added byte function converter
			# JR cc,dis 
			if opcode == 32:    # JR NZ,dis 
				if not fZ:
					#if ram_filled:
					#	print 'fZ:', fZ
					d = byte(nxtpcb())
					PC( (_PC +d)&0xffff )
					#if _PC  != 4572: 
					#	print '###########', _PC 
					#	print 'd:', d
					#	print '(_PC +d)&0xffff', (_PC +d)&0xffff
					#print '_PC +d)&0xffff:%s' % str((_PC +d)&0xffff)
					local_tstates += ( 12 )
					continue
				else :
					#print 'PC (inc16(_PC )):', PC( inc16( _PC  ) )
					PC( inc16( _PC  ) )
					#print 'NEW PC:', _PC 
					local_tstates += ( 7 )
				continue
		
			if opcode == 40:    # JR Z,dis 
				if ( fZ):
					d = byte(nxtpcb())
					PC( (_PC +d)&0xffff )
					local_tstates += ( 12 )
				else :
					PC( inc16( _PC  ) );
					local_tstates += ( 7 )
				continue
		
			if opcode == 48:    # JR NC,dis 
				if (not fC):
					d = byte(nxtpcb())
					PC( (_PC +d)&0xffff )
					local_tstates += ( 12 )
				else :
					PC( inc16( _PC  ) )
					local_tstates += ( 7 )
				continue
		
			if opcode == 56:    # JR C,dis 
				if ( fC):
					d = byte(nxtpcb())
					PC( (_PC +d)&0xffff )
					local_tstates += ( 12 )
				else :
					PC( inc16( _PC  ) )
					local_tstates += ( 7 )
				continue
		

			# LD rr,nn / ADD HL,rr 
			if opcode == 1:    # LD BCget(),nn 
				BC( nxtpcw() );
				local_tstates += ( 10 );
				continue
		
			if opcode == 9:    # ADD HL,BC 
				HL( add16( _HL, BCget() ) );
				local_tstates += ( 11 );
				continue
		
			if opcode == 17:    # LD DE,nn 
				DE( nxtpcw() );
				local_tstates += ( 10 );
				continue
		
			if opcode == 25:    # ADD HL,DE 
				HL( add16( _HL, DEget() ) );
				local_tstates += ( 11 );
				continue
		
			if opcode == 33:    # LD HL,nn 
				HL( nxtpcw() );
				local_tstates += ( 10 );
				continue
		
			if opcode == 41:    # ADD HL,HL 
				hl = _HL;
				HL( add16( hl, hl ) );
				local_tstates += ( 11 );
				continue
		
			if opcode == 49:    # LD SP,nn 
				SP( nxtpcw() );
				local_tstates += ( 10 );
				continue
		
			if opcode == 57:    # ADD HL,SP 
				HL( add16( _HL, SPget() ) );
				local_tstates += ( 11 );
				continue
		

			# LD (**),A/A,(**) 
			if opcode == 2:    # LD (BC),A 
			 mem[ BCget()] = _A ; local_tstates += ( 7 ); continue
			if opcode == 10:    # LD A,(BC) 
			 A( peekb( BCget() ) ); local_tstates += ( 7 ); continue
			if opcode == 18:    # LD (DE),A 
			 mem[ DEget()] = _A ; local_tstates += ( 7 ); continue
			if opcode == 26:    # LD A,(DE) 
			 A( peekb( DEget() ) ); local_tstates += ( 7 ); continue
			if opcode == 34:    # LD (nn),HL 
			 pokew( nxtpcw(), _HL ); local_tstates += ( 16 ); continue
			if opcode == 42:    # LD HL,(nn) 
			 HL( peekw( nxtpcw() ) ); local_tstates += ( 16 ); continue
			if opcode == 50:    # LD (nn),A 
			 mem[ nxtpcw()] = _A ; local_tstates += ( 13 ); continue
			if opcode == 58:    # LD A,(nn) 
			 A( peekb( nxtpcw() ) ); local_tstates += ( 13 ); continue

			# INC/DEC * 
			if opcode == 3:    # INC BC 
			 BC( inc16( BCget() ) ); local_tstates += ( 6 ); continue
			if opcode == 11:    # DEC BC 
			 BC( dec16( BCget() ) ); local_tstates += ( 6 ); continue
			if opcode == 19:    # INC DE 
			 DE( inc16( DEget() ) ); local_tstates += ( 6 ); continue
			if opcode == 27:    # DEC DE 
			 DE( dec16( DEget() ) ); local_tstates += ( 6 ); continue
			if opcode == 35:    # INC HL 
			 HL( inc16( _HL ) ); local_tstates += ( 6 ); continue
			if opcode == 43:    # DEC HL 
			 HL( dec16( _HL ) ); local_tstates += ( 6 ); continue
			if opcode == 51:    # INC SP 
			 SP( inc16( SPget() ) ); local_tstates += ( 6 ); continue
			if opcode == 59:    # DEC SP 
			 SP( dec16( SPget() ) ); local_tstates += ( 6 ); continue

			# INC * 
			if opcode == 4:    # INC B 
			 B( inc8( _B ) ); local_tstates += ( 4 ); continue
			if opcode == 12:    # INC C 
			 C( inc8(_C ) ); local_tstates += ( 4 ); continue
			if opcode == 20:    # INC D 
			 D( inc8( Dget() ) ); local_tstates += ( 4 ); continue
			if opcode == 28:    # INC E 
			 E( inc8( Eget() ) ); local_tstates += ( 4 ); continue
			if opcode == 36:    # INC H 
			 H( inc8( Hget() ) ); local_tstates += ( 4 ); continue
			if opcode == 44:    # INC L 
			 L( inc8( Lget() ) ); local_tstates += ( 4 ); continue
			if opcode == 52:    # INC (HL) 
				hl = _HL;
				mem[  hl] = inc8( peekb( hl ) )
				local_tstates += ( 11 );
				continue
		
			if opcode == 60:    # INC _A 
			 A( inc8( _A ) ); local_tstates += ( 4 ); continue

			# DEC * 
			if opcode == 5:    # DEC B 
			 B( dec8( _B ) ); local_tstates += ( 4 ); continue
			if opcode == 13:    # DEC C 
			 C( dec8(_C ) ); local_tstates += ( 4 ); continue
			if opcode == 21:    # DEC D 
			 D( dec8( Dget() ) ); local_tstates += ( 4 ); continue
			if opcode == 29:    # DEC E 
			 E( dec8( Eget() ) ); local_tstates += ( 4 ); continue
			if opcode == 37:    # DEC H 
			 H( dec8( Hget() ) ); local_tstates += ( 4 ); continue
			if opcode == 45:    # DEC L 
			 L( dec8( Lget() ) ); local_tstates += ( 4 ); continue
			if opcode == 53:    # DEC (HL) 
			
				hl = _HL;
				mem[  hl] = dec8( peekb( hl ) )
				local_tstates += ( 11 );
				continue
		
			if opcode == 61:    # DEC _A 
			 A( dec8( _A ) ); local_tstates += ( 4 ); continue

			# LD *,N 
			if opcode == 6:    # LD B,n 
			 B( nxtpcb() ); local_tstates += ( 7 ); continue
			if opcode == 14:    # LD C,n 
			 C( nxtpcb() ); local_tstates += ( 7 ); continue
			if opcode == 22:    # LD D,n 
			 D( nxtpcb() ); local_tstates += ( 7 ); continue
			if opcode == 30:    # LD E,n 
			 E( nxtpcb() ); local_tstates += ( 7 ); continue
			if opcode == 38:    # LD H,n 
			 H( nxtpcb() ); local_tstates += ( 7 ); continue
			if opcode == 46:    # LD L,n 
			 L( nxtpcb() ); local_tstates += ( 7 ); continue
			if opcode == 54:    # LD (HL),n 
				mem[  _HL] = nxtpcb()
				local_tstates += ( 10 );
				continue
		
			if opcode == 62:    # LD A,n 
			 A( nxtpcb() ); local_tstates += ( 7 ); continue

			# R**A 
			if opcode == 7: # RLCA 
			 rlc_a(); local_tstates += ( 4 ); continue
			if opcode == 15: # RRCA 
			 rrc_a(); local_tstates += ( 4 ); continue
			if opcode == 23: # RLA 
			 rl_a(); local_tstates += ( 4 ); continue
			if opcode == 31: # RRA 
			 rr_a(); local_tstates += ( 4 ); continue
			if opcode == 39: # DAA 
			 daa_a(); local_tstates += ( 4 ); continue
			if opcode == 47: # CPL 
			 cpl_a(); local_tstates += ( 4 ); continue
			if opcode == 55: # SCF 
			 scf(); local_tstates += ( 4 ); continue
			if opcode == 63: # CCF 
			 ccf(); local_tstates += ( 4 ); continue

			# LD B,* 
			if opcode == 64:    # LD B,B 
			 local_tstates += ( 4 ); continue
			if opcode == 65:    # LD B,C 
			 B(_C ); local_tstates += ( 4 ); continue
			if opcode == 66:    # LD B,D 
			 B( Dget() ); local_tstates += ( 4 ); continue
			if opcode == 67:    # LD B,E 
			 B( Eget() ); local_tstates += ( 4 ); continue
			if opcode == 68:    # LD B,H 
			 B( Hget() ); local_tstates += ( 4 ); continue
			if opcode == 69:    # LD B,L 
			 B( Lget() ); local_tstates += ( 4 ); continue
			if opcode == 70:    # LD B,(HL) 
			 B( peekb( _HL ) ); local_tstates += ( 7 ); continue
			if opcode == 71:    # LD B,A 
			 B( _A ); local_tstates += ( 4 ); continue

			# LD C,* 
			if opcode == 72:    # LD C,B 
			 C( _B ); local_tstates += ( 4 ); continue
			if opcode == 73:    # LD C,C 
			 local_tstates += ( 4 ); continue
			if opcode == 74:    # LD C,D 
			 C( Dget() ); local_tstates += ( 4 ); continue
			if opcode == 75:    # LD C,E 
			 C( Eget() ); local_tstates += ( 4 ); continue
			if opcode == 76:    # LD C,H 
			 C( Hget() ); local_tstates += ( 4 ); continue
			if opcode == 77:    # LD C,L 
			 C( Lget() ); local_tstates += ( 4 ); continue
			if opcode == 78:    # LD C,(HL) 
			 C( peekb( _HL ) ); local_tstates += ( 7 ); continue
			if opcode == 79:    # LD C,A 
			 C( _A ); local_tstates += ( 4 ); continue

			# LD D,* 
			if opcode == 80:    # LD D,B 
			 D( _B ); local_tstates += ( 4 ); continue
			if opcode == 81:    # LD D,C 
			 D(_C ); local_tstates += ( 4 ); continue
			if opcode == 82:    # LD D,D 
			 local_tstates += ( 4 ); continue
			if opcode == 83:    # LD D,E 
			 D( Eget() ); local_tstates += ( 4 ); continue
			if opcode == 84:    # LD D,H 
			 D( Hget() ); local_tstates += ( 4 ); continue
			if opcode == 85:    # LD D,L 
			 D( Lget() ); local_tstates += ( 4 ); continue
			if opcode == 86:    # LD D,(HL) 
			 D( peekb( _HL ) ); local_tstates += ( 7 ); continue
			if opcode == 87:    # LD D,A 
			 D( _A ); local_tstates += ( 4 ); continue

			# LD E,* 
			if opcode == 88:    # LD E,B 
			 E( _B ); local_tstates += ( 4 ); continue
			if opcode == 89:    # LD E,C 
			 E(_C ); local_tstates += ( 4 ); continue
			if opcode == 90:    # LD E,D 
			 E( Dget() ); local_tstates += ( 4 ); continue
			if opcode == 91:    # LD E,E 
			 local_tstates += ( 4 ); continue
			if opcode == 92:    # LD E,H 
			 E( Hget() ); local_tstates += ( 4 ); continue
			if opcode == 93:    # LD E,L 
			 E( Lget() ); local_tstates += ( 4 ); continue
			if opcode == 94:    # LD E,(HL) 
			 E( peekb( _HL ) ); local_tstates += ( 7 ); continue
			if opcode == 95:    # LD E,A 
			 E( _A ); local_tstates += ( 4 ); continue

			# LD H,* 
			if opcode == 96:    # LD H,B 
			 H( _B ); local_tstates += ( 4 ); continue
			if opcode == 97:    # LD H,C 
			 H(_C ); local_tstates += ( 4 ); continue
			if opcode == 98:    # LD H,D 
			 H( Dget() ); local_tstates += ( 4 ); continue
			if opcode == 99:    # LD H,E 
			 H( Eget() ); local_tstates += ( 4 ); continue
			if opcode == 100: # LD H,H 
			 local_tstates += ( 4 ); continue
			if opcode == 101:    # LD H,L 
			 H( Lget() ); local_tstates += ( 4 ); continue
			if opcode == 102:    # LD H,(HL) 
			 H( peekb( _HL ) ); local_tstates += ( 7 ); continue
			if opcode == 103:    # LD H,A 
			 H( _A ); local_tstates += ( 4 ); continue

			# LD L,* 
			if opcode == 104:    # LD L,B 
			 L( _B ); local_tstates += ( 4 ); continue
			if opcode == 105:    # LD L,C 
			 L(_C ); local_tstates += ( 4 ); continue
			if opcode == 106:    # LD L,D 
			 L( Dget() ); local_tstates += ( 4 ); continue
			if opcode == 107:    # LD L,E 
			 L( Eget() ); local_tstates += ( 4 ); continue
			if opcode == 108:    # LD L,H 
			 L( Hget() ); local_tstates += ( 4 ); continue
			if opcode == 109:    # LD L,L 
			 local_tstates += ( 4 ); continue
			if opcode == 110:    # LD L,(HL) 
			 L( peekb( _HL ) ); local_tstates += ( 7 ); continue
			if opcode == 111:    # LD L,A 
			 L( _A ); local_tstates += ( 4 ); continue

			# LD (HL),* 
			if opcode == 112:    # LD (HL),B 
			 mem[_HL] = _B; local_tstates += ( 7 ); continue
			if opcode == 113:    # LD (HL),C 
			 mem[_HL] = _C ; local_tstates += ( 7 ); continue
			if opcode == 114:    # LD (HL),D 
			 mem[_HL] = Dget() ; local_tstates += ( 7 ); continue
			if opcode == 115:    # LD (HL),E 
			 mem[_HL] = Eget() ; local_tstates += ( 7 ); continue
			if opcode == 116:    # LD (HL),H 
			 mem[_HL] = Hget() ; local_tstates += ( 7 ); continue
			if opcode == 117:    # LD (HL),L 
			 mem[_HL] = Lget(); local_tstates += ( 7 ); continue
			if opcode == 118:    # HALT 
				haltsToInterrupt = (((-local_tstates-1) / 4)+1);
				local_tstates += (haltsToInterrupt*4);
				_R += haltsToInterrupt-1 
				continue
		
			if opcode == 119:    # LD (HL),A 
			 mem[_HL] = _A ; local_tstates += ( 7 ); continue

			# LD A,* 
			if opcode == 120:    # LD A,B 
			 A( _B ); local_tstates += ( 4 ); continue
			if opcode == 121:    # LD A,C 
			 A(_C ); local_tstates += ( 4 ); continue
			if opcode == 122:    # LD A,D 
			 A( Dget() ); local_tstates += ( 4 ); continue
			if opcode == 123:    # LD A,E 
			 A( Eget() ); local_tstates += ( 4 ); continue
			if opcode == 124:    # LD A,H 
			 A( Hget() ); local_tstates += ( 4 ); continue
			if opcode == 125:    # LD A,L 
			 A( Lget() ); local_tstates += ( 4 ); continue
			if opcode == 126:    # LD A,(HL) 
			 A( peekb( _HL ) ); local_tstates += ( 7 ); continue
			if opcode == 127:    # LD A,A 
			 local_tstates += ( 4 ); continue

			# ADD A,* 
			if opcode == 128:    # ADD A,B 
			 add_a( _B ); local_tstates += ( 4 ); continue
			if opcode == 129:    # ADD A,C 
			 add_a(_C ); local_tstates += ( 4 ); continue
			if opcode == 130:    # ADD A,D 
			 add_a( Dget() ); local_tstates += ( 4 ); continue
			if opcode == 131:    # ADD A,E 
			 add_a( Eget() ); local_tstates += ( 4 ); continue
			if opcode == 132:    # ADD A,H 
			 add_a( Hget() ); local_tstates += ( 4 ); continue
			if opcode == 133:    # ADD A,L 
			 add_a( Lget() ); local_tstates += ( 4 ); continue
			if opcode == 134:    # ADD A,(HL) 
			 add_a( peekb( _HL ) ); local_tstates += ( 7 ); continue
			if opcode == 135:    # ADD A,A 
			 add_a( _A ); local_tstates += ( 4 ); continue

			# ADC A,* 
			if opcode == 136:    # ADC A,B 
			 adc_a( _B ); local_tstates += ( 4 ); continue
			if opcode == 137:    # ADC A,C 
			 adc_a(_C ); local_tstates += ( 4 ); continue
			if opcode == 138:    # ADC A,D 
			 adc_a( Dget() ); local_tstates += ( 4 ); continue
			if opcode == 139:    # ADC A,E 
			 adc_a( Eget() ); local_tstates += ( 4 ); continue
			if opcode == 140:    # ADC A,H 
			 adc_a( Hget() ); local_tstates += ( 4 ); continue
			if opcode == 141:    # ADC A,L 
			 adc_a( Lget() ); local_tstates += ( 4 ); continue
			if opcode == 142:    # ADC A,(HL) 
			 adc_a( peekb( _HL ) ); local_tstates += ( 7 ); continue
			if opcode == 143:    # ADC A,A 
			 adc_a( _A ); local_tstates += ( 4 ); continue

			# SUB * 
			if opcode == 144:    # SUB B 
			 sub_a( _B ); local_tstates += ( 4 ); continue
			if opcode == 145:    # SUB C 
			 sub_a(_C ); local_tstates += ( 4 ); continue
			if opcode == 146:    # SUB D 
			 sub_a( Dget() ); local_tstates += ( 4 ); continue
			if opcode == 147:    # SUB E 
			 sub_a( Eget() ); local_tstates += ( 4 ); continue
			if opcode == 148:    # SUB H 
			 sub_a( Hget() ); local_tstates += ( 4 ); continue
			if opcode == 149:    # SUB L 
			 sub_a( Lget() ); local_tstates += ( 4 ); continue
			if opcode == 150:    # SUB (HL) 
			 sub_a( peekb( _HL ) ); local_tstates += ( 7 ); continue
			if opcode == 151:    # SUB _A 
			 sub_a( _A ); local_tstates += ( 4 ); continue

			# SBC A,* 
			if opcode == 152:    # SBC A,B 
			 sbc_a( _B ); local_tstates += ( 4 ); continue
			if opcode == 153:    # SBC A,C 
			 sbc_a(_C ); local_tstates += ( 4 ); continue
			if opcode == 154:    # SBC A,D 
			 sbc_a( Dget() ); local_tstates += ( 4 ); continue
			if opcode == 155:    # SBC A,E 
			 sbc_a( Eget() ); local_tstates += ( 4 ); continue
			if opcode == 156:    # SBC A,H 
			 sbc_a( Hget() ); local_tstates += ( 4 ); continue
			if opcode == 157:    # SBC A,L 
			 sbc_a( Lget() ); local_tstates += ( 4 ); continue
			if opcode == 158:    # SBC A,(HL) 
			 sbc_a( peekb( _HL ) ); local_tstates += ( 7 ); continue
			if opcode == 159:    # SBC A,A 
			 sbc_a( _A ); local_tstates += ( 4 ); continue

			# AND * 
			if opcode == 160:    # AND B 
			 and_a( _B ); local_tstates += ( 4 ); continue
			if opcode == 161:    # AND C 
			 and_a(_C ); local_tstates += ( 4 ); continue
			if opcode == 162:    # AND D 
			 and_a( Dget() ); local_tstates += ( 4 ); continue
			if opcode == 163:    # AND E 
			 and_a( Eget() ); local_tstates += ( 4 ); continue
			if opcode == 164:    # AND H 
			 and_a( Hget() ); local_tstates += ( 4 ); continue
			if opcode == 165:    # AND L 
			 and_a( Lget() ); local_tstates += ( 4 ); continue
			if opcode == 166:    # AND (HL) 
			 and_a( peekb( _HL ) ); local_tstates += ( 7 ); continue
			if opcode == 167:    # AND _A 
			 and_a( _A ); local_tstates += ( 4 ); continue

			# XOR * 
			if opcode == 168:    # XOR B 
			 xor_a( _B ); local_tstates += ( 4 ); continue
			if opcode == 169:    # XOR C 
			 xor_a(_C ); local_tstates += ( 4 ); continue
			if opcode == 170:    # XOR D 
			 xor_a( Dget() ); local_tstates += ( 4 ); continue
			if opcode == 171:    # XOR E 
			 xor_a( Eget() ); local_tstates += ( 4 ); continue
			if opcode == 172:    # XOR H 
			 xor_a( Hget() ); local_tstates += ( 4 ); continue
			if opcode == 173:    # XOR L 
			 xor_a( Lget() ); local_tstates += ( 4 ); continue
			if opcode == 174:    # XOR (HL) 
			 xor_a( peekb( _HL ) ); local_tstates += ( 7 ); continue
			if opcode == 175:    # XOR _A 
			 xor_a( _A ); local_tstates += ( 4 ); continue

			# OR * 
			if opcode == 176:    # OR B 
			 or_a( _B ); local_tstates += ( 4 ); continue
			if opcode == 177:    # OR C 
			 or_a(_C ); local_tstates += ( 4 ); continue
			if opcode == 178:    # OR D 
			 or_a( Dget() ); local_tstates += ( 4 ); continue
			if opcode == 179:    # OR E 
			 or_a( Eget() ); local_tstates += ( 4 ); continue
			if opcode == 180:    # OR H 
			 or_a( Hget() ); local_tstates += ( 4 ); continue
			if opcode == 181:    # OR L 
			 or_a( Lget() ); local_tstates += ( 4 ); continue
			if opcode == 182:    # OR (HL) 
			 or_a( peekb( _HL ) ); local_tstates += ( 7 ); continue
			if opcode == 183:    # OR _A 
			 or_a( _A ); local_tstates += ( 4 ); continue

			# CP * 
			if opcode == 184:    # CP B 
			 cp_a( _B ); local_tstates += ( 4 ); continue
			if opcode == 185:    # CP C 
			 cp_a(_C ); local_tstates += ( 4 ); continue
			if opcode == 186:    # CP D 
			 cp_a( Dget() ); local_tstates += ( 4 ); continue
			if opcode == 187:    # CP E 
			 cp_a( Eget() ); local_tstates += ( 4 ); continue
			if opcode == 188:    # CP H 
			 cp_a( Hget() ); local_tstates += ( 4 ); continue
			if opcode == 189:    # CP L 
			 cp_a( Lget() ); local_tstates += ( 4 ); continue
			if opcode == 190:    # CP (HL) 
			 cp_a( peekb( _HL ) ); local_tstates += ( 7 ); continue
			if opcode == 191:    # CP _A 
			 cp_a( _A ); local_tstates += ( 4 ); continue

			# RET cc 
			if opcode == 192:    # RET NZ 
				if(not fZ):
					poppc();
					local_tstates += ( 11 )
				else :
					local_tstates += ( 5 )
				continue
		
			if opcode == 200:    # RET Z 
				if(fZ):
					poppc();
					local_tstates += ( 11 )
				else :
					local_tstates += ( 5 )
				continue
		
			if opcode == 208:    # RET NC 
				if(not fC):
					poppc();
					local_tstates += ( 11 )
				else :
					local_tstates += ( 5 )
				continue
		
			if opcode == 216:    # RET C 
				if(fC):
					poppc();
					local_tstates += ( 11 )
				else :
					local_tstates += ( 5 )
				continue
		
			if opcode == 224:    # RET PO 
				if(not fPV):
					poppc();
					local_tstates += ( 11 )
				else :
					local_tstates += ( 5 )
				continue
		
			if opcode == 232:    # RET PE 
				if(fPV):
					poppc();
					local_tstates += ( 11 )
				else :
					local_tstates += ( 5 )
				continue
		
			if opcode == 240:    # RET P 
				if(not fS):
					poppc();
					local_tstates += ( 11 )
				else :
					local_tstates += ( 5 )
				continue
		
			if opcode == 248:    # RET M 
				if(fS):
					poppc();
					local_tstates += ( 11 )
				else :
					local_tstates += ( 5 )
				continue
		

			# POP,Various 
			if opcode == 193:    # POP BC 
			 BC( popw() ); local_tstates += ( 10 ); continue
			if opcode == 201: # RET 
			 poppc(); local_tstates += ( 10 ); continue
			if opcode == 209:    # POP DE 
			 DE( popw() ); local_tstates += ( 10 ); continue
			if opcode == 217:    # EXX 
				exx();
				local_tstates += ( 4 );
				continue
		
			if opcode == 225:    # POP HL 
			 HL( popw() ); local_tstates += ( 10 ); continue
			if opcode == 233: # JP (HL) 
			 PC( _HL ); local_tstates += ( 4 ); continue
			if opcode == 241:    # POP AF 
			 AF( popw() ); local_tstates += ( 10 ); continue
			if opcode == 249:    # LD SP,HL 
			 SP( _HL ); local_tstates += ( 6 ); continue

			# JP cc,nn 
			if opcode == 194:    # JP NZ,nn 
				if(not fZ):
					PC( nxtpcw() )
				else :
					PC( (_PC +2)&0xffff )
				local_tstates += ( 10 );
				continue
		
			if opcode == 202:    # JP Z,nn 
				if( fZ):
					PC( nxtpcw() )
				else :
					PC( (_PC +2)&0xffff )
				local_tstates += ( 10 );
				continue
		
			if opcode == 210:    # JP NC,nn 
				if(not fC):
					PC( nxtpcw() )
				else :
					PC( (_PC +2)&0xffff )
				local_tstates += ( 10 );
				continue
		
			if opcode == 218:    # JP C,nn 
				if( fC):
					PC( nxtpcw() )
				else :
					PC( (_PC +2)&0xffff )
				local_tstates += ( 10 );
				continue
		
			if opcode == 226:    # JP PO,nn 
				if(not fPV):
					PC( nxtpcw() )
				else :
					PC( (_PC +2)&0xffff )
				local_tstates += ( 10 );
				continue
		
			if opcode == 234:    # JP PE,nn 
				if( fPV):
					PC( nxtpcw() )
				else :
					PC( (_PC +2)&0xffff )
				local_tstates += ( 10 );
				continue
		
			if opcode == 242:    # JP P,nn 
				if(not fS):
					PC( nxtpcw() )
				else :
					PC( (_PC +2)&0xffff )
				local_tstates += ( 10 );
				continue
		
			if opcode == 250:    # JP M,nn 
				if( fS):
					PC( nxtpcw() )
				else :
					PC( (_PC +2)&0xffff )
				local_tstates += ( 10 );
				continue
		


			# Various 
			if opcode == 195:    # JP nn 
			 PC( peekw( _PC  ) ); local_tstates += ( 10 ); continue
			if opcode == 203:    # prefix CB 
			 local_tstates += execute_cb(); continue
			if opcode == 211:    # OUT (n),A 
				outb( nxtpcb(), _A, local_tstates );
				local_tstates += ( 11 );
				continue
		
			if opcode == 219:    # IN A,(n) 
				A( inb((_A << 8) | nxtpcb()) );
				local_tstates += ( 11 );
				continue
		
			if opcode == 227:    # EX (SP),HL 
				t = _HL;
				sp = SPget();
				HL( peekw( sp ) );
				pokew( sp, t );
				local_tstates += ( 19 );
				continue
		
			if opcode == 235:    # EX DE,HL 
				t = _HL;
				HL( DEget() );
				DE( t );
				local_tstates += ( 4 );
				continue
		
			if opcode == 243:    # DI 
				IFF1( False );
				IFF2( False );
				local_tstates += ( 4 );
				continue
		
			if opcode == 251:    # EI 
				IFF1( True );
				IFF2( True );
				local_tstates += ( 4 ); 
				continue
		

			# CALL cc,nn 
			if opcode == 196: # CALL NZ,nn 
				if( not fZ ):
					t = nxtpcw();
					pushpc();
					PC( t );
					local_tstates += ( 17 )
				else :
					PC( (_PC  + 2)&0xffff );
					local_tstates += ( 10 )
				continue
		
			if opcode == 204: # CALL Z,nn 
				if( fZ ):
					t = nxtpcw();
					pushpc();
					PC( t );
					local_tstates += ( 17 )
				else :
					PC( (_PC  + 2)&0xffff );
					local_tstates += ( 10 )
				continue
		
			if opcode == 212: # CALL NC,nn 
				if( not fC ):
					t = nxtpcw();
					pushpc();
					PC( t );
					local_tstates += ( 17 )
				else :
					PC( (_PC  + 2)&0xffff );
					local_tstates += ( 10 )
				continue
		
			if opcode == 220: # CALL C,nn 
				if( fC ):
					t = nxtpcw();
					pushpc();
					PC( t );
					local_tstates += ( 17 )
				else :
					PC( (_PC  + 2)&0xffff );
					local_tstates += ( 10 )
				continue
		
			if opcode == 228: # CALL PO,nn 
				if( not fPV ):
					t = nxtpcw();
					pushpc();
					PC( t );
					local_tstates += ( 17 )
				else :
					PC( (_PC  + 2)&0xffff );
					local_tstates += ( 10 )
				continue
		
			if opcode == 236: # CALL PE,nn 
				if fPV:
					t = nxtpcw();
					pushpc();
					PC( t );
					local_tstates += ( 17 )
				else :
					PC( (_PC  + 2)&0xffff );
					local_tstates += ( 10 )
				continue
		
			if opcode == 244: # CALL P,nn 
				if( not fS ):
					t = nxtpcw();
					pushpc();
					PC( t );
					local_tstates += ( 17 )
				else :
					PC( (_PC  + 2)&0xffff );
					local_tstates += ( 10 )
				continue
		
			if opcode == 252: # CALL M,nn 
				if( fS ):
					t = nxtpcw();
					pushpc();
					PC( t );
					local_tstates += ( 17 )
				else :
					PC( (_PC  + 2)&0xffff );
					local_tstates += ( 10 )
				continue
		

			# PUSH,Various 
			if opcode == 197:    # PUSH BC 
			 pushw( BCget() ); local_tstates += ( 11 ); continue
			if opcode == 205:    # CALL nn 
				t = nxtpcw();
				pushpc();
				PC( t );
				local_tstates += ( 17 );
				continue
		
			if opcode == 213:    # PUSH DE 
			 pushw( DEget() ); local_tstates += ( 11 ); continue
			if opcode == 221:    # prefix IX 
				ID( IXget() );
				local_tstates += execute_id();
				IX( IDget() );
				continue
		
			if opcode == 229:    # PUSH HL 
			 pushw( _HL ); local_tstates += ( 11 ); continue
			if opcode == 237:    # prefix ED 
			 local_tstates += execute_ed( local_tstates ); continue
			if opcode == 245:    # PUSH AF 
			 pushw( AFget() ); local_tstates += ( 11 ); continue
			if opcode == 253:    # prefix IY 
				ID( IYget() );
				local_tstates += execute_id();
				IY( IDget() );
				continue
		

			# op A,N 
			if opcode == 198: # ADD A,N 
			 add_a(nxtpcb()); local_tstates += ( 7 ); continue
			if opcode == 206: # ADC A,N 
			 adc_a(nxtpcb()); local_tstates += ( 7 ); continue
			if opcode == 214: # SUB N 
			 sub_a(nxtpcb()); local_tstates += ( 7 ); continue
			if opcode == 222: # SBC A,N 
			 sbc_a(nxtpcb()); local_tstates += ( 7 ); continue
			if opcode == 230: # AND N 
			 and_a(nxtpcb()); local_tstates += ( 7 ); continue
			if opcode == 238: # XOR N 
			 xor_a(nxtpcb()); local_tstates += ( 7 ); continue
			if opcode == 246: # OR N 
			 or_a(nxtpcb()); local_tstates += ( 7 ); continue
			if opcode == 254: # CP N 
			 cp_a(nxtpcb()); local_tstates += ( 7 ); continue

			# RST n 
			if opcode == 199:    # RST 0 
			 pushpc(); PC( 0 ); local_tstates += ( 11 ); continue
			if opcode == 207:    # RST 8 
			 pushpc(); PC( 8 ); local_tstates += ( 11 ); continue
			if opcode == 215:    # RST 16 
			 pushpc(); PC( 16 ); local_tstates += ( 11 ); continue
			if opcode == 223:    # RST 24  
			 pushpc(); PC( 24 ); local_tstates += ( 11 ); continue
			if opcode == 231:    # RST 32 
			 pushpc(); PC( 32 ); local_tstates += ( 11 ); continue
			if opcode == 239:    # RST 40 
			 pushpc(); PC( 40 ); local_tstates += ( 11 ); continue
			if opcode == 247:    # RST 48 
			 pushpc(); PC( 48 ); local_tstates += ( 11 ); continue
			if opcode == 255:    # RST 56 
			 pushpc(); PC( 56 ); local_tstates += ( 11 ); continue

		local_tstates -= tstatesPerInterrupt - 0;

	 ## end while



def execute_ed( local_tstates ):
		global _R

		_R += 1 

		opcode =  nxtpcb()

		#NOP
		if opcode in (0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 127, 128, 129, 130, 131, 132, 133, 134, 135, 136, 137, 138, 139, 140, 141, 142, 143, 144, 145, 146, 147, 148, 149, 150, 151, 152, 153, 154, 155, 156, 157, 158, 159, 164, 165, 166, 167, 172, 173, 174, 175, 180, 181, 182, 183):
			return ( 8 );

		# IN r,(c) 
		if opcode == 64:  # IN B,(c) 
		 B( in_bc() ); return ( 12 )
		if opcode == 72:  # IN C,(c) 
		 C( in_bc() ); return ( 12 )
		if opcode == 80:  # IN D,(c) 
		 D( in_bc() ); return ( 12 )
		if opcode == 88:  # IN E,(c) 
		 E( in_bc() ); return ( 12 )
		if opcode == 96:  # IN H,(c) 
		 H( in_bc() ); return ( 12 )
		if opcode == 104:  # IN L,(c) 
		 L( in_bc() ); return ( 12 )
		if opcode == 112:  # IN (c) 
		 in_bc(); return ( 12 )
		if opcode == 120:  # IN A,(c) 
		 A( in_bc() ); return ( 12 )

		# OUT (c),r 
		if opcode == 65:  # OUT (c),B 
		 outb( BCget(), _B, local_tstates ); return ( 12 )
		if opcode == 73:  # OUT (c),C 
		 outb( BCget(),_C, local_tstates ); return ( 12 )
		if opcode == 81:  # OUT (c),D 
		 outb( BCget(), Dget(), local_tstates ); return ( 12 )
		if opcode == 89:  # OUT (c),E 
		 outb( BCget(), Eget(), local_tstates ); return ( 12 )
		if opcode == 97:  # OUT (c),H 
		 outb( BCget(), Hget(), local_tstates ); return ( 12 )
		if opcode == 105:  # OUT (c),L 
		 outb( BCget(), Lget(), local_tstates ); return ( 12 )
		if opcode == 113:  # OUT (c),0 
		 outb( BCget(), 0, local_tstates ); return ( 12 )
		if opcode == 121:  # OUT (c),A 
		 outb( BCget(), _A, local_tstates ); return ( 12 )

		# SBC/ADC HL,ss 
		if opcode == 66:  # SBC HL,BC 
		 HL( sbc16( _HL, BCget() ) ); return ( 15 )
		if opcode == 74:  # ADC HL,BC 
		 HL( adc16( _HL, BCget() ) ); return ( 15 )
		if opcode == 82:  # SBC HL,DE 
		 HL( sbc16( _HL, DEget() ) ); return ( 15 )
		if opcode == 90:  # ADC HL,DE 
		 HL( adc16( _HL, DEget() ) ); return ( 15 )
		if opcode == 98:  # SBC HL,HL 
			hl = _HL;
			HL( sbc16( hl, hl ) );
			return ( 15 );
	
		if opcode == 106:  # ADC HL,HL 
			hl = _HL;
			HL( adc16( hl, hl ) );
			return ( 15 );
	
		if opcode == 114:  # SBC HL,SP 
		 HL( sbc16( _HL, SPget() ) ); return ( 15 )
		if opcode == 122:  # ADC HL,SP 
		 HL( adc16( _HL, SPget() ) ); return ( 15 )

		# LD (nn),ss, LD ss,(nn) 
		if opcode == 67:  # LD (nn),BC 
		 pokew( nxtpcw(), BCget() ); return ( 20 )
		if opcode == 75:  # LD BCget(),(nn) 
		 BC( peekw( nxtpcw() ) ); return ( 20 )
		if opcode == 83:  # LD (nn),DE 
		 pokew( nxtpcw(), DEget() ); return ( 20 )
		if opcode == 91:  # LD DE,(nn) 
		 DE( peekw( nxtpcw() ) ); return ( 20 )
		if opcode == 99:  # LD (nn),HL 
		 pokew( nxtpcw(), _HL ); return ( 20 )
		if opcode == 107:  # LD HL,(nn) 
		 HL( peekw( nxtpcw() ) ); return ( 20 )
		if opcode == 115:  # LD (nn),SP 
		 pokew( nxtpcw(), SPget() ); return ( 20 )
		if opcode == 123:  # LD SP,(nn) 
		 SP( peekw( nxtpcw() ) ); return ( 20 )

		# NEG 
		if opcode in (68 ,76, 84, 92, 100, 108, 116, 124):  # NEG 
		 neg_a(); return ( 8 )

		# RETn 
		if opcode in (69, 85, 101, 117):  # RETN 
			IFF1( IFF2get() );
			poppc();
			return ( 14 );
	
		if opcode in (77, 93, 109, 125):  # RETI 
			poppc();
			return ( 14 );
	

		# IM x 
		if opcode in (70, 78, 102, 110):  # IM 0 
		 IM( IM0 ); return ( 8 )
		if opcode in (86, 118):  # IM 1 
		 IM( IM1 ); return ( 8 )
		if opcode in (94, 126):  # IM 2 
		 IM( IM2 ); return ( 8 )

		# LD A,s / LD s,A / RxD 
		if opcode == 71:  # LD I,A 
		 I( _A ); return ( 9 )
		if opcode == 79:  # LD R,A 
		 R( _A ); return ( 9 )
		if opcode == 87:  # LD A,I 
		 ld_a_i(); return ( 9 )
		if opcode == 95:  # LD A,R 
		 ld_a_r(); return ( 9 )
		if opcode == 103:  # RRD 
		 rrd_a(); return ( 18 )
		if opcode == 111:  # RLD 
		 rld_a(); return ( 18 )

		# xxI 
		if opcode == 160:  # LDI 
			mem[ DEget()] = peekb( _HL )
			DE( inc16( DEget() ) );
			HL( inc16( _HL ) );
			BC( dec16( BCget() ) );

			setPV( BCget() != 0 );
			setH( False );
			setN( False );

			return ( 16 );
	
		if opcode == 161:  # CPI 
			c = fC;

			cp_a( peekb( _HL ) );
			HL( inc16( _HL ) );
			BC( dec16( BCget() ) );

			setPV( BCget() != 0 );
			setC( c );

			return ( 16 );
	
		if opcode == 162:  # INI 
			mem[ _HL] = inb( BCget() )
			B( b = qdec8( _B ) );
			HL( inc16( _HL ) );

			setZ( b == 0 );
			setN( True );

			return ( 16 );
	
		if opcode == 163:  # OUTI 
			B( b = qdec8( _B ) );
			outb( BCget(), peekb( _HL ), local_tstates );
			HL( inc16( _HL ) );

			setZ( b == 0 );
			setN( True );

			return ( 16 );
	

		# xxD 
		if opcode == 168:  # LDD 
			mem[ DEget()] = peekb( _HL )
			DE( dec16( DEget() ) );
			HL( dec16( _HL ) );
			BC( dec16( BCget() ) );

			setPV( BCget() != 0 );
			setH( False );
			setN( False );

			return ( 16 );
	
		if opcode == 169:  # CPD 
			c = fC;

			cp_a( peekb( _HL ) );
			HL( dec16( _HL ) );
			BC( dec16( BCget() ) );

			setPV( BCget() != 0 );
			setC( c );

			return ( 16 );
	
		if opcode == 170:  # IND 
			mem[ _HL] = inb( BCget() )
			B( b = qdec8( _B ) );
			HL( dec16( _HL ) );

			setZ( b == 0 );
			setN( True );

			return ( 16 );
	
		if opcode == 171:  # OUTD 
			B( b = qdec8( _B ) );
			outb( BCget(), peekb( _HL ), local_tstates );
			HL( dec16( _HL ) );

			setZ( b == 0 );
			setN( True );

			return ( 16 );
	

		# xxIR 
		if opcode == 176:  # LDIR 
			_local_tstates = 0;

			count = BCget();
			dest = DEget();
			src = _HL;
			_R += -2 

			while count != 0:
				mem[dest] = mem[src]
				src  = ( src  + 1) & 0xffff
				dest  = ( dest  + 1) & 0xffff
				count = ( count  - 1) & 0xffff
			_local_tstates += 21*count
			_R += 2*count
#---------------------------------------------------------
			if (count != 0):
				PC( (_PC -2)&0xffff );
				setH( False );
				setN( False );
				setPV( True )
			else :
				_local_tstates += ( -5 );
				setH( False );
				setN( False );
				setPV( False )
			DE( dest );
			HL( src );
			BC( count );

			return ( _local_tstates );
	
		if opcode == 177:  # CPIR 
			c = fC

			cp_a( peekb( _HL ) )
			HL( inc16( _HL ) )
			BC( dec16( BCget() ) )

			pv = bool(BCget() != 0)

			setPV( pv );
			setC( c );
			if ( pv and (not fZ) ):
				PC( (_PC -2)&0xffff );
				return ( 21 )
			return ( 16 );
	
		if opcode == 178:  # INIR 
			mem[ _HL] = inb( BCget() )
			B( b = qdec8( _B ) );
			HL( inc16( _HL ) );

			setZ( True );
			setN( True );
			if (b != 0):
				PC( (_PC -2)&0xffff );
				return ( 21 )
			return ( 16 );
	
		if opcode == 179:  # OTIR 
			B( b = qdec8( _B ) );
			outb( BCget(), peekb( _HL ), local_tstates );
			HL( inc16( _HL ) );

			setZ( True );
			setN( True );
			if (b != 0):
				PC( (_PC -2)&0xffff );
				return ( 21 )
			return ( 16 );
	

		# xxDR 
		if opcode == 184:  # LDDR 
		
			_local_tstates = 0;

			count = BCget();
			dest = DEget();
			src = _HL;
			_R += -2

			while count:
				mem[dest] = mem[src]
				src  = ( src  - 1) & 0xffff
				dest  = ( dest  - 1) & 0xffff
				count -= 1
			_local_tstates += 21*count
			_R += 2*count

			if (count != 0):
				PC( (_PC -2)&0xffff );
				setH( False );
				setN( False );
				setPV( True )
			else :
				_local_tstates += ( -5 );
				setH( False );
				setN( False );
				setPV( False )
			DE( dest );
			HL( src );
			BC( count );

			return _local_tstates
	
		if opcode == 185:  # CPDR 
		
			c = fC;

			cp_a( peekb( _HL ) );
			HL( dec16( _HL ) );
			BC( dec16( BCget() ) );

			pv = bool(BCget() != 0);

			setPV( pv );
			setC( c );
			if ( pv and (not fZ) ):
				PC( (_PC -2)&0xffff );
				return ( 21 )
			return ( 16 );
	
		if opcode == 186:  # INDR 
			mem [ _HL] = inb( BCget() )
			B( b = qdec8( _B ) );
			HL( dec16( _HL ) );

			setZ( True );
			setN( True );
			if (b != 0):
				PC( (_PC -2)&0xffff );
				return ( 21 )
			return ( 16 );
	
		if opcode == 187:  # OTDR 
			B( b = qdec8( _B ) );
			outb( BCget(), peekb( _HL ), local_tstates );
			HL( dec16( _HL ) );

			setZ( True );
			setN( True );
			if (b != 0):
				PC( (_PC -2)&0xffff );
				return ( 21 )
			return ( 16 );
	

	 # end opcode = 

		# NOP
		return ( 8 );


def execute_cb():
		global _R

		_R += 1 

		opcode =  ( nxtpcb() )

		if opcode ==   0:	# RLC B 
		 B( rlc( _B ) ); return ( 8 )
		if opcode ==   1:	# RLC C 
		 C( rlc(_C ) ); return ( 8 )
		if opcode ==   2:	# RLC D 
		 D( rlc( Dget() ) ); return ( 8 )
		if opcode ==   3:	# RLC E 
		 E( rlc( Eget() ) ); return ( 8 )
		if opcode ==   4:	# RLC H 
		 H( rlc( Hget() ) ); return ( 8 )
		if opcode ==   5:	# RLC L 
		 L( rlc( Lget() ) ); return ( 8 )
		if opcode ==   6:	# RLC (HL) 
		
			hl = _HL;
			mem[ hl] = rlc( peekb( hl ) ) 
			return ( 15 );
	
		if opcode ==   7:	# RLC A 
		 A( rlc( _A ) ); return ( 8 )

		if opcode ==   8:	# RRC B 
		 B( rrc( _B ) ); return ( 8 )
		if opcode ==   9:	# RRC C 
		 C( rrc(_C ) ); return ( 8 )
		if opcode ==  10:	# RRC D 
		 D( rrc( Dget() ) ); return ( 8 )
		if opcode ==  11:	# RRC E 
		 E( rrc( Eget() ) ); return ( 8 )
		if opcode ==  12:	# RRC H 
		 H( rrc( Hget() ) ); return ( 8 )
		if opcode ==  13:	# RRC L 
		 L( rrc( Lget() ) ); return ( 8 )
		if opcode ==  14:	# RRC (HL) 
			hl = _HL;
			mem[ hl] = rrc( peekb( hl ) )
			return ( 15 );
	
		if opcode ==  15:	# RRC A 
		 A( rrc( _A ) ); return ( 8 )

		if opcode ==  16:	# RL B 
		 B( rl( _B ) ); return ( 8 )
		if opcode ==  17:	# RL C 
		 C( rl(_C ) ); return ( 8 )
		if opcode ==  18:	# RL D 
		 D( rl( Dget() ) ); return ( 8 )
		if opcode ==  19:	# RL E 
		 E( rl( Eget() ) ); return ( 8 )
		if opcode ==  20:	# RL H 
		 H( rl( Hget() ) ); return ( 8 )
		if opcode ==  21:	# RL L 
		 L( rl( Lget() ) ); return ( 8 )
		if opcode ==  22:	# RL (HL) 
			hl = _HL;
			mem[hl] = rl( peekb( hl ) )
			return ( 15 );

		if opcode ==  23:	# RL A 
		 A( rl( _A ) ); return ( 8 )

		if opcode ==  24:	# RR B 
		 B( rr( _B ) ); return ( 8 )
		if opcode ==  25:	# RR C 
		 C( rr(_C ) ); return ( 8 )
		if opcode ==  26:	# RR D 
		 D( rr( Dget() ) ); return ( 8 )
		if opcode ==  27:	# RR E 
		 E( rr( Eget() ) ); return ( 8 )
		if opcode ==  28:	# RR H 
		 H( rr( Hget() ) ); return ( 8 )
		if opcode ==  29:	# RR L 
		 L( rr( Lget() ) ); return ( 8 )
		if opcode ==  30:	# RR (HL) 
		
			hl = _HL;
			mem[hl] = rr( peekb( hl ) )
			return ( 15 );
	
		if opcode ==  31:	# RR A 
		 A( rr( _A ) ); return ( 8 )

		if opcode ==  32:	# SLA B 
		 B( sla( _B ) ); return ( 8 )
		if opcode ==  33:	# SLA C 
		 C( sla(_C ) ); return ( 8 )
		if opcode ==  34:	# SLA D 
		 D( sla( Dget() ) ); return ( 8 )
		if opcode ==  35:	# SLA E 
		 E( sla( Eget() ) ); return ( 8 )
		if opcode ==  36:	# SLA H 
		 H( sla( Hget() ) ); return ( 8 )
		if opcode ==  37:	# SLA L 
		 L( sla( Lget() ) ); return ( 8 )
		if opcode ==  38:	# SLA (HL) 
		
			hl = _HL;
			mem[hl] = sla( peekb( hl ) )
			return ( 15 );
	
		if opcode ==  39:	# SLA A 
		 A( sla( _A ) ); return ( 8 )

		if opcode ==  40:	# SRA B 
		 B( sra( _B ) ); return ( 8 )
		if opcode ==  41:	# SRA C 
		 C( sra(_C ) ); return ( 8 )
		if opcode ==  42:	# SRA D 
		 D( sra( Dget() ) ); return ( 8 )
		if opcode ==  43:	# SRA E 
		 E( sra( Eget() ) ); return ( 8 )
		if opcode ==  44:	# SRA H 
		 H( sra( Hget() ) ); return ( 8 )
		if opcode ==  45:	# SRA L 
		 L( sra( Lget() ) ); return ( 8 )
		if opcode ==  46:	# SRA (HL) 
		
			hl = _HL;
			mem[ hl] = sra( peekb( hl ) )
			return ( 15 );
	
		if opcode ==  47:	# SRA A 
		 A( sra( _A ) ); return ( 8 )

		if opcode ==  48:	# SLS B 
		 B( sls( _B ) ); return ( 8 )
		if opcode ==  49:	# SLS C 
		 C( sls(_C ) ); return ( 8 )
		if opcode ==  50:	# SLS D 
		 D( sls( Dget() ) ); return ( 8 )
		if opcode ==  51:	# SLS E 
		 E( sls( Eget() ) ); return ( 8 )
		if opcode ==  52:	# SLS H 
		 H( sls( Hget() ) ); return ( 8 )
		if opcode ==  53:	# SLS L 
		 L( sls( Lget() ) ); return ( 8 )
		if opcode ==  54:	# SLS (HL) 
		
			hl = _HL;
			mem[ hl] = sls( peekb( hl ) )
			return ( 15 );
	
		if opcode ==  55:	# SLS A 
		 A( sls( _A ) ); return ( 8 )

		if opcode ==  56:	# SRL B 
		 B( srl( _B ) ); return ( 8 )
		if opcode ==  57:	# SRL C 
		 C( srl(_C ) ); return ( 8 )
		if opcode ==  58:	# SRL D 
		 D( srl( Dget() ) ); return ( 8 )
		if opcode ==  59:	# SRL E 
		 E( srl( Eget() ) ); return ( 8 )
		if opcode ==  60:	# SRL H 
		 H( srl( Hget() ) ); return ( 8 )
		if opcode ==  61:	# SRL L 
		 L( srl( Lget() ) ); return ( 8 )
		if opcode ==  62:	# SRL (HL) 
		
			hl = _HL;
			mem[hl] = srl( peekb( hl ) )
			return ( 15 );
	
		if opcode ==  63:	# SRL A 
		 A( srl( _A ) ); return ( 8 )

		if opcode ==  64:	# BIT 0,B 
		 bit( 0x01, _B ); return ( 8 )
		if opcode ==  65:	# BIT 0,C 
		 bit( 0x01,_C ); return ( 8 )
		if opcode ==  66:	# BIT 0,D 
		 bit( 0x01, Dget() ); return ( 8 )
		if opcode ==  67:	# BIT 0,E 
		 bit( 0x01, Eget() ); return ( 8 )
		if opcode ==  68:	# BIT 0,H 
		 bit( 0x01, Hget() ); return ( 8 )
		if opcode ==  69:	# BIT 0,L 
		 bit( 0x01, Lget() ); return ( 8 )
		if opcode ==  70:	# BIT 0,(HL) 
		 bit( 0x01, peekb( _HL ) ); return ( 12 )
		if opcode ==  71:	# BIT 0,A 
		 bit( 0x01, _A ); return ( 8 )

		if opcode ==  72:	# BIT 1,B 
		 bit( 0x02, _B ); return ( 8 )
		if opcode ==  73:	# BIT 1,C 
		 bit( 0x02,_C ); return ( 8 )
		if opcode ==  74:	# BIT 1,D 
		 bit( 0x02, Dget() ); return ( 8 )
		if opcode ==  75:	# BIT 1,E 
		 bit( 0x02, Eget() ); return ( 8 )
		if opcode ==  76:	# BIT 1,H 
		 bit( 0x02, Hget() ); return ( 8 )
		if opcode ==  77:	# BIT 1,L 
		 bit( 0x02, Lget() ); return ( 8 )
		if opcode ==  78:	# BIT 1,(HL) 
		 bit( 0x02, peekb( _HL ) ); return ( 12 )
		if opcode ==  79:	# BIT 1,A 
		 bit( 0x02, _A ); return ( 8 )

		if opcode ==  80:	# BIT 2,B 
		 bit( 0x04, _B ); return ( 8 )
		if opcode ==  81:	# BIT 2,C 
		 bit( 0x04,_C ); return ( 8 )
		if opcode ==  82:	# BIT 2,D 
		 bit( 0x04, Dget() ); return ( 8 )
		if opcode ==  83:	# BIT 2,E 
		 bit( 0x04, Eget() ); return ( 8 )
		if opcode ==  84:	# BIT 2,H 
		 bit( 0x04, Hget() ); return ( 8 )
		if opcode ==  85:	# BIT 2,L 
		 bit( 0x04, Lget() ); return ( 8 )
		if opcode ==  86:	# BIT 2,(HL) 
		 bit( 0x04, peekb( _HL ) ); return ( 12 )
		if opcode ==  87:	# BIT 2,A 
		 bit( 0x04, _A ); return ( 8 )

		if opcode ==  88:	# BIT 3,B 
		 bit( 0x08, _B ); return ( 8 )
		if opcode ==  89:	# BIT 3,C 
		 bit( 0x08,_C ); return ( 8 )
		if opcode ==  90:	# BIT 3,D 
		 bit( 0x08, Dget() ); return ( 8 )
		if opcode ==  91:	# BIT 3,E 
		 bit( 0x08, Eget() ); return ( 8 )
		if opcode ==  92:	# BIT 3,H 
		 bit( 0x08, Hget() ); return ( 8 )
		if opcode ==  93:	# BIT 3,L 
		 bit( 0x08, Lget() ); return ( 8 )
		if opcode ==  94:	# BIT 3,(HL) 
		 bit( 0x08, peekb( _HL ) ); return ( 12 )
		if opcode ==  95:	# BIT 3,A 
		 bit( 0x08, _A ); return ( 8 )

		if opcode ==  96:	# BIT 4,B 
		 bit( 0x10, _B ); return ( 8 )
		if opcode ==  97:	# BIT 4,C 
		 bit( 0x10,_C ); return ( 8 )
		if opcode ==  98:	# BIT 4,D 
		 bit( 0x10, Dget() ); return ( 8 )
		if opcode ==  99:	# BIT 4,E 
		 bit( 0x10, Eget() ); return ( 8 )
		if opcode == 100:	# BIT 4,H 
		 bit( 0x10, Hget() ); return ( 8 )
		if opcode == 101:	# BIT 4,L 
		 bit( 0x10, Lget() ); return ( 8 )
		if opcode == 102:	# BIT 4,(HL) 
		 bit( 0x10, peekb( _HL ) ); return ( 12 )
		if opcode == 103:	# BIT 4,A 
		 bit( 0x10, _A ); return ( 8 )

		if opcode == 104:	# BIT 5,B 
		 bit( 0x20, _B ); return ( 8 )
		if opcode == 105:	# BIT 5,C 
		 bit( 0x20,_C ); return ( 8 )
		if opcode == 106:	# BIT 5,D 
		 bit( 0x20, Dget() ); return ( 8 )
		if opcode == 107:	# BIT 5,E 
		 bit( 0x20, Eget() ); return ( 8 )
		if opcode == 108:	# BIT 5,H 
		 bit( 0x20, Hget() ); return ( 8 )
		if opcode == 109:	# BIT 5,L 
		 bit( 0x20, Lget() ); return ( 8 )
		if opcode == 110:	# BIT 5,(HL) 
		 bit( 0x20, peekb( _HL ) ); return ( 12 )
		if opcode == 111:	# BIT 5,A 
		 bit( 0x20, _A ); return ( 8 )

		if opcode == 112:	# BIT 6,B 
		 bit( 0x40, _B ); return ( 8 )
		if opcode == 113:	# BIT 6,C 
		 bit( 0x40,_C ); return ( 8 )
		if opcode == 114:	# BIT 6,D 
		 bit( 0x40, Dget() ); return ( 8 )
		if opcode == 115:	# BIT 6,E 
		 bit( 0x40, Eget() ); return ( 8 )
		if opcode == 116:	# BIT 6,H 
		 bit( 0x40, Hget() ); return ( 8 )
		if opcode == 117:	# BIT 6,L 
		 bit( 0x40, Lget() ); return ( 8 )
		if opcode == 118:	# BIT 6,(HL) 
		 bit( 0x40, peekb( _HL ) ); return ( 12 )
		if opcode == 119:	# BIT 6,A 
		 bit( 0x40, _A ); return ( 8 )

		if opcode == 120:	# BIT 7,B 
		 bit( 0x80, _B ); return ( 8 )
		if opcode == 121:	# BIT 7,C 
		 bit( 0x80,_C ); return ( 8 )
		if opcode == 122:	# BIT 7,D 
		 bit( 0x80, Dget() ); return ( 8 )
		if opcode == 123:	# BIT 7,E 
		 bit( 0x80, Eget() ); return ( 8 )
		if opcode == 124:	# BIT 7,H 
		 bit( 0x80, Hget() ); return ( 8 )
		if opcode == 125:	# BIT 7,L 
		 bit( 0x80, Lget() ); return ( 8 )
		if opcode == 126:	# BIT 7,(HL) 
		 bit( 0x80, peekb( _HL ) ); return ( 12 )
		if opcode == 127:	# BIT 7,A 
		 bit( 0x80, _A ); return ( 8 )

		if opcode == 128:	# RES 0,B 
		 B( res( 0x01, _B ) ); return ( 8 )
		if opcode == 129:	# RES 0,C 
		 C( res( 0x01,_C ) ); return ( 8 )
		if opcode == 130:	# RES 0,D 
		 D( res( 0x01, Dget() ) ); return ( 8 )
		if opcode == 131:	# RES 0,E 
		 E( res( 0x01, Eget() ) ); return ( 8 )
		if opcode == 132:	# RES 0,H 
		 H( res( 0x01, Hget() ) ); return ( 8 )
		if opcode == 133:	# RES 0,L 
		 L( res( 0x01, Lget() ) ); return ( 8 )
		if opcode == 134:	# RES 0,(HL) 
		
			hl = _HL;
			mem[hl] = res( 0x01, peekb( hl ) )
			return ( 15 );
	
		if opcode == 135:	# RES 0,A 
		 A( res( 0x01, _A ) ); return ( 8 )

		if opcode == 136:	# RES 1,B 
		 B( res( 0x02, _B ) ); return ( 8 )
		if opcode == 137:	# RES 1,C 
		 C( res( 0x02,_C ) ); return ( 8 )
		if opcode == 138:	# RES 1,D 
		 D( res( 0x02, Dget() ) ); return ( 8 )
		if opcode == 139:	# RES 1,E 
		 E( res( 0x02, Eget() ) ); return ( 8 )
		if opcode == 140:	# RES 1,H 
		 H( res( 0x02, Hget() ) ); return ( 8 )
		if opcode == 141:	# RES 1,L 
		 L( res( 0x02, Lget() ) ); return ( 8 )
		if opcode == 142:	# RES 1,(HL) 
		
			hl = _HL;
			mem[ hl] = res( 0x02, peekb( hl ) )
			return ( 15 );
	
		if opcode == 143:	# RES 1,A 
		 A( res( 0x02, _A ) ); return ( 8 )

		if opcode == 144:	# RES 2,B 
		 B( res( 0x04, _B ) ); return ( 8 )
		if opcode == 145:	# RES 2,C 
		 C( res( 0x04,_C ) ); return ( 8 )
		if opcode == 146:	# RES 2,D 
		 D( res( 0x04, Dget() ) ); return ( 8 )
		if opcode == 147:	# RES 2,E 
		 E( res( 0x04, Eget() ) ); return ( 8 )
		if opcode == 148:	# RES 2,H 
		 H( res( 0x04, Hget() ) ); return ( 8 )
		if opcode == 149:	# RES 2,L 
		 L( res( 0x04, Lget() ) ); return ( 8 )
		if opcode == 150:	# RES 2,(HL) 
		
			hl = _HL;
			mem[ hl] = res( 0x04, peekb( hl ) )
			return ( 15 );
	
		if opcode == 151:	# RES 2,A 
		 A( res( 0x04, _A ) ); return ( 8 )

		if opcode == 152:	# RES 3,B 
		 B( res( 0x08, _B ) ); return ( 8 )
		if opcode == 153:	# RES 3,C 
		 C( res( 0x08,_C ) ); return ( 8 )
		if opcode == 154:	# RES 3,D 
		 D( res( 0x08, Dget() ) ); return ( 8 )
		if opcode == 155:	# RES 3,E 
		 E( res( 0x08, Eget() ) ); return ( 8 )
		if opcode == 156:	# RES 3,H 
		 H( res( 0x08, Hget() ) ); return ( 8 )
		if opcode == 157:	# RES 3,L 
		 L( res( 0x08, Lget() ) ); return ( 8 )
		if opcode == 158:	# RES 3,(HL) 
		
			hl = _HL;
			mem[ hl] = res( 0x08, peekb( hl ) )
			return ( 15 );
	
		if opcode == 159:	# RES 3,A 
		 A( res( 0x08, _A ) ); return ( 8 )

		if opcode == 160:	# RES 4,B 
		 B( res( 0x10, _B ) ); return ( 8 )
		if opcode == 161:	# RES 4,C 
		 C( res( 0x10,_C ) ); return ( 8 )
		if opcode == 162:	# RES 4,D 
		 D( res( 0x10, Dget() ) ); return ( 8 )
		if opcode == 163:	# RES 4,E 
		 E( res( 0x10, Eget() ) ); return ( 8 )
		if opcode == 164:	# RES 4,H 
		 H( res( 0x10, Hget() ) ); return ( 8 )
		if opcode == 165:	# RES 4,L 
		 L( res( 0x10, Lget() ) ); return ( 8 )
		if opcode == 166:	# RES 4,(HL) 
		
			hl = _HL;
			mem[hl] = res( 0x10, peekb( hl ) )
			return ( 15 );
	
		if opcode == 167:	# RES 4,A 
		 A( res( 0x10, _A ) ); return ( 8 )

		if opcode == 168:	# RES 5,B 
		 B( res( 0x20, _B ) ); return ( 8 )
		if opcode == 169:	# RES 5,C 
		 C( res( 0x20,_C ) ); return ( 8 )
		if opcode == 170:	# RES 5,D 
		 D( res( 0x20, Dget() ) ); return ( 8 )
		if opcode == 171:	# RES 5,E 
		 E( res( 0x20, Eget() ) ); return ( 8 )
		if opcode == 172:	# RES 5,H 
		 H( res( 0x20, Hget() ) ); return ( 8 )
		if opcode == 173:	# RES 5,L 
		 L( res( 0x20, Lget() ) ); return ( 8 )
		if opcode == 174:	# RES 5,(HL) 
			hl = _HL;
			mem[ hl] = res( 0x20, peekb( hl ) )
			return ( 15 );
	
		if opcode == 175:	# RES 5,A 
		 A( res( 0x20, _A ) ); return ( 8 )

		if opcode == 176:	# RES 6,B 
		 B( res( 0x40, _B ) ); return ( 8 )
		if opcode == 177:	# RES 6,C 
		 C( res( 0x40,_C ) ); return ( 8 )
		if opcode == 178:	# RES 6,D 
		 D( res( 0x40, Dget() ) ); return ( 8 )
		if opcode == 179:	# RES 6,E 
		 E( res( 0x40, Eget() ) ); return ( 8 )
		if opcode == 180:	# RES 6,H 
		 H( res( 0x40, Hget() ) ); return ( 8 )
		if opcode == 181:	# RES 6,L 
		 L( res( 0x40, Lget() ) ); return ( 8 )
		if opcode == 182:	# RES 6,(HL) 
		
			hl = _HL;
			mem[ hl] = res( 0x40, peekb( hl ) )
			return ( 15 );
	
		if opcode == 183:	# RES 6,A 
		 A( res( 0x40, _A ) ); return ( 8 )

		if opcode == 184:	# RES 7,B 
		 B( res( 0x80, _B ) ); return ( 8 )
		if opcode == 185:	# RES 7,C 
		 C( res( 0x80,_C ) ); return ( 8 )
		if opcode == 186:	# RES 7,D 
		 D( res( 0x80, Dget() ) ); return ( 8 )
		if opcode == 187:	# RES 7,E 
		 E( res( 0x80, Eget() ) ); return ( 8 )
		if opcode == 188:	# RES 7,H 
		 H( res( 0x80, Hget() ) ); return ( 8 )
		if opcode == 189:	# RES 7,L 
		 L( res( 0x80, Lget() ) ); return ( 8 )
		if opcode == 190:	# RES 7,(HL) 
		
			hl = _HL;
			mem[hl] = res( 0x80, peekb( hl ) )
			return ( 15 );
	
		if opcode == 191:	# RES 7,A 
		 A( res( 0x80, _A ) ); return ( 8 )

		if opcode == 192:	# SET 0,B 
		 B( set( 0x01, _B ) ); return ( 8 )
		if opcode == 193:	# SET 0,C 
		 C( set( 0x01,_C ) ); return ( 8 )
		if opcode == 194:	# SET 0,D 
		 D( set( 0x01, Dget() ) ); return ( 8 )
		if opcode == 195:	# SET 0,E 
		 E( set( 0x01, Eget() ) ); return ( 8 )
		if opcode == 196:	# SET 0,H 
		 H( set( 0x01, Hget() ) ); return ( 8 )
		if opcode == 197:	# SET 0,L 
		 L( set( 0x01, Lget() ) ); return ( 8 )
		if opcode == 198:	# SET 0,(HL) 
			hl = _HL;
			mem[ hl] = set( 0x01, peekb( hl ) )
			return ( 15 );
	
		if opcode == 199:	# SET 0,A 
		 A( set( 0x01, _A ) ); return ( 8 )

		if opcode == 200:	# SET 1,B 
		 B( set( 0x02, _B ) ); return ( 8 )
		if opcode == 201:	# SET 1,C 
		 C( set( 0x02,_C ) ); return ( 8 )
		if opcode == 202:	# SET 1,D 
		 D( set( 0x02, Dget() ) ); return ( 8 )
		if opcode == 203:	# SET 1,E 
		 E( set( 0x02, Eget() ) ); return ( 8 )
		if opcode == 204:	# SET 1,H 
		 H( set( 0x02, Hget() ) ); return ( 8 )
		if opcode == 205:	# SET 1,L 
		 L( set( 0x02, Lget() ) ); return ( 8 )
		if opcode == 206:	# SET 1,(HL) 
			hl = _HL;
			mem[hl] = set( 0x02, peekb( hl ) )
			return ( 15 );
	
		if opcode == 207:	# SET 1,A 
		 A( set( 0x02, _A ) ); return ( 8 )

		if opcode == 208:	# SET 2,B 
		 B( set( 0x04, _B ) ); return ( 8 )
		if opcode == 209:	# SET 2,C 
		 C( set( 0x04,_C ) ); return ( 8 )
		if opcode == 210:	# SET 2,D 
		 D( set( 0x04, Dget() ) ); return ( 8 )
		if opcode == 211:	# SET 2,E 
		 E( set( 0x04, Eget() ) ); return ( 8 )
		if opcode == 212:	# SET 2,H 
		 H( set( 0x04, Hget() ) ); return ( 8 )
		if opcode == 213:	# SET 2,L 
		 L( set( 0x04, Lget() ) ); return ( 8 )
		if opcode == 214:	# SET 2,(HL) 
			hl = _HL;
			mem[hl] = set( 0x04, peekb( hl ) )
			return ( 15 );
	
		if opcode == 215:	# SET 2,A 
		 A( set( 0x04, _A ) ); return ( 8 )

		if opcode == 216:	# SET 3,B 
		 B( set( 0x08, _B ) ); return ( 8 )
		if opcode == 217:	# SET 3,C 
		 C( set( 0x08,_C ) ); return ( 8 )
		if opcode == 218:	# SET 3,D 
		 D( set( 0x08, Dget() ) ); return ( 8 )
		if opcode == 219:	# SET 3,E 
		 E( set( 0x08, Eget() ) ); return ( 8 )
		if opcode == 220:	# SET 3,H 
		 H( set( 0x08, Hget() ) ); return ( 8 )
		if opcode == 221:	# SET 3,L 
		 L( set( 0x08, Lget() ) ); return ( 8 )
		if opcode == 222:	# SET 3,(HL) 
			hl = _HL;
			mem[hl] = set( 0x08, peekb( hl ) )
			return ( 15 );
	
		if opcode == 223:	# SET 3,A 
		 A( set( 0x08, _A ) ); return ( 8 )

		if opcode == 224:	# SET 4,B 
		 B( set( 0x10, _B ) ); return ( 8 )
		if opcode == 225:	# SET 4,C 
		 C( set( 0x10,_C ) ); return ( 8 )
		if opcode == 226:	# SET 4,D 
		 D( set( 0x10, Dget() ) ); return ( 8 )
		if opcode == 227:	# SET 4,E 
		 E( set( 0x10, Eget() ) ); return ( 8 )
		if opcode == 228:	# SET 4,H 
		 H( set( 0x10, Hget() ) ); return ( 8 )
		if opcode == 229:	# SET 4,L 
		 L( set( 0x10, Lget() ) ); return ( 8 )
		if opcode == 230:	# SET 4,(HL) 
			hl = _HL;
			mem[ hl] = set( 0x10, peekb( hl ) )
			return ( 15 );
	
		if opcode == 231:	# SET 4,A 
		 A( set( 0x10, _A ) ); return ( 8 )

		if opcode == 232:	# SET 5,B 
		 B( set( 0x20, _B ) ); return ( 8 )
		if opcode == 233:	# SET 5,C 
		 C( set( 0x20,_C ) ); return ( 8 )
		if opcode == 234:	# SET 5,D 
		 D( set( 0x20, Dget() ) ); return ( 8 )
		if opcode == 235:	# SET 5,E 
		 E( set( 0x20, Eget() ) ); return ( 8 )
		if opcode == 236:	# SET 5,H 
		 H( set( 0x20, Hget() ) ); return ( 8 )
		if opcode == 237:	# SET 5,L 
		 L( set( 0x20, Lget() ) ); return ( 8 )
		if opcode == 238:	# SET 5,(HL) 
			hl = _HL;
			mem[hl] = set( 0x20, peekb( hl ) )
			return ( 15 );
	
		if opcode == 239:	# SET 5,A 
		 A( set( 0x20, _A ) ); return ( 8 )

		if opcode == 240:	# SET 6,B 
		 B( set( 0x40, _B ) ); return ( 8 )
		if opcode == 241:	# SET 6,C 
		 C( set( 0x40,_C ) ); return ( 8 )
		if opcode == 242:	# SET 6,D 
		 D( set( 0x40, Dget() ) ); return ( 8 )
		if opcode == 243:	# SET 6,E 
		 E( set( 0x40, Eget() ) ); return ( 8 )
		if opcode == 244:	# SET 6,H 
		 H( set( 0x40, Hget() ) ); return ( 8 )
		if opcode == 245:	# SET 6,L 
		 L( set( 0x40, Lget() ) ); return ( 8 )
		if opcode == 246:	# SET 6,(HL) 
			hl = _HL;
			mem[hl] = set( 0x40, peekb( hl ) )
			return ( 15 );
	
		if opcode == 247:	# SET 6,A 
		 A( set( 0x40, _A ) ); return ( 8 )

		if opcode == 248:	# SET 7,B 
		 B( set( 0x80, _B ) ); return ( 8 )
		if opcode == 249:	# SET 7,C 
		 C( set( 0x80,_C ) ); return ( 8 )
		if opcode == 250:	# SET 7,D 
		 D( set( 0x80, Dget() ) ); return ( 8 )
		if opcode == 251:	# SET 7,E 
		 E( set( 0x80, Eget() ) ); return ( 8 )
		if opcode == 252:	# SET 7,H 
		 H( set( 0x80, Hget() ) ); return ( 8 )
		if opcode == 253:	# SET 7,L 
		 L( set( 0x80, Lget() ) ); return ( 8 )
		if opcode == 254:	# SET 7,(HL) 
			hl = _HL;
			mem[hl] = set( 0x80, peekb( hl ) )
			return ( 15 );
	
		if opcode == 255:	# SET 7,A 
		 A( set( 0x80, _A ) ); return ( 8 )

	 # end opcode = 

		return 0;


def execute_id():
		global _R

		_R += 1 

		opcode =  ( nxtpcb() )

		# NOP 
		if opcode in  (0, 1,  2,  3,  4,  5,  6,  7,  8, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 26, 27, 28, 29, 30, 31, 32, 39, 40, 47, 48, 49, 50, 51, 55, 56, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 71, 72, 73, 74, 75, 79, 80, 81, 82, 83, 87, 88, 89, 90, 91, 95, 120, 121, 122, 123, 127, 128, 129, 130, 131, 135, 136, 137, 138, 139, 143, 144, 145, 146, 147, 151, 152, 153, 154, 155, 159, 160, 161, 162, 163, 167, 168, 169, 170, 171, 175, 176, 177, 178, 179, 183, 184, 185, 186, 187, 191, 192, 193, 194, 195, 196, 197, 198, 199, 200, 201, 202, 204, 205, 206, 207, 208, 209, 210, 211, 212, 213, 214, 215, 216, 217, 218, 219, 220, 221, 222, 223, 224, 226, 228, 230, 231, 232, 234, 235, 236, 237, 238, 239, 240, 241, 242, 243, 244, 245, 246, 247, 248):
			PC( dec16( _PC  ) );
			_R += -1
			return ( 4 );
	

		if opcode ==  9: # ADD ID,BC 
		 ID( add16( IDget(), BCget() ) ); return ( 15 )
		if opcode == 25: # ADD ID,DE 
		 ID( add16( IDget(), DEget() ) ); return ( 15 )
		if opcode == 41: # ADD ID,ID 
			id = IDget();
			ID( add16( id, id ) );
			return ( 15 );
	
		if opcode == 57: # ADD ID,SP 
		 ID( add16( IDget(),SPget() ) ); return ( 15 )

		if opcode == 33: # LD ID,nn 
		 ID( nxtpcw() ); return ( 14 )
		if opcode == 34: # LD (nn),ID 
		 pokew( nxtpcw(), IDget() ); return ( 20 )
		if opcode == 42: # LD ID,(nn) 
		 ID( peekw( nxtpcw() ) ); return ( 20 )
		if opcode == 35:# INC ID 
		 ID( inc16( IDget() ) ); return ( 10 )
		if opcode == 43:# DEC ID 
		 ID( dec16( IDget() ) ); return ( 10 )
		if opcode == 36:# INC IDH 
		 IDH( inc8( IDHget() ) ); return ( 8 )
		if opcode == 44:# INC IDL 
		 IDL( inc8( IDLget() ) ); return ( 8 )
		if opcode == 52:# INC (ID+d) 
		    z = ID_d();
		    mem[z] = inc8( peekb(z) )
		    return ( 23 );
	
		if opcode == 37:# DEC IDH 
		 IDH( dec8( IDHget() ) ); return ( 8 )
		if opcode == 45:# DEC IDL 
		 IDL( dec8( IDLget() ) ); return ( 8 )
		if opcode == 53:# DEC (ID+d) 
		    z = ID_d();
		    mem[z] = dec8( peekb(z) )
		    return ( 23 );
	

		if opcode == 38: # LD IDH,n 
		 IDH( nxtpcb() ); return ( 11 )
		if opcode == 46: # LD IDL,n 
		 IDL( nxtpcb() ); return ( 11 )
		if opcode == 54: # LD (ID+d),n 
		 z = ID_d(); mem[z] = nxtpcb(); return ( 19 )

		if opcode == 68: # LD B,IDH 
		 B( IDHget() ); return ( 8 )
		if opcode == 69: # LD B,IDL 
		 B( IDLget() ); return ( 8 )
		if opcode == 70: # LD B,(ID+d) 
		 B( peekb( ID_d() ) ); return ( 19 )

		if opcode == 76: # LD C,IDH 
		 C( IDHget() ); return ( 8 )
		if opcode == 77: # LD C,IDL 
		 C( IDLget() ); return ( 8 )
		if opcode == 78: # LD C,(ID+d) 
		 C( peekb( ID_d() ) ); return ( 19 )

		if opcode == 84: # LD D,IDH 
		 D( IDHget() ); return ( 8 )
		if opcode == 85: # LD D,IDL 
		 D( IDLget() ); return ( 8 )
		if opcode == 86: # LD D,(ID+d) 
		 D( peekb( ID_d() ) ); return ( 19 )

		if opcode == 92: # LD E,IDH 
		 E( IDHget() ); return ( 8 )
		if opcode == 93: # LD E,IDL 
		 E( IDLget() ); return ( 8 )
		if opcode == 94: # LD E,(ID+d) 
		 E( peekb( ID_d() ) ); return ( 19 )

		if opcode == 96: # LD IDH,B 
		 IDH( _B ); return ( 8 )
		if opcode == 97: # LD IDH,C 
		 IDH(_C ); return ( 8 )
		if opcode == 98: # LD IDH,D 
		 IDH( Dget() ); return ( 8 )
		if opcode == 99: # LD IDH,E 
		 IDH( Eget() ); return ( 8 )
		if opcode == 100: # LD IDH,IDH 
		 return ( 8 )
		if opcode == 101: # LD IDH,IDL 
		 IDH( IDLget() ); return ( 8 )
		if opcode == 102: # LD H,(ID+d) 
		 H( peekb( ID_d() ) ); return ( 19 )
		if opcode == 103: # LD IDH,A 
		 IDH( _A ); return ( 8 )

		if opcode == 104: # LD IDL,B 
		 IDL( _B ); return ( 8 )
		if opcode == 105: # LD IDL,C 
		 IDL(_C ); return ( 8 )
		if opcode == 106: # LD IDL,D 
		 IDL( Dget() ); return ( 8 )
		if opcode == 107: # LD IDL,E 
		 IDL( Eget() ); return ( 8 )
		if opcode == 108: # LD IDL,IDH 
		 IDL( IDHget() ); return ( 8 )
		if opcode == 109: # LD IDL,IDL 
		 return ( 8 )
		if opcode == 110: # LD L,(ID+d) 
		 L( peekb( ID_d() ) ); return ( 19 )
		if opcode == 111: # LD IDL,A 
		 IDL( _A ); return ( 8 )

		if opcode == 112: # LD (ID+d),B 
		 mem[ID_d()]=_B ; return ( 19 )
		if opcode == 113: # LD (ID+d),C 
		 mem[ID_d()]=_C ; return ( 19 )
		if opcode == 114: # LD (ID+d),D 
		 mem[ID_d()]=Dget() ; return ( 19 )
		if opcode == 115: # LD (ID+d),E 
		 mem[ID_d()]=Eget() ; return ( 19 )
		if opcode == 116: # LD (ID+d),H 
		 mem[ID_d()]=Hget() ; return ( 19 )
		if opcode == 117: # LD (ID+d),L 
		 mem[ID_d()]=Lget() ; return ( 19 )
		if opcode == 119: # LD (ID+d),A 
		 mem[ID_d()]=_A ; return ( 19 )

		if opcode == 124: # LD A,IDH 
		 A( IDHget() ); return ( 8 )
		if opcode == 125: # LD A,IDL 
		 A( IDLget() ); return ( 8 )
		if opcode == 126: # LD A,(ID+d) 
		 A( peekb( ID_d() ) ); return ( 19 )

		if opcode == 132: # ADD A,IDH 
		 add_a(IDHget()); return ( 8 )
		if opcode == 133: # ADD A,IDL 
		 add_a(IDLget()); return ( 8 )
		if opcode == 134: # ADD A,(ID+d) 
		 add_a(peekb( ID_d() )); return ( 19 )

		if opcode == 140: # ADC A,IDH 
		 adc_a(IDHget()); return ( 8 )
		if opcode == 141: # ADC A,IDL 
		 adc_a(IDLget()); return ( 8 )
		if opcode == 142: # ADC A,(ID+d) 
		 adc_a(peekb( ID_d() )); return ( 19 )

		if opcode == 148: # SUB IDH 
		 sub_a(IDHget()); return ( 8 )
		if opcode == 149: # SUB IDL 
		 sub_a(IDLget()); return ( 8 )
		if opcode == 150: # SUB (ID+d) 
		 sub_a(peekb( ID_d() )); return ( 19 )

		if opcode == 156: # SBC A,IDH 
		 sbc_a(IDHget()); return ( 8 )
		if opcode == 157: # SBC A,IDL 
		 sbc_a(IDLget()); return ( 8 )
		if opcode == 158: # SBC A,(ID+d) 
		 sbc_a(peekb( ID_d() )); return ( 19 )

		if opcode == 164: # AND IDH 
		 and_a(IDHget()); return ( 8 )
		if opcode == 165: # AND IDL 
		 and_a(IDLget()); return ( 8 )
		if opcode == 166: # AND (ID+d) 
		 and_a(peekb( ID_d() )); return ( 19 )

		if opcode == 172: # XOR IDH 
		 xor_a(IDHget()); return ( 8 )
		if opcode == 173: # XOR IDL 
		 xor_a(IDLget()); return ( 8 )
		if opcode == 174: # XOR (ID+d) 
		 xor_a(peekb( ID_d() )); return ( 19 )

		if opcode == 180: # OR IDH 
		 or_a(IDHget()); return ( 8 )
		if opcode == 181: # OR IDL 
		 or_a(IDLget()); return ( 8 )
		if opcode == 182: # OR (ID+d) 
		 or_a(peekb( ID_d() )); return ( 19 )

		if opcode == 188: # CP IDH 
		 cp_a(IDHget()); return ( 8 )
		if opcode == 189: # CP IDL 
		 cp_a(IDLget()); return ( 8 )
		if opcode == 190: # CP (ID+d) 
		 cp_a(peekb( ID_d() )); return ( 19 )

		if opcode == 225: # POP ID 
		 ID( popw() ); return ( 14 )

		if opcode == 233: # JP (ID) 
		 PC( IDget() ); return ( 8 )

		if opcode == 249: # LD SP,ID 
		 SP( IDget() ); return ( 10 )

		if opcode == 203: # prefix CB 
			# Get index address (offset byte is first)
			z = ID_d();
			# Opcode comes after offset byte
			op = nxtpcb();
			execute_id_cb( op, z );
			# Bit instructions take 20 T states, rest 23
			return iif( (( op & 0xc0 ) == 0x40) , 20 , 23 );
	

		if opcode == 227: # EX (SP),ID 
			t = IDget();
			sp = SPget();
			ID( peekw( sp ) );
			pokew( sp, t );
			return ( 23 );
	

		if opcode == 229:    # PUSH ID 
		 pushw( IDget() ); return ( 15 )

	 # end opcode = 

		return 0;



def execute_id_cb(op, z):

		opcode =  ( op )

		if opcode ==   0:	# RLC B 
		 B( op = rlc( peekb( z ) ) ); mem[z]=op ; return
		if opcode ==   1:	# RLC C 
		 C( op = rlc( peekb( z ) ) ); mem[z]=op ; return
		if opcode ==   2:	# RLC D 
		 D( op = rlc( peekb( z ) ) ); mem[z]=op ; return
		if opcode ==   3:	# RLC E 
		 E( op = rlc( peekb( z ) ) ); mem[z]=op ; return
		if opcode ==   4:	# RLC H 
		 H( op = rlc( peekb( z ) ) ); mem[z]=op ; return
		if opcode ==   5:	# RLC L 
		 L( op = rlc( peekb( z ) ) ); mem[z]=op ; return
		if opcode ==   6:	# RLC (HL) 
		 mem[z]=rlc( peekb( z ) ) ; return
		if opcode ==   7:	# RLC A 
		 A( op = rlc( peekb( z ) ) ); mem[z]=op ; return

		if opcode ==   8:	# RRC B 
		 B( op = rrc( peekb( z ) ) ); pokeb( z, op ); return
		if opcode ==   9:	# RRC C 
		 C( op = rrc( peekb( z ) ) ); pokeb( z, op ); return
		if opcode ==  10:	# RRC D 
		 D( op = rrc( peekb( z ) ) ); pokeb( z, op ); return
		if opcode ==  11:	# RRC E 
		 E( op = rrc( peekb( z ) ) ); pokeb( z, op ); return
		if opcode ==  12:	# RRC H 
		 H( op = rrc( peekb( z ) ) ); pokeb( z, op ); return
		if opcode ==  13:	# RRC L 
		 L( op = rrc( peekb( z ) ) ); pokeb( z, op ); return
		if opcode ==  14:	# RRC (HL) 
		 pokeb( z, rrc( peekb( z ) ) ); return
		if opcode ==  15:	# RRC A 
		 A( op = rrc( peekb( z ) ) ); pokeb( z, op ); return

		if opcode ==  16:	# RL B 
		 B( op = rl( peekb( z ) ) ); pokeb( z, op ); return
		if opcode ==  17:	# RL C 
		 C( op = rl( peekb( z ) ) ); pokeb( z, op ); return
		if opcode ==  18:	# RL D 
		 D( op = rl( peekb( z ) ) ); pokeb( z, op ); return
		if opcode ==  19:	# RL E 
		 E( op = rl( peekb( z ) ) ); pokeb( z, op ); return
		if opcode ==  20:	# RL H 
		 H( op = rl( peekb( z ) ) ); pokeb( z, op ); return
		if opcode ==  21:	# RL L 
		 L( op = rl( peekb( z ) ) ); pokeb( z, op ); return
		if opcode ==  22:	# RL (HL) 
		 pokeb( z, rl( peekb( z ) ) ); return
		if opcode ==  23:	# RL A 
		 A( op = rl( peekb( z ) ) ); pokeb( z, op ); return

		if opcode ==  24:	# RR B 
		 B( op = rr( peekb( z ) ) ); pokeb( z, op ); return
		if opcode ==  25:	# RR C 
		 C( op = rr( peekb( z ) ) ); pokeb( z, op ); return
		if opcode ==  26:	# RR D 
		 D( op = rr( peekb( z ) ) ); pokeb( z, op ); return
		if opcode ==  27:	# RR E 
		 E( op = rr( peekb( z ) ) ); pokeb( z, op ); return
		if opcode ==  28:	# RR H 
		 H( op = rr( peekb( z ) ) ); pokeb( z, op ); return
		if opcode ==  29:	# RR L 
		 L( op = rr( peekb( z ) ) ); pokeb( z, op ); return
		if opcode ==  30:	# RR (HL) 
		 pokeb( z, rr( peekb( z ) ) ); return
		if opcode ==  31:	# RR A 
		 A( op = rr( peekb( z ) ) ); pokeb( z, op ); return

		if opcode ==  32:	# SLA B 
		 B( op = sla( peekb( z ) ) ); pokeb( z, op ); return
		if opcode ==  33:	# SLA C 
		 C( op = sla( peekb( z ) ) ); pokeb( z, op ); return
		if opcode ==  34:	# SLA D 
		 D( op = sla( peekb( z ) ) ); pokeb( z, op ); return
		if opcode ==  35:	# SLA E 
		 E( op = sla( peekb( z ) ) ); pokeb( z, op ); return
		if opcode ==  36:	# SLA H 
		 H( op = sla( peekb( z ) ) ); pokeb( z, op ); return
		if opcode ==  37:	# SLA L 
		 L( op = sla( peekb( z ) ) ); pokeb( z, op ); return
		if opcode ==  38:	# SLA (HL) 
		 pokeb( z, sla( peekb( z ) ) ); return
		if opcode ==  39:	# SLA A 
		 A( op = sla( peekb( z ) ) ); pokeb( z, op ); return

		if opcode ==  40:	# SRA B 
		 B( op = sra( peekb( z ) ) ); pokeb( z, op ); return
		if opcode ==  41:	# SRA C 
		 C( op = sra( peekb( z ) ) ); pokeb( z, op ); return
		if opcode ==  42:	# SRA D 
		 D( op = sra( peekb( z ) ) ); pokeb( z, op ); return
		if opcode ==  43:	# SRA E 
		 E( op = sra( peekb( z ) ) ); pokeb( z, op ); return
		if opcode ==  44:	# SRA H 
		 H( op = sra( peekb( z ) ) ); pokeb( z, op ); return
		if opcode ==  45:	# SRA L 
		 L( op = sra( peekb( z ) ) ); pokeb( z, op ); return
		if opcode ==  46:	# SRA (HL) 
		 pokeb( z, sra( peekb( z ) ) ); return
		if opcode ==  47:	# SRA A 
		 A( op = sra( peekb( z ) ) ); pokeb( z, op ); return

		if opcode ==  48:	# SLS B 
		 B( op = sls( peekb( z ) ) ); pokeb( z, op ); return
		if opcode ==  49:	# SLS C 
		 C( op = sls( peekb( z ) ) ); pokeb( z, op ); return
		if opcode ==  50:	# SLS D 
		 D( op = sls( peekb( z ) ) ); pokeb( z, op ); return
		if opcode ==  51:	# SLS E 
		 E( op = sls( peekb( z ) ) ); pokeb( z, op ); return
		if opcode ==  52:	# SLS H 
		 H( op = sls( peekb( z ) ) ); pokeb( z, op ); return
		if opcode ==  53:	# SLS L 
		 L( op = sls( peekb( z ) ) ); pokeb( z, op ); return
		if opcode ==  54:	# SLS (HL) 
		 pokeb( z, sls( peekb( z ) ) ); return
		if opcode ==  55:	# SLS A 
		 A( op = sls( peekb( z ) ) ); pokeb( z, op ); return

		if opcode ==  56:	# SRL B 
		 B( op = srl( peekb( z ) ) ); pokeb( z, op ); return
		if opcode ==  57:	# SRL C 
		 C( op = srl( peekb( z ) ) ); pokeb( z, op ); return
		if opcode ==  58:	# SRL D 
		 D( op = srl( peekb( z ) ) ); pokeb( z, op ); return
		if opcode ==  59:	# SRL E 
		 E( op = srl( peekb( z ) ) ); pokeb( z, op ); return
		if opcode ==  60:	# SRL H 
		 H( op = srl( peekb( z ) ) ); pokeb( z, op ); return
		if opcode ==  61:	# SRL L 
		 L( op = srl( peekb( z ) ) ); pokeb( z, op ); return
		if opcode ==  62:	# SRL (HL) 
		 pokeb( z, srl( peekb( z ) ) ); return
		if opcode ==  63:	# SRL A 
		 A( op = srl( peekb( z ) ) ); pokeb( z, op ); return

		if opcode in  (64, 65, 66, 67, 68, 69, 70, 71):	# BIT 0,B 
		 bit( 0x01, peekb( z ) ); return

		if opcode in  (72, 73, 74, 75, 76, 77, 78, 79): # BIT 1,B
		 bit( 0x02, peekb( z ) ); return

		if opcode in  (80, 81, 82, 83, 84, 85, 86, 87):	# BIT 2,B 
		 bit( 0x04, peekb( z ) ); return

		if opcode in  (88, 89, 90, 91, 92, 93, 94, 95):	# BIT 3,B 
		 bit( 0x08, peekb( z ) ); return

		if opcode in  (96, 97, 98, 99,100,101,102,103):	# BIT 4,B 
		 bit( 0x10, peekb( z ) ); return

		if opcode in (104,105,106,107,108,109,110,111):	# BIT 5,B 
		 bit( 0x20, peekb( z ) ); return

		if opcode in (112,113,114,115,116,117,118,119):	# BIT 6,B 
		 bit( 0x40, peekb( z ) ); return

		if opcode in (120,121,122,123,124,125,126,127):	# BIT 7,B 
		 bit( 0x80, peekb( z ) ); return

		if opcode == 128:	# RES 0,B 
		 B( op = res( 0x01, peekb( z ) ) ); pokeb( z, op ); return
		if opcode == 129:	# RES 0,C 
		 C( op = res( 0x01, peekb( z ) ) ); pokeb( z, op ); return
		if opcode == 130:	# RES 0,D 
		 D( op = res( 0x01, peekb( z ) ) ); pokeb( z, op ); return
		if opcode == 131:	# RES 0,E 
		 E( op = res( 0x01, peekb( z ) ) ); pokeb( z, op ); return
		if opcode == 132:	# RES 0,H 
		 H( op = res( 0x01, peekb( z ) ) ); pokeb( z, op ); return
		if opcode == 133:	# RES 0,L 
		 L( op = res( 0x01, peekb( z ) ) ); pokeb( z, op ); return
		if opcode == 134:	# RES 0,(HL) 
		 pokeb( z, res( 0x01, peekb( z ) ) ); return
		if opcode == 135:	# RES 0,A 
		 A( op = res( 0x01, peekb( z ) ) ); pokeb( z, op ); return

		if opcode == 136:	# RES 1,B 
		 B( op = res( 0x02, peekb( z ) ) ); pokeb( z, op ); return
		if opcode == 137:	# RES 1,C 
		 C( op = res( 0x02, peekb( z ) ) ); pokeb( z, op ); return
		if opcode == 138:	# RES 1,D 
		 D( op = res( 0x02, peekb( z ) ) ); pokeb( z, op ); return
		if opcode == 139:	# RES 1,E 
		 E( op = res( 0x02, peekb( z ) ) ); pokeb( z, op ); return
		if opcode == 140:	# RES 1,H 
		 H( op = res( 0x02, peekb( z ) ) ); pokeb( z, op ); return
		if opcode == 141:	# RES 1,L 
		 L( op = res( 0x02, peekb( z ) ) ); pokeb( z, op ); return
		if opcode == 142:	# RES 1,(HL) 
		 pokeb( z, res( 0x02, peekb( z ) ) ); return
		if opcode == 143:	# RES 1,A 
		 A( op = res( 0x02, peekb( z ) ) ); pokeb( z, op ); return

		if opcode == 144:	# RES 2,B 
		 B( op = res( 0x04, peekb( z ) ) ); pokeb( z, op ); return
		if opcode == 145:	# RES 2,C 
		 C( op = res( 0x04, peekb( z ) ) ); pokeb( z, op ); return
		if opcode == 146:	# RES 2,D 
		 D( op = res( 0x04, peekb( z ) ) ); pokeb( z, op ); return
		if opcode == 147:	# RES 2,E 
		 E( op = res( 0x04, peekb( z ) ) ); pokeb( z, op ); return
		if opcode == 148:	# RES 2,H 
		 H( op = res( 0x04, peekb( z ) ) ); pokeb( z, op ); return
		if opcode == 149:	# RES 2,L 
		 L( op = res( 0x04, peekb( z ) ) ); pokeb( z, op ); return
		if opcode == 150:	# RES 2,(HL) 
		 pokeb( z, res( 0x04, peekb( z ) ) ); return
		if opcode == 151:	# RES 2,A 
		 A( op = res( 0x04, peekb( z ) ) ); pokeb( z, op ); return

		if opcode == 152:	# RES 3,B 
		 B( op = res( 0x08, peekb( z ) ) ); pokeb( z, op ); return
		if opcode == 153:	# RES 3,C 
		 C( op = res( 0x08, peekb( z ) ) ); pokeb( z, op ); return
		if opcode == 154:	# RES 3,D 
		 D( op = res( 0x08, peekb( z ) ) ); pokeb( z, op ); return
		if opcode == 155:	# RES 3,E 
		 E( op = res( 0x08, peekb( z ) ) ); pokeb( z, op ); return
		if opcode == 156:	# RES 3,H 
		 H( op = res( 0x08, peekb( z ) ) ); pokeb( z, op ); return
		if opcode == 157:	# RES 3,L 
		 L( op = res( 0x08, peekb( z ) ) ); pokeb( z, op ); return
		if opcode == 158:	# RES 3,(HL) 
		 pokeb( z, res( 0x08, peekb( z ) ) ); return
		if opcode == 159:	# RES 3,A 
		 A( op = res( 0x08, peekb( z ) ) ); pokeb( z, op ); return

		if opcode == 160:	# RES 4,B 
		 B( op = res( 0x10, peekb( z ) ) ); pokeb( z, op ); return
		if opcode == 161:	# RES 4,C 
		 C( op = res( 0x10, peekb( z ) ) ); pokeb( z, op ); return
		if opcode == 162:	# RES 4,D 
		 D( op = res( 0x10, peekb( z ) ) ); pokeb( z, op ); return
		if opcode == 163:	# RES 4,E 
		 E( op = res( 0x10, peekb( z ) ) ); pokeb( z, op ); return
		if opcode == 164:	# RES 4,H 
		 H( op = res( 0x10, peekb( z ) ) ); pokeb( z, op ); return
		if opcode == 165:	# RES 4,L 
		 L( op = res( 0x10, peekb( z ) ) ); pokeb( z, op ); return
		if opcode == 166:	# RES 4,(HL) 
		 pokeb( z, res( 0x10, peekb( z ) ) ); return
		if opcode == 167:	# RES 4,A 
		 A( op = res( 0x10, peekb( z ) ) ); pokeb( z, op ); return

		if opcode == 168:	# RES 5,B 
		 B( op = res( 0x20, peekb( z ) ) ); pokeb( z, op ); return
		if opcode == 169:	# RES 5,C 
		 C( op = res( 0x20, peekb( z ) ) ); pokeb( z, op ); return
		if opcode == 170:	# RES 5,D 
		 D( op = res( 0x20, peekb( z ) ) ); pokeb( z, op ); return
		if opcode == 171:	# RES 5,E 
		 E( op = res( 0x20, peekb( z ) ) ); pokeb( z, op ); return
		if opcode == 172:	# RES 5,H 
		 H( op = res( 0x20, peekb( z ) ) ); pokeb( z, op ); return
		if opcode == 173:	# RES 5,L 
		 L( op = res( 0x20, peekb( z ) ) ); pokeb( z, op ); return
		if opcode == 174:	# RES 5,(HL) 
		 pokeb( z, res( 0x20, peekb( z ) ) ); return
		if opcode == 175:	# RES 5,A 
		 A( op = res( 0x20, peekb( z ) ) ); pokeb( z, op ); return

		if opcode == 176:	# RES 6,B 
		 B( op = res( 0x40, peekb( z ) ) ); pokeb( z, op ); return
		if opcode == 177:	# RES 6,C 
		 C( op = res( 0x40, peekb( z ) ) ); pokeb( z, op ); return
		if opcode == 178:	# RES 6,D 
		 D( op = res( 0x40, peekb( z ) ) ); pokeb( z, op ); return
		if opcode == 179:	# RES 6,E 
		 E( op = res( 0x40, peekb( z ) ) ); pokeb( z, op ); return
		if opcode == 180:	# RES 6,H 
		 H( op = res( 0x40, peekb( z ) ) ); pokeb( z, op ); return
		if opcode == 181:	# RES 6,L 
		 L( op = res( 0x40, peekb( z ) ) ); pokeb( z, op ); return
		if opcode == 182:	# RES 6,(HL) 
		 pokeb( z, res( 0x40, peekb( z ) ) ); return
		if opcode == 183:	# RES 6,A 
		 A( op = res( 0x40, peekb( z ) ) ); pokeb( z, op ); return

		if opcode == 184:	# RES 7,B 
		 B( op = res( 0x80, peekb( z ) ) ); pokeb( z, op ); return
		if opcode == 185:	# RES 7,C 
		 C( op = res( 0x80, peekb( z ) ) ); pokeb( z, op ); return
		if opcode == 186:	# RES 7,D 
		 D( op = res( 0x80, peekb( z ) ) ); pokeb( z, op ); return
		if opcode == 187:	# RES 7,E 
		 E( op = res( 0x80, peekb( z ) ) ); pokeb( z, op ); return
		if opcode == 188:	# RES 7,H 
		 H( op = res( 0x80, peekb( z ) ) ); pokeb( z, op ); return
		if opcode == 189:	# RES 7,L 
		 L( op = res( 0x80, peekb( z ) ) ); pokeb( z, op ); return
		if opcode == 190:	# RES 7,(HL) 
		 pokeb( z, res( 0x80, peekb( z ) ) ); return
		if opcode == 191:	# RES 7,A 
		 A( op = res( 0x80, peekb( z ) ) ); pokeb( z, op ); return

		if opcode == 192:	# SET 0,B 
		 B( op = set( 0x01, peekb( z ) ) ); pokeb( z, op ); return
		if opcode == 193:	# SET 0,C 
		 C( op = set( 0x01, peekb( z ) ) ); pokeb( z, op ); return
		if opcode == 194:	# SET 0,D 
		 D( op = set( 0x01, peekb( z ) ) ); pokeb( z, op ); return
		if opcode == 195:	# SET 0,E 
		 E( op = set( 0x01, peekb( z ) ) ); pokeb( z, op ); return
		if opcode == 196:	# SET 0,H 
		 H( op = set( 0x01, peekb( z ) ) ); pokeb( z, op ); return
		if opcode == 197:	# SET 0,L 
		 L( op = set( 0x01, peekb( z ) ) ); pokeb( z, op ); return
		if opcode == 198:	# SET 0,(HL) 
		 pokeb( z, set( 0x01, peekb( z ) ) ); return
		if opcode == 199:	# SET 0,A 
		 A( op = set( 0x01, peekb( z ) ) ); pokeb( z, op ); return

		if opcode == 200:	# SET 1,B 
		 B( op = set( 0x02, peekb( z ) ) ); pokeb( z, op ); return
		if opcode == 201:	# SET 1,C 
		 C( op = set( 0x02, peekb( z ) ) ); pokeb( z, op ); return
		if opcode == 202:	# SET 1,D 
		 D( op = set( 0x02, peekb( z ) ) ); pokeb( z, op ); return
		if opcode == 203:	# SET 1,E 
		 E( op = set( 0x02, peekb( z ) ) ); pokeb( z, op ); return
		if opcode == 204:	# SET 1,H 
		 H( op = set( 0x02, peekb( z ) ) ); pokeb( z, op ); return
		if opcode == 205:	# SET 1,L 
		 L( op = set( 0x02, peekb( z ) ) ); pokeb( z, op ); return
		if opcode == 206:	# SET 1,(HL) 
		 pokeb( z, set( 0x02, peekb( z ) ) ); return
		if opcode == 207:	# SET 1,A 
		 A( op = set( 0x02, peekb( z ) ) ); pokeb( z, op ); return

		if opcode == 208:	# SET 2,B 
		 B( op = set( 0x04, peekb( z ) ) ); pokeb( z, op ); return
		if opcode == 209:	# SET 2,C 
		 C( op = set( 0x04, peekb( z ) ) ); pokeb( z, op ); return
		if opcode == 210:	# SET 2,D 
		 D( op = set( 0x04, peekb( z ) ) ); pokeb( z, op ); return
		if opcode == 211:	# SET 2,E 
		 E( op = set( 0x04, peekb( z ) ) ); pokeb( z, op ); return
		if opcode == 212:	# SET 2,H 
		 H( op = set( 0x04, peekb( z ) ) ); pokeb( z, op ); return
		if opcode == 213:	# SET 2,L 
		 L( op = set( 0x04, peekb( z ) ) ); pokeb( z, op ); return
		if opcode == 214:	# SET 2,(HL) 
		 pokeb( z, set( 0x04, peekb( z ) ) ); return
		if opcode == 215:	# SET 2,A 
		 A( op = set( 0x04, peekb( z ) ) ); pokeb( z, op ); return

		if opcode == 216:	# SET 3,B 
		 B( op = set( 0x08, peekb( z ) ) ); pokeb( z, op ); return
		if opcode == 217:	# SET 3,C 
		 C( op = set( 0x08, peekb( z ) ) ); pokeb( z, op ); return
		if opcode == 218:	# SET 3,D 
		 D( op = set( 0x08, peekb( z ) ) ); pokeb( z, op ); return
		if opcode == 219:	# SET 3,E 
		 E( op = set( 0x08, peekb( z ) ) ); pokeb( z, op ); return
		if opcode == 220:	# SET 3,H 
		 H( op = set( 0x08, peekb( z ) ) ); pokeb( z, op ); return
		if opcode == 221:	# SET 3,L 
		 L( op = set( 0x08, peekb( z ) ) ); pokeb( z, op ); return
		if opcode == 222:	# SET 3,(HL) 
		 pokeb( z, set( 0x08, peekb( z ) ) ); return
		if opcode == 223:	# SET 3,A 
		 A( op = set( 0x08, peekb( z ) ) ); pokeb( z, op ); return

		if opcode == 224:	# SET 4,B 
		 B( op = set( 0x10, peekb( z ) ) ); pokeb( z, op ); return
		if opcode == 225:	# SET 4,C 
		 C( op = set( 0x10, peekb( z ) ) ); pokeb( z, op ); return
		if opcode == 226:	# SET 4,D 
		 D( op = set( 0x10, peekb( z ) ) ); pokeb( z, op ); return
		if opcode == 227:	# SET 4,E 
		 E( op = set( 0x10, peekb( z ) ) ); pokeb( z, op ); return
		if opcode == 228:	# SET 4,H 
		 H( op = set( 0x10, peekb( z ) ) ); pokeb( z, op ); return
		if opcode == 229:	# SET 4,L 
		 L( op = set( 0x10, peekb( z ) ) ); pokeb( z, op ); return
		if opcode == 230:	# SET 4,(HL) 
		 pokeb( z, set( 0x10, peekb( z ) ) ); return
		if opcode == 231:	# SET 4,A 
		 A( op = set( 0x10, peekb( z ) ) ); pokeb( z, op ); return

		if opcode == 232:	# SET 5,B 
		 B( op = set( 0x20, peekb( z ) ) ); pokeb( z, op ); return
		if opcode == 233:	# SET 5,C 
		 C( op = set( 0x20, peekb( z ) ) ); pokeb( z, op ); return
		if opcode == 234:	# SET 5,D 
		 D( op = set( 0x20, peekb( z ) ) ); pokeb( z, op ); return
		if opcode == 235:	# SET 5,E 
		 E( op = set( 0x20, peekb( z ) ) ); pokeb( z, op ); return
		if opcode == 236:	# SET 5,H 
		 H( op = set( 0x20, peekb( z ) ) ); pokeb( z, op ); return
		if opcode == 237:	# SET 5,L 
		 L( op = set( 0x20, peekb( z ) ) ); pokeb( z, op ); return
		if opcode == 238:	# SET 5,(HL) 
		 pokeb( z, set( 0x20, peekb( z ) ) ); return
		if opcode == 239:	# SET 5,A 
		 A( op = set( 0x20, peekb( z ) ) ); pokeb( z, op ); return

		if opcode == 240:	# SET 6,B 
		 B( op = set( 0x40, peekb( z ) ) ); pokeb( z, op ); return
		if opcode == 241:	# SET 6,C 
		 C( op = set( 0x40, peekb( z ) ) ); pokeb( z, op ); return
		if opcode == 242:	# SET 6,D 
		 D( op = set( 0x40, peekb( z ) ) ); pokeb( z, op ); return
		if opcode == 243:	# SET 6,E 
		 E( op = set( 0x40, peekb( z ) ) ); pokeb( z, op ); return
		if opcode == 244:	# SET 6,H 
		 H( op = set( 0x40, peekb( z ) ) ); pokeb( z, op ); return
		if opcode == 245:	# SET 6,L 
		 L( op = set( 0x40, peekb( z ) ) ); pokeb( z, op ); return
		if opcode == 246:	# SET 6,(HL) 
		 pokeb( z, set( 0x40, peekb( z ) ) ); return
		if opcode == 247:	# SET 6,A 
		 A( op = set( 0x40, peekb( z ) ) ); pokeb( z, op ); return

		if opcode == 248:	# SET 7,B 
		 B( op = set( 0x80, peekb( z ) ) ); pokeb( z, op ); return
		if opcode == 249:	# SET 7,C 
		 C( op = set( 0x80, peekb( z ) ) ); pokeb( z, op ); return
		if opcode == 250:	# SET 7,D 
		 D( op = set( 0x80, peekb( z ) ) ); pokeb( z, op ); return
		if opcode == 251:	# SET 7,E 
		 E( op = set( 0x80, peekb( z ) ) ); pokeb( z, op ); return
		if opcode == 252:	# SET 7,H 
		 H( op = set( 0x80, peekb( z ) ) ); pokeb( z, op ); return
		if opcode == 253:	# SET 7,L 
		 L( op = set( 0x80, peekb( z ) ) ); pokeb( z, op ); return
		if opcode == 254:	# SET 7,(HL) 
		 pokeb( z, set( 0x80, peekb( z ) ) ); return
		if opcode == 255:	# SET 7,A 
		 A( op = set( 0x80, peekb( z ) ) ); pokeb( z, op ); return

	 # end switch



def in_bc():
		ans = inb( BCget() );

		setZ( ans == 0 )
		setS(ans & F_S)
		set3(ans & F_3)
		set5(ans & F_5)
		setPV( parity[ ans ] )
		setN( False )
		setH( False )

		return ans;


# Add with carry - alters all flags (CHECKED) 
def	adc_a( b ):
		a    = _A;
		c    = iif(fC , 1 , 0)
		wans = a + b + c;
		ans  = wans & 0xff;

		setS( (ans & F_S)  != 0 );
		set3( (ans & F_3)  != 0 );
		set5( (ans & F_5)  != 0 );
		setZ( (ans)        == 0 );
		setC( (wans&0x100) != 0 );
		setPV( ((a ^ ~b) & (a ^ ans) & 0x80) != 0 );
		setH(  (((a & 0x0f) + (b & 0x0f) + c) & F_H) != 0 );
		setN( False );

		A( ans );


# Add - alters all flags (CHECKED) 
def	add_a( b ):
		a    = _A;
		wans = a + b;
		ans  = wans & 0xff;

		setS( (ans & F_S)  != 0 );
		set3( (ans & F_3)  != 0 );
		set5( (ans & F_5)  != 0 );
		setZ( (ans)        == 0 );
		setC( (wans&0x100) != 0 );
		setPV( ((a ^ ~b) & (a ^ ans) & 0x80) != 0 );
		setH(  (((a & 0x0f) + (b & 0x0f)) & F_H) != 0 );
		setN( False );

		A( ans );
		#print 'add_a(%d): a=%d wans=%d ans=%d' % (b, a, wans, ans)

# Subtract with carry - alters all flags (CHECKED) 
def	sbc_a( b ):
		a    = _A;
		c    = iif(fC , 1 , 0)
		wans = a - b - c;
		ans  = wans & 0xff;

		setS( (ans & F_S)  != 0 );
		set3( (ans & F_3)  != 0 );
		set5( (ans & F_5)  != 0 );
		setZ( (ans)        == 0 );
		setC( (wans&0x100) != 0 );
		setPV( ((a ^ b) & (a ^ ans) & 0x80) != 0 );
		setH(  (((a & 0x0f) - (b & 0x0f) - c) & F_H) != 0 );
		setN( True );

		A( ans );


# Subtract - alters all flags (CHECKED) 
def	sub_a( b ):
		a    = _A;
		wans = a - b;
		ans  = wans & 0xff;

		setS( (ans & F_S)  != 0 );
		set3( (ans & F_3)  != 0 );
		set5( (ans & F_5)  != 0 );
		setZ( (ans)        == 0 );
		setC( (wans&0x100) != 0 );
		setPV( ((a ^ b) & (a ^ ans) & 0x80) != 0 );
		setH(  (((a & 0x0f) - (b & 0x0f)) & F_H) != 0 );
		setN( True );

		A( ans );


# Rotate Left - alters H N C 3 5 flags (CHECKED) 
def	rlc_a():
		ans = _A;
		c   = (ans & 0x80) != 0;

		if ( c ):
			ans = (ans << 1)|0x01;
		else:
			ans <<= 1;
	
		ans &= 0xff;

		set3( (ans & F_3)  != 0 );
		set5( (ans & F_5)  != 0 );
		setN( False );
		setH( False );
		setC( c );

		A( ans );


# Rotate Right - alters H N C 3 5 flags (CHECKED) 
def	rrc_a():
		ans = _A;
		c   = (ans & 0x01) != 0;

		if ( c ):
			ans = (ans >> 1)|0x80;
		else:
			ans >>= 1;
	

		set3( (ans & F_3)  != 0 );
		set5( (ans & F_5)  != 0 );
		setN( False );
		setH( False );
		setC( c );

		A( ans );


# Rotate Left through Carry - alters H N C 3 5 flags (CHECKED) 
def	rl_a():
		ans = _A;
		c   = (ans & 0x80) != 0;

		if ( fC ):
			ans = (ans << 1) | 0x01;
		else:
			ans <<= 1;
	

		ans &= 0xff;

		set3( (ans & F_3)  != 0 );
		set5( (ans & F_5)  != 0 );
		setN( False );
		setH( False );
		setC( c );

		A( ans );


# Rotate Right through Carry - alters H N C 3 5 flags (CHECKED) 
def	rr_a():
		ans = _A;
		c   = (ans & 0x01) != 0;

		if ( fC ):
			ans = (ans >> 1) | 0x80;
		else:
			ans >>= 1;
	

		set3( (ans & F_3)  != 0 );
		set5( (ans & F_5)  != 0 );
		setN( False );
		setH( False );
		setC( c );

		A( ans );

#TODO: check comparisons !
# Compare - alters all flags (CHECKED) 
def	cp_a( b ):
		global fS, f3, f5, fN, fZ, fC, fH, fPV

		a    = _A
		wans = a - b
		ans  = wans & 0xff

		fS=(ans & F_S)
		f3=(b & F_3)
		f5=(b & F_5)
		fN=(True )
		fZ=(ans == 0 )
		fC=(wans & 0x100)
		fH=(((a & 0x0f) - (b & 0x0f)) & F_H)
		fPV=((a ^ b) & (a ^ ans) & 0x80)


# Bitwise and - alters all flags (CHECKED) 
def	and_a( b ):
		global fS, f3, f5, fN, fZ, fC, fH, fPV
		ans = _A & b;

		fS=( (ans & F_S) != 0 );
		f3=( (ans & F_3) != 0 );
		f5=( (ans & F_5) != 0 );
		fH=( True );
		fPV=( parity[ ans ] );
		fZ=( ans == 0 );
		fN=( False );
		fC=( False );

		A( ans );


# Bitwise or - alters all flags (CHECKED) 
def	or_a( b ):
		global fS, f3, f5, fN, fZ, fC, fH, fPV
		ans = _A | b;

		fS=( (ans & F_S) != 0 );
		f3=( (ans & F_3) != 0 );
		f5=( (ans & F_5) != 0 );
		fH=( False );
		fPV=( parity[ ans ] );
		fZ=( ans == 0 );
		fN=( False );
		fC=( False );

		A( ans );


# Bitwise exclusive or - alters all flags (CHECKED) 
def	xor_a( b ):
		global fS, f3, f5, fN, fZ, fC, fH, fPV
		ans = (_A ^ b) & 0xff;

		fS=( (ans & F_S) != 0 );
		f3=( (ans & F_3) != 0 );
		f5=( (ans & F_5) != 0 );
		fH=( False );
		fPV=( parity[ ans ] );
		fZ=( ans == 0 );
		fN=( False );
		fC=( False );    

		A( ans );


# Negate (Two's complement) - alters all flags (CHECKED) 
def	neg_a():
		t = _A;

		A( 0 );
		sub_a(t);


# One's complement - alters N H 3 5 flags (CHECKED) 
def	cpl_a():
		ans = _A ^ 0xff;

		set3( (ans & F_3) != 0 );
		set5( (ans & F_5) != 0 );
		setH( True );    
		setN( True );    

		A( ans );


# Decimal Adjust Accumulator - alters all flags (CHECKED) 
def	daa_a():
		ans = _A;
		incr = 0;
		carry = fC;

		if ( fH or ((ans & 0x0f) > 0x09)):
			incr |= 0x06;
	
		if (carry or (ans > 0x9f) or ((ans > 0x8f) and ((ans & 0x0f) > 0x09))):
			incr |= 0x60;
	
		if (ans > 0x99):
			carry = True;
	
		if fN:
			sub_a(incr);
		else:
			add_a(incr);
	

		ans = _A;

		setC( carry );
		setPV( parity[ ans ] );


# Load a with i - (NOT CHECKED) 
def	ld_a_i():
		ans = Iget();

		setS( (ans & F_S) != 0 );
		set3( (ans & F_3) != 0 );
		set5( (ans & F_5) != 0 );
		setZ( ans == 0 );
		setPV( IFF2get() );
		setH( False );    
		setN( False );    

		A( ans );


# Load a with r - (NOT CHECKED) 
def	ld_a_r():
		ans = Rget();

		setS( (ans & F_S) != 0 );
		set3( (ans & F_3) != 0 );
		set5( (ans & F_5) != 0 );
		setZ( ans == 0 );
		setPV( IFF2get() );
		setH( False );
		setN( False );

		A( ans );


# Rotate right through a and (hl) - (NOT CHECKED) 
def	rrd_a():
		ans = _A;
		t   = peekb( _HL );
		q   = t;

		t   = (t >> 4) | (ans << 4);
		ans = (ans & 0xf0) | (q & 0x0f);
		pokeb( _HL, t );

		setS( (ans & F_S) != 0 );
		set3( (ans & F_3) != 0 );
		set5( (ans & F_5) != 0 );
		setZ( ans == 0 );
		setPV( IFF2get() );
		setH( False );    
		setN( False );        

		A( ans );


# Rotate left through a and (hl) - (NOT CHECKED) 
def	rld_a():
		ans = _A;
		t   = peekb( _HL );
		q   = t;

		t   = (t << 4) | (ans & 0x0f);
		ans = (ans & 0xf0) | (q >> 4);
		pokeb( _HL, (t & 0xff) );

		setS( (ans & F_S) != 0 );
		set3( (ans & F_3) != 0 );
		set5( (ans & F_5) != 0 );
		setZ( ans == 0 );
		setPV( IFF2get() );
		setH( False );    
		setN( False );            

		A( ans );


# Test bit - alters all but C flag (CHECKED) 
def	bit( b, r ):
		bitSet = bool((r & b) != 0);

		setN( False );
		setH( True );
		set3( (r & F_3) != 0 );
		set5( (r & F_5) != 0 );
		setS( iif((b == F_S) , bitSet , False) );
		setZ(  not bitSet );
		setPV( not bitSet );


# Set carry flag - alters N H 3 5 C flags (CHECKED) 
def	scf():
		ans = _A;

		set3( (ans & F_3) != 0 );
		set5( (ans & F_5) != 0 );
		setN( False );
		setH( False );
		setC( True );


# Complement carry flag - alters N 3 5 C flags (CHECKED) 
def	ccf():
		ans = _A;

		set3( (ans & F_3) != 0 );
		set5( (ans & F_5) != 0 );
		setN( False );
		setC( iif(fC , False , True ))


# Rotate left - alters all flags (CHECKED) 
def	rlc( ans ):
		c = bool((ans & 0x80) != 0)

		if ( c ):
			ans = (ans << 1)|0x01;
		else:
			ans <<= 1;
	
		ans &= 0xff;

		setS( (ans & F_S) != 0 );
		set3( (ans & F_3) != 0 );
		set5( (ans & F_5) != 0 );
		setZ( (ans) == 0 );
		setPV( parity[ ans ] );
		setH( False );
		setN( False );
		setC( c );    

		return(ans);


# Rotate right - alters all flags (CHECKED) 
def	rrc( ans ):
		c = bool((ans & 0x01) != 0)

		if ( c ):
			ans = (ans >> 1)|0x80;
		else:
			ans >>= 1;
	

		setS( (ans & F_S) != 0 );
		set3( (ans & F_3) != 0 );
		set5( (ans & F_5) != 0 );
		setZ( (ans) == 0 );
		setPV( parity[ ans ] );
		setH( False );
		setN( False );
		setC( c );    

		return(ans);


# Rotate left through carry - alters all flags (CHECKED) 
def	rl( ans ):
		c = bool((ans & 0x80) != 0)

		if ( fC ):
			ans = (ans << 1) | 0x01;
		else:
			ans <<= 1;
	
		ans &= 0xff;

		setS( (ans & F_S) != 0 );
		set3( (ans & F_3) != 0 );
		set5( (ans & F_5) != 0 );
		setZ( (ans) == 0 );
		setPV( parity[ ans ] );
		setH( False );
		setN( False );
		setC( c );    

		return(ans);


# Rotate right through carry - alters all flags (CHECKED) 
def	rr( ans ):
		c = bool((ans & 0x01) != 0)

		if ( fC ):
			ans = (ans >> 1) | 0x80;
		else:
			ans >>= 1;
	

		setS( (ans & F_S) != 0 );
		set3( (ans & F_3) != 0 );
		set5( (ans & F_5) != 0 );
		setZ( (ans) == 0 );
		setPV( parity[ ans ] );
		setH( False );
		setN( False );
		setC( c );    

		return(ans);


# Shift Left Arithmetically - alters all flags (CHECKED) 
def	sla( ans ):
		c = bool((ans & 0x80) != 0)
		ans = (ans << 1) & 0xff;
    
		setS( (ans & F_S) != 0 );
		set3( (ans & F_3) != 0 );
		set5( (ans & F_5) != 0 );
		setZ( (ans) == 0 );
		setPV( parity[ ans ] );
		setH( False );
		setN( False );
		setC( c );

		return(ans);


# Shift Left and Set - alters all flags (CHECKED) 
def	sls( ans ):
		c = bool((ans & 0x80) != 0)
		ans = ((ans << 1) | 0x01) & 0xff;

		setS( (ans & F_S) != 0 );
		set3( (ans & F_3) != 0 );
		set5( (ans & F_5) != 0 );
		setZ( (ans) == 0 );
		setPV( parity[ ans ] );
		setH( False );
		setN( False );
		setC( c );

		return(ans);


# Shift Right Arithmetically - alters all flags (CHECKED) 
def	sra( ans ):
		c = bool((ans & 0x01) != 0)
		ans = (ans >> 1) | (ans & 0x80);

		setS( (ans & F_S) != 0 );
		set3( (ans & F_3) != 0 );
		set5( (ans & F_5) != 0 );
		setZ( (ans) == 0 );
		setPV( parity[ ans ] );
		setH( False );
		setN( False );
		setC( c );

		return(ans);


# Shift Right Logically - alters all flags (CHECKED) 
def srl( ans ):
		c = bool((ans & 0x01) != 0)
		ans = ans >> 1;

		setS( (ans & F_S) != 0 );
		set3( (ans & F_3) != 0 );
		set5( (ans & F_5) != 0 );
		setZ( (ans) == 0 );
		setPV( parity[ ans ] );
		setH( False );
		setN( False );
		setC( c );

		return(ans);


# Decrement - alters all but C flag (CHECKED) 
def dec8( ans ):
		global fS, f3, f5, fN, fZ, fC, fH, fPV
		pv = (ans == 0x80)
		h  = ((ans & 0x0f) - 1) & F_H
		ans = (ans - 1) & 0xff

		fS= (ans & F_S)
		f3= (ans & F_3)
		f5= (ans & F_5)
		fZ= ((ans) == 0 )
		fPV= pv
		fH= h 
		fN= True

		return(ans);


# Increment - alters all but C flag (CHECKED) 
def inc8( ans ):
		global fS, f3, f5, fN, fZ, fC, fH, fPV
		pv = (ans == 0x7f)
		h  = ((ans & 0x0f) + 1) & F_H
		ans = (ans + 1) & 0xff;

		fS=(ans & F_S)
		f3=(ans & F_3)
		f5=(ans & F_5)
		fZ=( (ans) == 0 )
		fPV= pv
		fH= h
		fN= False

		return(ans);


# Add with carry - (NOT CHECKED) 
def adc16( a, b ):
		global fS, f3, f5, fN, fZ, fC, fH, fPV
		c    = iif(fC , 1 , 0)
		lans = a + b + c;
		ans  = lans & 0xffff;

		fS=(ans & (F_S<<8))
		f3=(ans & (F_3<<8))
		f5=(ans & (F_5<<8))
		fZ=( (ans) == 0 )
		fC= (lans & 0x10000)
		fPV= ((a ^ ~b) & (a ^ ans) & 0x8000)
		fH= (((a & 0x0fff) + (b & 0x0fff) + c) & 0x1000)
		fN= False

		return(ans);


# Add - (NOT CHECKED) 
def add16( a, b ):
		lans = a + b;
		ans  = lans & 0xffff;

		set3( (ans & (F_3<<8)) != 0 );
		set5( (ans & (F_5<<8)) != 0 );
		setC (lans & 0x10000)
		setH (((a & 0x0fff) + (b & 0x0fff)) & 0x1000)
		setN( False );

		return(ans);


# Add with carry - (NOT CHECKED) 
def sbc16( a, b ):
		c    = iif(fC , 1 , 0)
		lans = a - b - c;
		ans  = lans & 0xffff;

		setS( (ans & (F_S<<8)) != 0 );
		set3( (ans & (F_3<<8)) != 0 );
		set5( (ans & (F_5<<8)) != 0 );
		setZ( (ans) == 0 );
		setC (lans & 0x10000)
		setPV ((a ^ b) & (a ^ ans) & 0x8000)
		setH (((a & 0x0fff) - (b & 0x0fff) - c) & 0x1000)
		setN( True );

		return(ans);


# EXX 
def exx():
		global _HL_, _DE_, _BC_
		t = _HL;
		HL( _HL_ );
		_HL_ = t;

		t = DEget();
		DE( _DE_ );
		_DE_ = t;

		t = BCget();
		BC( _BC_ );
		_BC_ = t;    


# EX AF,AF' 
def ex_af_af():
		global _AF_
		t = AFget(); AF( _AF_ ); _AF_ = t;


# Quick Increment : no flags 
def inc16( a ): return (a + 1) & 0xffff
def qinc8( a ): return (a + 1) & 0xff

# Quick Decrement : no flags 
def dec16( a ): return (a - 1) & 0xffff
def qdec8( a ): return (a - 1) & 0xff

# Bit toggling 
def res( bit, val ): return val & ~bit
def set( bit, val ): return val |  bit

#ALL CHECKED - VM 2005
