import sys
import Z80

def loadZ80(name):
		compressed = False;

		f = open( name, 'rb')
		header_str = f.read(30)
		header = [ord(b) for b in header_str]

		Z80.A( header[0] );
		Z80.F( header[1] );
     
		Z80.C( header[2] );
		Z80.B( header[3] );
		Z80.L( header[4] );
		Z80.H( header[5] );

		Z80.PC( header[6] | (header[7]<<8) );
		Z80.SP( header[8] | (header[9]<<8) );

		Z80.I( header[10] );
		Z80.R( header[11] );

		tbyte = header[12];
		if ( tbyte == 255 ):
			tbyte = 1

		Z80.outb( 254, ((tbyte >> 1) & 0x07), 0 ) #border

		if (tbyte & 0x01) != 0:
			Z80.R( Z80.Rget() | 0x80 )

		compressed = ((tbyte & 0x20) != 0);
     
		Z80.E( header[13] );
		Z80.D( header[14] );

		Z80.ex_af_af();
		Z80.exx();

		Z80.C( header[15] );
		Z80.B( header[16] );
		Z80.E( header[17] );
		Z80.D( header[18] );
		Z80.L( header[19] );
		Z80.H( header[20] );

		Z80.A( header[21] );
		Z80.F( header[22] );

		Z80.ex_af_af();
		Z80.exx();

		Z80.IY( header[23] | (header[24]<<8) );
		Z80.IX( header[25] | (header[26]<<8) );

		Z80.IFF1( header[27] != 0 );
		Z80.IFF2( header[28] != 0 );

		switch = header[29] & 0x03
		if switch == 0:
			Z80.IM( Z80.IM0 )
		elif switch == 1:
			Z80.IM( Z80.IM1 )
		else:
			Z80.IM( Z80.IM2 )

		if Z80.PCget() == 0:
			#print 'unsupported filetype, extended z80'
			#sys.exit()
			pos = 30
			loadZ80_extended( f, pos )
			return

		#Old format Z80 snapshot
		if ( compressed ):
			print 'reading compressed'
			f = open( name, 'rb')
			f.seek(30)
			bytes = [ord(b) for b in  f.read()]
			size = len(bytes)
			print 'size = len(bytes):', size
			i = 0
			addr = 16384
			while (addr < 65536) and (i < size) :
				tbyte = bytes[i]
				i += 1
				if tbyte != 0xed:
					Z80.mem[addr] = tbyte
					addr += 1
				else:
					tbyte = bytes[i]
					i+=1
					if tbyte != 0xed:
						Z80.mem[addr] = 0xed
						i -= 1
						addr += 1
					else:
						count = bytes[i]
						i += 1
						tbyte = bytes[i]
						i += 1
						while count != 0:
							count -= 1
							Z80.mem[addr] = tbyte
							addr += 1
			print 'loaded'

			t="""
			int data[] = new int[ bytesLeft ];
			addr   = 16384;

			int size = readBytes( is, data, 0, bytesLeft );
			int i    = 0;

			while ( (addr < 65536) && (i < size) ) {
				tbyte = data[i++];
				if ( tbyte != 0xed ) {
					pokeb( addr, tbyte );
					addr++;
				}
				else {
					tbyte = data[i++];
					if ( tbyte != 0xed ) {
						pokeb( addr, 0xed );
						i--;
						addr++;
					}
					else {
						int        count;
						count = data[i++];
						tbyte = data[i++];
						while ( (count--) != 0 ) {
							pokeb( addr, tbyte );
							addr++;
						}
					}
				}
			}
		}"""
		else:
			print 'reading uncompressed',
			f = open( name, 'rb')
			f.seek(30)
			bytes =[ord(b) for b in f.read(49152)]
			print 'len(Z80.mem):', len(Z80.mem)
			Z80.mem[16384:len(bytes)+1] = bytes[:]
			print 'len(bytes):%s len(Z80.mem):%s' % (len(bytes), len(Z80.mem))


def	loadZ80_extended(f, pos):
		f.seek(pos)
		header = [ord(b) for b in f.read(2)]
		pos += 2

		type = header[0] | (header[1] << 8)

		switch = type
		if switch == 23: #V2.01
			loadZ80_v201(f, pos)
		elif switch == 54: #V3.00
			loadZ80_v300(f, pos)
		elif switch == 58: #V3.01
			loadZ80_v301(f, pos)
		else:
			print "Z80 (extended): unsupported type ", type
			sys.exit()


