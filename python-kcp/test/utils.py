import time
import random
import sys

g_ScriptStartTime = time.time()

g_RndSeed = int(time.time())

def msleep(ms):
    time.sleep(ms * 0.001)

def initrndseed():
    global g_RndSeed
    random.seed(g_RndSeed)

def rndvalue(_min, _max):
    return _min + random.randint(0, _max - _min)

def getms():
    global g_ScriptStartTime
    return int((time.time()-g_ScriptStartTime)*1000)

def uint322netbytes(i):
    return chr(i>>24&255) + chr(i>>16&255) + chr(i>>8&255) + chr(i&255)

def netbytes2uint32(s):
	if sys.version_info.major == 3 and isinstance(s, bytes):
		return s[0]<<24 | s[1]<<16 | s[2]<<8 | s[3]
	else:
		return ord(s[0])<<24 | ord(s[1])<<16 | ord(s[2])<<8 | ord(s[3])
