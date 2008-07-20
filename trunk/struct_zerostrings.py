# how to parse zero terminated strings with struct
# made by thomas {AT} thomasfischer {DOT} biz
import struct

def packExt(fmt, *args):
	if fmt.find("z") < 0:
		# normal pack
		return struct.pack(fmt, *args)
	else:
		# should contain zero terminated string
		argcounter = 0
		format_buffer = ""
		result=""
		for i in range(0, len(fmt)):
			if fmt[i] not in ['x','c','b','B','h','H','i','I','l','L','q','Q','f','d','s','p','P','z']:
				format_buffer += fmt[i]
				continue
				
			if fmt[i] == 'z':
				zeropos = args[argcounter].find('\0')
				arg = args[argcounter]
				if zeropos < 0:
					# add after end
					nfmt = '%ds'%(len(args[argcounter])+1)
					arg += '\0'
				else:
					nfmt = '%ds'%(zeropos+1)
				
				result += struct.pack(nfmt, arg)
				argcounter += 1
			else:
				#control character!
				format_buffer += fmt[i]
				#print format_buffer, "->", args[argcounter]
				result += struct.pack(format_buffer, args[argcounter])
				argcounter += 1
			format_buffer=""
		return result

# like unpack_from just with extension, this also enables you to use something unpack_from equivalent in python 2.4
def unpackFromExt(fmt, buffer, offset=0):
	size = struct.calcsize(fmt)
	buf = buffer[offset:offset+size]
	return unpackExt(fmt, buf)
	
def unpackExt(fmt, string):
	if fmt.find("z") < 0:
		# normal unpack
		return struct.unpack(fmt, string)
	else:
		# contains zero terminated string
		offset = 0
		result = []
		format_buffer = ""
		for i in range(0, len(fmt)):
			if fmt[i] == 'z':
				#process buffer
				size = 0
				if len(format_buffer) > 0:
					size = struct.calcsize(format_buffer)
					result_this = unpackFromExt(format_buffer, string, offset)
					offset += size
					#print " '%s, %s' => "%(format_buffer, size), result_this
					result += result_this
					format_buffer = ""
				
				# now the z part
				str = ""
				strsize = -1
				for j in range(0, 4096):
					if string[offset+j] == '\0':
						strsize=j
						break
					else:
						str+=string[offset+j]
					
				result += [str]
				offset += strsize + 1 # 1 = \0
			else:
				# cache all chars for later processing
				format_buffer += fmt[i]
			
		#process last buffer
		size = struct.calcsize(format_buffer)
		result_this = unpackFromExt(format_buffer, string, offset)
		#print " '%s' => "%format_buffer, result_this
		result += result_this
		format_buffer = ""
		return result, offset + size

if __name__ == '__main__':
	print unpackExt("z", packExt("z", "test1"))
	print unpackExt("z", packExt("z", "test1 test2"))
	print unpackExt("z", packExt("z", "test1\0test2"))
	print unpackExt("ibzi", packExt("ibzi", 200, 3, "test1\0test2", 34))
	print unpackExt("ibzizf", packExt("ibzizf", 200, 3, "test1\0test2", 34, "test string", 0.234))
