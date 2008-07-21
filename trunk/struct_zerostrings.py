# how to parse zero terminated strings with struct
# made by thomas {AT} thomasfischer {DOT} biz
import struct

def packExt(fmt, *args):
	#workaround :)
	if type(args[0]) == list:
		args = args[0]
	
	#pack now
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
				if type(args[argcounter]) != type(''):
					print "no string at string argument!"
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
	#todo clac size of zero string correctly!
	size = calcSizeExt(fmt, buffer[offset:])
	buf = buffer[offset:offset+size]
	return unpackExt(fmt, buf)
	
def calcSizeExt(fmt, string=""):
	default_string_size = 255
	if fmt.find("z") < 0:
		# normal unpack
		return struct.calcsize(fmt)
	else:
		# contains zero terminated string
		size_all = 0
		result = []
		format_buffer = ""
		for i in range(0, len(fmt)):
			if fmt[i] == 'z':
				#process buffer
				if len(format_buffer) > 0:
					size_all += struct.calcsize(format_buffer)
					format_buffer = ""
				
				if string != '':
					# now the z part
					str = ""
					strsize = -1
					for j in range(0, 4096):
						if string[size_all+j] == '\0':
							strsize=j
							break
						else:
							str+=string[size_all+j]
					size_all += strsize + 1 # 1 = \0
				else:
					size_all += default_string_size
			else:
				# cache all chars for later processing
				format_buffer += fmt[i]
			
		#process last buffer
		size_all += struct.calcsize(format_buffer)
		return size_all

def unpackExt(fmt, string):
	if fmt.find("z") < 0:
		# normal unpack
		return struct.unpack(fmt, string), calcSizeExt(fmt)
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
					size = calcSizeExt(format_buffer)
					result_this = unpackFromExt(format_buffer, string, offset)
					offset += size
					#print " '%s, %s' => "%(format_buffer, size), result_this
					result += result_this
					format_buffer = ""
				
				# now the z part
				str = ""
				strsize = -1
				for j in range(0, 4096):
					if offset+j >= len(string):
						strsize=j
						break
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
		size = calcSizeExt(format_buffer, string[offset:])
		result_this = unpackFromExt(format_buffer, string, offset)
		#print " '%s, %s' => "%(format_buffer, size), result_this
		#print " '%s' => "%format_buffer, result_this
		result += result_this
		format_buffer = ""
		return result, offset + size

if __name__ == '__main__':
	print "some basic tests: "
	print unpackExt("z", packExt("z", "test1"))
	print unpackExt("z", packExt("z", "test1 test2"))
	print unpackExt("z", packExt("z", "test1\0test2"))
	print unpackExt("ibzi", packExt("ibzi", 200, 3, "test1\0test2", 34))
	print unpackExt("ibzizf", packExt("ibzizf", 200, 3, "test1\0test2", 34, "test string", 0.234))
	
	printOK=False
	# add your test cases below :)
	testcases = [
		{
			'name'  :'test1',
			'format':'BIIIIzBIB',
			'args'  :[2, 1234253, 2435436, 76543, 9876523, 'helloooo?', 128, 11111, 127],
		},
		{
			'name'  :'test zero inside string',
			'format':'IzI',
			'args'  :[1234253, 'testsentence\n\0\ntest3', 111117],
		},
		{
			'name'  :'test zero inside string',
			'format':'hH',
			'args'  :[-123, -123],
		},
	]
	
	for test in testcases:
		print '\n','='*40, test['name'], '='*40
		try:
			format = test['format']
			args = test['args']
			string = packExt(format, args)
			#print "BUFFERs: \n"
			offset=0
			counter=0
			allOK2=True
			for c in format:
				allOK=True
				try:
					size = calcSizeExt(c, string[offset:])
					
					res1 = unpackFromExt(c, string[offset:offset+size])
					msgs = []
					status = "ERROR"
					if res1[0][0] == args[counter]:
						status="OK"
					else:
						allOK=False
					if (status == "OK" and printOK) or status != "OK":
						msgs.append(" - %6s - unpack with unpackFromExt: %s"%(status, res1.__str__()))
					
					res2 = unpackFromExt(c, string, offset)
					status = "ERROR"
					if res2[0][0] == args[counter]:
						status="OK"
					else:
						allOK=False
					if (status == "OK" and printOK) or status != "OK":
						msgs.append(" - %6s - unpack with unpackFromExt(with offset): %s"%(status, res2.__str__()))
					
					res3=unpackExt(c, string[offset:offset+size])
					status = "ERROR"
					if res3[0][0] == args[counter]:
						status="OK"
					else:
						allOK=False
					if (status == "OK" and printOK) or status != "OK":
						msgs.append(" - %6s - unpack with unpackExt: %s"%(status, res3.__str__()))
				except Exception, e:
					print "exception: ",e
					allOK=False
					
				if (allOK and printOK) or not allOK:
					print " %c (%d,%d): %s, " % (c, offset, size, string[offset:offset+size].encode("hex")), "org: ", args[counter]
					for msg in msgs:
						print msg
				counter += 1
				offset += size
			
			if not allOK:
				allOK2=False
		

		except Exception, e:
			print "exception: ",e
			allOK2=False
		
		if allOK2:
			print " no errors found!"
		else:
			print " ERRORS found!"

		