def loadZ80_v201(f, pos):
		f.seek(pos)
		header = [ord(b) for b in f.read(23)]
		pos += 23
		Z80.PC( header[0] | (header[1]<<8) )
		# 0 - 48K
		# 1 - 48K + IF1
		# 2 - SamRam
		# 3 - 128K
		# 4 - 128K + IF1
		type = header[2]
		if  type > 1 :
			print "Z80 (v201): unsupported type ", type
			sys.exit()
		f.seek(pos)
		data = [ord(b) for b in f.read()]
		offset = 0
		j = 0
		while j < 3:
			offset = loadZ80_page( data, offset )
			j += 1


def loadZ80_v300(f, pos):
		f.seek(pos)
		header = [ord(b) for b in f.read(54)]
		pos += 54
		Z80.PC( header[0] | (header[1]<<8) )
		# 0 - 48K
		# 1 - 48K + IF1
		# 2 - 48K + MGT
		# 3 - SamRam
		# 4 - 128K
		# 5 - 128K + IF1
		# 6 - 128K + MGT
		type = header[2]
		if type > 6 :
			print "Z80 (v300): unsupported type ", type
			sys.exit()
		f.seek(pos)
		data = [ord(b) for b in f.read()]
		offset = 0
		j = 0
		while j < 3:
			offset = loadZ80_page( data, offset )
			j += 1


def loadZ80_v301(f, pos):
		f.seek(pos)
		header = [ord(b) for b in f.read(54)]
		pos += 54
		Z80.PC( header[0] | (header[1]<<8) )
		# 0 - 48K
		# 1 - 48K + IF1
		# 2 - 48K + MGT
		# 3 - SamRam
		# 4 - 128K
		# 5 - 128K + IF1
		# 6 - 128K + MGT
		# 7 - +3
		type = header[2]
		if type > 7 :
			print "Z80 (v301): unsupported type ", type
			sys.exit()
		f.seek(pos)
		data = [ord(b) for b in f.read()]
		offset = 0
		j = 0
		while j < 3:
			offset = loadZ80_page( data, offset )
			j += 1


def loadZ80_page(data, i):
		blocklen  = data[i]
		i+=1
		blocklen |= (data[i]) << 8
		i+=1
		page = data[i]
		i+=1

		switch = page
		if switch == 4:
			addr = 32768
		elif switch == 5:
			addr = 49152
		elif switch == 8:
			addr = 16384
		else:
			print "Z80 (page): out of range ", page
			sys.exit()

		k = 0
		while k < blocklen:
			tbyte = data[i]
			i+=1
			k+=1
			if tbyte != 0xed:
				Z80.mem[addr] = ~tbyte
				Z80.mem[addr] = tbyte
				addr+=1
			else:
				tbyte = data[i]
				i+=1
				k+=1
				if tbyte != 0xed:
					#TODO: check
					Z80.mem[addr] = 0
					Z80.mem[addr] = 0xed
					addr+=1
					i-=1
					k-=1
				else:
					count = data[i]
					i+=1
					k+=1
					tbyte = data[i]
					i+=1
					k+=1
					while ( count > 0 ):
						count -= 1
						Z80.mem[addr] = ~tbyte
						Z80.mem[addr] = tbyte
						addr+=1

		if ((addr & 16383) != 0):
			print "Z80 (page): overrun"
			sys.exit()
		return i

a="""
	private int readBytes( InputStream is, int a[], int off, int n ) throws Exception {
		try {
			BufferedInputStream bis = new BufferedInputStream( is, n );

			byte buff[] = new byte[ n ];
			int toRead = n;
			while ( toRead > 0 ) {
				int	nRead = bis.read( buff, n-toRead, toRead );
				toRead -= nRead;
				updateProgress( nRead );
			}

			for ( int i = 0; i < n; i++ ) {
				a[ i+off ] = (buff[i]+256)&0xff;
			}

			return n;
		}
		catch ( Exception e ) {
			System.err.println( e );
			e.printStackTrace();
			stopProgress();
			throw e;
		}
	}
}
"""


#loadZ80('JSWAPRIL.Z80', Z80.mem)

