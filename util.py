#!/usr/bin/python3
# coding: utf8

import struct
import datetime
import sys
import string
from enum import IntEnum, unique

XXD_SET = string.ascii_letters + string.digits + string.punctuation

crc_table = [
        0x0000, 0x1189, 0x2312, 0x329b, 0x4624, 0x57ad, 0x6536, 0x74bf,
        0x8c48, 0x9dc1, 0xaf5a, 0xbed3, 0xca6c, 0xdbe5, 0xe97e, 0xf8f7,
        0x1081, 0x0108, 0x3393, 0x221a, 0x56a5, 0x472c, 0x75b7, 0x643e,
        0x9cc9, 0x8d40, 0xbfdb, 0xae52, 0xdaed, 0xcb64, 0xf9ff, 0xe876,
        0x2102, 0x308b, 0x0210, 0x1399, 0x6726, 0x76af, 0x4434, 0x55bd,
        0xad4a, 0xbcc3, 0x8e58, 0x9fd1, 0xeb6e, 0xfae7, 0xc87c, 0xd9f5,
        0x3183, 0x200a, 0x1291, 0x0318, 0x77a7, 0x662e, 0x54b5, 0x453c,
        0xbdcb, 0xac42, 0x9ed9, 0x8f50, 0xfbef, 0xea66, 0xd8fd, 0xc974,
        0x4204, 0x538d, 0x6116, 0x709f, 0x0420, 0x15a9, 0x2732, 0x36bb,
        0xce4c, 0xdfc5, 0xed5e, 0xfcd7, 0x8868, 0x99e1, 0xab7a, 0xbaf3,
        0x5285, 0x430c, 0x7197, 0x601e, 0x14a1, 0x0528, 0x37b3, 0x263a,
        0xdecd, 0xcf44, 0xfddf, 0xec56, 0x98e9, 0x8960, 0xbbfb, 0xaa72,
        0x6306, 0x728f, 0x4014, 0x519d, 0x2522, 0x34ab, 0x0630, 0x17b9,
        0xef4e, 0xfec7, 0xcc5c, 0xddd5, 0xa96a, 0xb8e3, 0x8a78, 0x9bf1,
        0x7387, 0x620e, 0x5095, 0x411c, 0x35a3, 0x242a, 0x16b1, 0x0738,
        0xffcf, 0xee46, 0xdcdd, 0xcd54, 0xb9eb, 0xa862, 0x9af9, 0x8b70,
        0x8408, 0x9581, 0xa71a, 0xb693, 0xc22c, 0xd3a5, 0xe13e, 0xf0b7,
        0x0840, 0x19c9, 0x2b52, 0x3adb, 0x4e64, 0x5fed, 0x6d76, 0x7cff,
        0x9489, 0x8500, 0xb79b, 0xa612, 0xd2ad, 0xc324, 0xf1bf, 0xe036,
        0x18c1, 0x0948, 0x3bd3, 0x2a5a, 0x5ee5, 0x4f6c, 0x7df7, 0x6c7e,
        0xa50a, 0xb483, 0x8618, 0x9791, 0xe32e, 0xf2a7, 0xc03c, 0xd1b5,
        0x2942, 0x38cb, 0x0a50, 0x1bd9, 0x6f66, 0x7eef, 0x4c74, 0x5dfd,
        0xb58b, 0xa402, 0x9699, 0x8710, 0xf3af, 0xe226, 0xd0bd, 0xc134,
        0x39c3, 0x284a, 0x1ad1, 0x0b58, 0x7fe7, 0x6e6e, 0x5cf5, 0x4d7c,
        0xc60c, 0xd785, 0xe51e, 0xf497, 0x8028, 0x91a1, 0xa33a, 0xb2b3,
        0x4a44, 0x5bcd, 0x6956, 0x78df, 0x0c60, 0x1de9, 0x2f72, 0x3efb,
        0xd68d, 0xc704, 0xf59f, 0xe416, 0x90a9, 0x8120, 0xb3bb, 0xa232,
        0x5ac5, 0x4b4c, 0x79d7, 0x685e, 0x1ce1, 0x0d68, 0x3ff3, 0x2e7a,
        0xe70e, 0xf687, 0xc41c, 0xd595, 0xa12a, 0xb0a3, 0x8238, 0x93b1,
        0x6b46, 0x7acf, 0x4854, 0x59dd, 0x2d62, 0x3ceb, 0x0e70, 0x1ff9,
        0xf78f, 0xe606, 0xd49d, 0xc514, 0xb1ab, 0xa022, 0x92b9, 0x8330,
        0x7bc7, 0x6a4e, 0x58d5, 0x495c, 0x3de3, 0x2c6a, 0x1ef1, 0x0f78
        ]

def dm_crc16(arr):
    ret = 0xffff
    for b in arr:
        ret = (ret >> 8) ^ crc_table[(ret ^ b) & 0xff]
    return ret ^ 0xffff

def wrap(arr):
    t = arr.replace(b'\x7d', b'\x7d\x5d')
    t = t.replace(b'\x7e', b'\x7d\x5e')
    return t

def unwrap(arr):
    t = arr.replace(b'\x7d\x5e', b'\x7e')
    t = t.replace(b'\x7d\x5d', b'\x7d')
    return t

def generate_packet(arr):
    crc = struct.pack('<H', dm_crc16(arr))
    arr += crc
    arr = wrap(arr)
    arr += b'\x7e'
    return arr

emr_1 = bytes.fromhex('''
7D 04 00 00 65 00 00 00 00 00 00 00 00 00 00 00 
00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 
00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 
00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 
00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 
00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 
00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 
00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 
00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 
00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 
00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 
00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 
00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 
00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 
00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 
00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 
00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 
00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 
00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 
00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 
00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 
00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 
00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 
00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 
00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 
00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00
'''.strip().replace('\n', '').replace(' ', ''))

emr_2 = bytes.fromhex('''
7D 04 F4 01 FA 01 00 00 00 00 00 00 00 00 00 00 
00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 
00 00 00 00
'''.strip().replace('\n', '').replace(' ', ''))

emr_3 = bytes.fromhex('''
7D 04 E8 03 EF 03 00 00 00 00 00 00 00 00 00 00 
00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 
00 00 00 00 00 00 00 00 
'''.strip().replace('\n', '').replace(' ', ''))

emr_4 = bytes.fromhex('''
7D 04 D0 07 D8 07 00 00 00 00 00 00 00 00 00 00 
00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 
00 00 00 00 00 00 00 00 00 00 00 00 
'''.strip().replace('\n', '').replace(' ', ''))

emr_5 = bytes.fromhex('''
7D 04 B8 0B C6 0B 00 00 00 00 00 00 00 00 00 00 
00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 
00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 
00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 
00 00 00 00 
'''.strip().replace('\n', '').replace(' ', ''))

emr_6 = bytes.fromhex('''
7D 04 A0 0F AA 0F 00 00 00 00 00 00 00 00 00 00 
00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 
00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 
00 00 00 00 
'''.strip().replace('\n', '').replace(' ', ''))

emr_7 = bytes.fromhex('''
7D 04 94 11 AE 11 00 00 00 00 00 00 00 00 00 00 
00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 
00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 
00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 
00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 
00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 
00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 
00 00 00 00 
'''.strip().replace('\n', '').replace(' ', ''))

emr_8 = bytes.fromhex('''
7D 04 F8 11 06 12 00 00 00 00 00 00 00 00 00 00 
00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 
00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 
00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 
00 00 00 00 
'''.strip().replace('\n', '').replace(' ', ''))

emr_9 = bytes.fromhex('''
7D 04 88 13 A6 13 00 00 00 00 00 00 00 00 00 00 
00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 
00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 
00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 
00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 
00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 
00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 
00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 
00 00 00 00 
'''.strip().replace('\n', '').replace(' ', ''))

emr_10 = bytes.fromhex('''
7D 04 7C 15 8C 15 00 00 00 00 00 00 00 00 00 00 
00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 
00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 
00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 
00 00 00 00 00 00 00 00 00 00 00 00 
'''.strip().replace('\n', '').replace(' ', ''))

emr_11 = bytes.fromhex('''
7D 04 70 17 C0 17 00 00 00 00 00 00 00 00 00 00 
00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 
00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 
00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 
00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 
00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 
00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 
00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 
00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 
00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 
00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 
00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 
00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 
00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 
00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 
00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 
00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 
00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 
00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 
00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 
00 00 00 00 00 00 00 00 00 00 00 00 
'''.strip().replace('\n', '').replace(' ', ''))

emr_12 = bytes.fromhex('''
7D 04 64 19 79 19 00 00 00 00 00 00 00 00 00 00 
00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 
00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 
00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 
00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 
00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 
'''.strip().replace('\n', '').replace(' ', ''))

emr_13 = bytes.fromhex('''
7D 04 58 1B 5B 1B 00 00 00 00 00 00 00 00 00 00 
00 00 00 00 00 00 00 00 
'''.strip().replace('\n', '').replace(' ', ''))

emr_14 = bytes.fromhex('''
7D 04 BC 1B C7 1B 00 00 00 00 00 00 00 00 00 00 
00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 
00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 
00 00 00 00 00 00 00 00 
'''.strip().replace('\n', '').replace(' ', ''))

emr_15 = bytes.fromhex('''
7D 04 20 1C 21 1C 00 00 00 00 00 00 00 00 00 00 
'''.strip().replace('\n', '').replace(' ', ''))

emr_16 = bytes.fromhex('''
7D 04 40 1F 40 1F 00 00 00 00 00 00 
'''.strip().replace('\n', '').replace(' ', ''))

emr_17 = bytes.fromhex('''
7D 04 34 21 4C 21 00 00 00 00 00 00 00 00 00 00 
00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 
00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 
00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 
00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 
00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 
00 00 00 00 00 00 00 00 00 00 00 00 
'''.strip().replace('\n', '').replace(' ', ''))

emr_18 = bytes.fromhex('''
7D 04 28 23 30 23 00 00 00 00 00 00 00 00 00 00 
00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 
00 00 00 00 00 00 00 00 00 00 00 00 
'''.strip().replace('\n', '').replace(' ', ''))

emr_19 = bytes.fromhex('''
7D 04 1C 25 25 25 00 00 00 00 00 00 00 00 00 00 
00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 
00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 
'''.strip().replace('\n', '').replace(' ', ''))

emr_20 = bytes.fromhex('''
7D 04 D8 27 E2 27 00 00 00 00 00 00 00 00 00 00 
00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 
00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 
00 00 00 00 
'''.strip().replace('\n', '').replace(' ', ''))

emr_21 = bytes.fromhex('''
7D 04 0B 28 0F 28 00 00 00 00 00 00 00 00 00 00 
00 00 00 00 00 00 00 00 00 00 00 00 
'''.strip().replace('\n', '').replace(' ', ''))

emr_22 = bytes.fromhex('''
7D 04 3C 28 3C 28 00 00 00 00 00 00 
'''.strip().replace('\n', '').replace(' ', ''))

emr_23 = bytes.fromhex('''
7D 04 6E 28 86 28 00 00 00 00 00 00 00 00 00 00 
00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 
00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 
00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 
00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 
00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 
00 00 00 00 00 00 00 00 00 00 00 00 
'''.strip().replace('\n', '').replace(' ', ''))

emr_config_1 = bytes.fromhex('''
7D 04 00 00 5E 00 00 00 1F 00 00 00 1E 00 00 00 
1F 00 00 00 18 00 00 00 1F 00 00 00 1E 00 00 00 
1E 00 00 00 1C 00 00 00 18 00 00 00 1F 00 00 00 
18 00 00 00 1E 00 00 00 1C 00 00 00 1C 00 00 00 
1F 00 00 00 1F 00 00 00 18 00 00 00 1F 00 00 00 
1E 00 00 00 1E 00 00 00 1E 00 00 00 1F 00 00 00 
1E 00 00 00 1F 00 00 00 1F 00 00 00 1E 00 00 00 
1E 00 00 00 1E 00 00 00 1E 00 00 00 1E 00 00 00 
9E FF 03 00 FE FF 03 00 1E 00 00 00 1E 00 00 00 
1C 00 00 00 1C 00 00 00 1C 00 00 00 1C 00 00 00 
1E 00 00 00 1E 00 00 00 FE 01 00 00 1F 00 00 00 
1F 00 00 00 1C 00 00 00 1C 00 00 00 1C 00 00 00 
1E 00 00 00 FE FF FF 03 1E 00 00 00 FE 07 00 00 
1F 00 00 00 1F 00 00 00 1E 00 00 00 1F 00 00 00 
1F 00 00 00 1F 00 00 00 1C 00 00 00 1F 00 00 00 
1F 00 00 00 FF 01 00 00 7F 00 00 00 1E 00 00 00 
1E 00 00 00 1F 00 00 00 FE FF 1F 00 1F 00 00 00 
1E 00 00 00 1F 00 00 00 1F 00 00 00 1F 00 00 00 
1C 00 00 00 1C 00 00 00 1F 00 00 00 1F 00 00 00 
1F 00 00 00 1F 00 00 00 1F 00 00 00 1C 00 00 00 
1C 00 00 00 1F 00 00 00 1F 00 00 00 1F 00 00 00 
1F 00 00 00 1F 00 00 00 1F 00 00 00 1F 00 00 00 
1E 00 00 00 1F 00 00 00 1F 00 00 00 1E 00 00 00 
1F 00 00 00 1F 00 00 00 1F 00 00 00 1C 00 00 00 
1F 00 00 00
'''.strip().replace('\n', '').replace(' ', ''))

emr_config_2 = bytes.fromhex('''
7D 04 F4 01 FA 01 00 00 1E 00 00 00 1C 00 00 00 
1C 00 00 00 1F 00 00 00 1C 00 00 00 1C 00 00 00 
1C 00 00 00 
'''.strip().replace('\n', '').replace(' ', ''))

emr_config_3 = bytes.fromhex('''
7D 04 E8 03 EF 03 00 00 1E 00 00 00 1E 00 00 00 
1E 00 00 00 1E 00 00 00 1E 00 00 00 3E 00 00 00 
1E 00 00 00 FE 07 7F 0F
'''.strip().replace('\n', '').replace(' ', ''))

emr_config_4 = bytes.fromhex('''
7D 04 D0 07 D8 07 00 00 1E 00 00 00 1E 00 00 00 
1E 00 00 00 1E 00 00 00 1E 00 00 00 E0 07 00 00 
1E 00 00 00 1E 00 00 00 1E 00 00 00 
'''.strip().replace('\n', '').replace(' ', ''))

emr_config_5 = bytes.fromhex('''
7D 04 B8 0B C6 0B 00 00 1C 00 00 00 FC FF 71 00 
7C 00 00 00 1C 00 00 00 1C 00 00 00 FC 00 00 00 
1C 00 00 00 1C 00 00 00 1C 00 00 00 1C 00 00 00 
1C 00 00 00 1C 00 00 00 1C 00 00 00 1F 00 00 00 
1F 00 00 00 
'''.strip().replace('\n', '').replace(' ', ''))

emr_config_6 = bytes.fromhex('''
7D 04 A0 0F AA 0F 00 00 1C 00 00 00 1E 00 00 00 
1C 00 00 00 1E 00 00 00 1E 00 00 00 1E 00 00 00 
1E 00 00 00 1E 00 00 00 1E 00 00 00 FE 03 00 00 
1E 00 00 00 
'''.strip().replace('\n', '').replace(' ', ''))

emr_config_7 = bytes.fromhex('''
7D 04 94 11 AE 11 00 00 1E 00 00 00 1E 00 00 00 
1E 00 00 00 1E 00 00 00 1E 00 00 00 1E 00 00 00 
1E 00 00 00 1F 00 00 00 1F 00 00 00 1F 00 00 00 
1F 00 00 00 1F 00 00 00 1F 00 00 00 1F 00 00 00 
1F 00 00 00 1F 00 00 00 1F 00 00 00 1F 00 00 00 
1F 00 00 00 1F 00 00 00 1F 00 00 00 1F 00 00 00 
1F 00 00 00 1F 00 00 00 1F 00 00 00 1F 00 00 00 
1F 00 00 00 
'''.strip().replace('\n', '').replace(' ', ''))

emr_config_8 = bytes.fromhex('''
7D 04 F8 11 05 12 00 00 1E 00 00 00 1E 00 00 00 
1E 00 00 00 1E 00 00 00 1E 00 00 00 1E 00 00 00 
1E 00 00 00 1E 00 00 00 1E 00 00 00 1E 00 00 00 
1E 00 00 00 1E 00 00 00 1F 00 00 00 1F 00 00 00 
'''.strip().replace('\n', '').replace(' ', ''))

emr_config_9 = bytes.fromhex('''
7D 04 88 13 A5 13 00 00 1E 00 00 00 1E 00 00 00 
1E 00 00 00 1E 00 00 00 1E 00 00 00 1E 00 00 00 
1E 00 00 00 1E 00 00 00 1E 00 00 00 1E 00 00 00 
1E 00 00 00 1E 00 00 00 1E 00 00 00 1E 00 00 00 
1E 00 00 00 1E 00 00 00 1F 00 00 00 1F 00 00 00 
1F 00 00 00 1E 00 00 00 1E 00 00 00 1E 00 00 00 
1E 00 00 00 1E 00 00 00 1E 00 00 00 1E 00 00 00 
1E 00 00 00 1E 00 00 00 1E 00 00 00 1E 00 00 00 
'''.strip().replace('\n', '').replace(' ', ''))

emr_config_10 = bytes.fromhex('''
7D 04 7C 15 8B 15 00 00 3E 00 00 00 3E 00 00 00 
3E 00 00 00 3E 00 00 00 3E 00 00 00 3E 00 00 00 
3E 00 00 00 3E 00 00 00 3E 00 00 00 3E 00 00 00 
3E 00 00 00 3E 00 00 00 3E 00 00 00 3E 00 00 00 
3E 00 00 00 3E 00 00 00 
'''.strip().replace('\n', '').replace(' ', ''))

emr_config_11 = bytes.fromhex('''
7D 04 70 17 BE 17 00 00 1E 00 00 00 18 00 00 00 
1F 00 00 00 FF FF 7F 00 3F 00 00 00 1F 00 00 00 
1F 00 00 00 1F 00 00 00 1F 00 00 00 1F 00 00 00 
1F 00 00 00 1F 00 00 00 1F 00 00 00 3F 00 00 00 
3F 00 00 00 3F 00 00 00 3F 00 00 00 3F 00 00 00 
3F 00 00 00 3F 00 00 00 3F 00 00 00 3F 00 00 00 
3F 00 00 00 3F 00 00 00 3F 00 00 00 3F 00 00 00 
3F 00 00 00 3F 00 00 00 3F 00 00 00 3F 00 00 00 
3F 00 00 00 3F 00 00 00 1F 00 00 00 1E 00 00 00 
1C 00 00 00 1F 00 00 00 1F 00 00 00 1F 00 00 00 
7F 00 00 00 1C 00 00 00 1F 00 00 00 1F 00 00 00 
1F 00 00 00 1F 00 00 00 1F 00 00 00 1F 00 00 00 
1F 00 00 00 1F 00 00 00 1F 00 00 00 1F 00 00 00 
1F 00 00 00 1F 00 00 00 1E 00 00 00 1E 00 00 00 
1E 00 00 00 1E 00 00 00 1E 00 00 00 1E 00 00 00 
1E 00 00 00 1E 00 00 00 1E 00 00 00 1E 00 00 00 
1E 00 00 00 1E 00 00 00 1E 00 00 00 1E 00 00 00 
1E 00 00 00 1E 00 00 00 1E 00 00 00 1E 00 00 00 
1E 00 00 00 1E 00 00 00 1F 00 00 00 1F 00 00 00 
1F 00 00 00 1F 00 00 00 1F 00 00 00 1F 00 00 00 
1F 00 00 00 
'''.strip().replace('\n', '').replace(' ', ''))

emr_config_11_5 = bytes.fromhex('''
7D 04 C0 17 C0 17 00 00 1F 00 00 00 
'''.strip().replace('\n', '').replace(' ', ''))

emr_config_12 = bytes.fromhex('''
7D 04 64 19 79 19 00 00 1F 00 00 00 1F 00 00 00 
1F 00 00 00 1F 00 00 00 1F 00 00 00 1F 00 00 00 
1F 00 00 00 1F 00 00 00 1F 00 00 00 1F 00 00 00 
1F 00 00 00 1F 00 00 00 1F 00 00 00 1F 00 00 00 
1F 00 00 00 1F 00 00 00 1F 00 00 00 1F 00 00 00 
1F 00 00 00 1F 00 00 00 1F 00 00 00 1F 00 00 00 
'''.strip().replace('\n', '').replace(' ', ''))

emr_config_13 = bytes.fromhex('''
7D 04 58 1B 5B 1B 00 00 1E 00 00 00 1E 00 00 00 
1E 00 00 00 1E 00 00 00 
'''.strip().replace('\n', '').replace(' ', ''))

emr_config_14 = bytes.fromhex('''
7D 04 BC 1B C7 1B 00 00 1E 00 00 00 1E 00 00 00 
1E 00 00 00 1E 00 00 00 1E 00 00 00 1E 00 00 00 
1E 00 00 00 1E 00 00 00 1E 00 00 00 1E 00 00 00 
1E 00 00 00 1E 00 00 00 
'''.strip().replace('\n', '').replace(' ', ''))

emr_config_15 = bytes.fromhex('''
7D 04 20 1C 21 1C 00 00 1E 00 00 00 1E 00 00 00 
'''.strip().replace('\n', '').replace(' ', ''))

emr_config_16 = bytes.fromhex('''
7D 04 40 1F 40 1F 00 00 1E 00 00 00 
'''.strip().replace('\n', '').replace(' ', ''))

emr_config_17 = bytes.fromhex('''
7D 04 34 21 4B 21 00 00 1F 00 00 00 1F 00 00 00 
1F 00 00 00 1F 00 00 00 1F 00 00 00 1F 00 00 00 
1F 00 00 00 1F 00 00 00 1F 00 00 00 1F 00 00 00 
1F 00 00 00 1F 00 00 00 1F 00 00 00 1F 00 00 00 
1F 00 00 00 1F 00 00 00 1F 00 00 00 1F 00 00 00 
1F 00 00 00 1F 00 00 00 1F 00 00 00 1F 00 00 00 
1F 00 00 00 1F 00 00 00 
'''.strip().replace('\n', '').replace(' ', ''))

emr_config_18 = bytes.fromhex('''
7D 04 28 23 30 23 00 00 1E 00 00 00 1E 00 00 00 
1E 00 00 00 DE 03 00 00 FE FF 03 00 1E 00 00 00 
FE FF 7F 00 1E 00 00 00 1E 00 00 00 
'''.strip().replace('\n', '').replace(' ', ''))

emr_config_19 = bytes.fromhex('''
7D 04 1C 25 25 25 00 00 1F 00 00 00 1F FF 1F 00 
7F 00 00 00 3F 00 00 00 7F 00 00 00 1F 00 00 00 
FF 03 00 00 1F 00 00 00 1F 00 00 00 FF FF 71 00 
'''.strip().replace('\n', '').replace(' ', ''))

emr_config_20 = bytes.fromhex('''
7D 04 D8 27 E2 27 00 00 1F 00 00 00 1F 00 00 00 
1F 00 00 00 1F 00 00 00 1F 00 00 00 1F 00 00 00 
1F 00 00 00 1F 00 00 00 1F 00 00 00 1F 00 00 00 
1F 00 00 00 
'''.strip().replace('\n', '').replace(' ', ''))

emr_config_21 = bytes.fromhex('''
7D 04 0B 28 0F 28 00 00 FF 1F 00 00 1F 00 00 00 
1F 00 00 00 1F 00 00 00 1F 00 00 00 
'''.strip().replace('\n', '').replace(' ', ''))

emr_config_22 = bytes.fromhex('''
7D 04 3C 28 3C 28 00 00 1C 00 00 00 
'''.strip().replace('\n', '').replace(' ', ''))

emr_config_23 = bytes.fromhex('''
7D 04 6E 28 86 28 00 00 1F 00 00 00 1F 00 00 00 
1F 00 00 00 1F 00 00 00 1F 00 00 00 1F 00 00 00 
1F 00 00 00 1F 00 00 00 1F 00 00 00 1F 00 00 00 
1F 00 00 00 1F 00 00 00 1F 00 00 00 1F 00 00 00 
1F 00 00 00 1F 00 00 00 1F 00 00 00 1F 00 00 00 
1F 00 00 00 1F 00 00 00 1F 00 00 00 1F 00 00 00 
1F 00 00 00 1F 00 00 00 1F 00 00 00 
'''.strip().replace('\n', '').replace(' ', ''))

log_enable_1x_all = bytes.fromhex('''
73 00 00 00 03 00 00 00 01 00 00 00 5B 07 00 00 
FF FF FF F6 61 FF FF FF 7F FF 3F E0 FF FF DF FF 
FD FF FF FF FF FF FF F7 FF FF CF FF 1F 00 FC FF 
FF FF 3F 00 38 00 38 00 38 00 F0 C1 FF FF FF FF 
FF FF FF FF FF FF FF FF FF 01 00 00 FE FF FF FF 
FD FF 7F FF FF FF FF 3F 02 00 FF FF FF FF FF FF 
7F FE FF FF FF FF FF FF 02 00 00 00 F8 03 02 00 
00 00 00 00 00 F8 FF FF FF FF FF FF FF FF FF FF 
FF FF FF FF FF BF FD FF FF FF FF FF FF FF FF FF 
FF FF FF FF FF FF FF FF FF FF FF FF FF BF FF FF 
FF F7 F3 FF C7 3F FF FF FF FF FF 7F FF BF FF FF 
FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF 
FF FF FF FF FF FF FF FF FF 3F 0C 00 00 00 00 00 
00 00 00 0C 00 00 F8 FF FF 03 1F 00 00 00 00 00 
00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 
00 00 00 00 00 00 00 00 00 03 FF 03 
'''.strip().replace('\n', '').replace(' ', ''))

log_enable_wcdma_all = bytes.fromhex('''
73 00 00 00 03 00 00 00 04 00 00 00 18 09 00 00 
7F 01 FB FF F8 00 22 00 00 00 00 00 00 00 00 00 
00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 
FF 7F FF FF FF CF 3C 9F FE FF 6F 03 6F 0B FF F7 
FF 7F F2 3F 00 D4 3D 00 00 00 00 00 00 00 00 00 
FF FF FF FF FF 57 63 CF 00 00 00 00 00 00 00 00 
00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 
FE DF 1F 00 7E 00 4E 00 FF 03 00 0C 00 00 00 00 
00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 
00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 
00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 
00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 
00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 
00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 
00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 
00 00 00 00 04 00 00 00 00 00 00 00 00 00 5B 01 
00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 
00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 
00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 
FF FF FF 
'''.strip().replace('\n', '').replace(' ', ''))

log_enable_gsm_all = bytes.fromhex('''
73 00 00 00 03 00 00 00 05 00 00 00 28 04 00 00 
03 00 00 00 00 00 00 00 00 00 00 00 70 9E FF 3F 
FC 71 53 00 03 00 00 00 00 07 00 00 00 00 00 00 
00 00 00 00 00 F0 FF D7 00 00 00 00 00 00 00 00 
00 00 03 00 00 00 00 00 00 00 00 00 00 00 F0 FF 
E7 FF FF F7 C3 7F FF 84 E0 E3 FF FF 0D 00 0F 00 
00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 
00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 
10 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 
01 01 03 00 00 
'''.strip().replace('\n', '').replace(' ', ''))

log_enable_umts_all = bytes.fromhex('''
73 00 00 00 03 00 00 00 07 00 00 00 5E 0B 00 00 
FE 7F FF FF 00 00 00 00 00 00 00 00 00 00 00 00 
00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 
00 00 00 00 00 00 FF FF 1F 00 FF 03 00 00 00 00 
00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 
FF 37 06 EA 07 00 07 00 00 00 00 FC F0 20 00 00 
00 00 00 00 00 00 00 00 00 FF 01 00 00 00 00 00 
00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 
00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 
10 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 
00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 
00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 
00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 
00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 
00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 
00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 
00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 
00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 
00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 
00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 
00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 
00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 
00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 
00 00 00 00 00 00 FF 77 00 00 7F 00 
'''.strip().replace('\n', '').replace(' ', ''))

log_enable_dtv_all = bytes.fromhex('''
73 00 00 00 03 00 00 00 0A 00 00 00 92 03 00 00 
01 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 
00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 
FF FF 01 00 07 00 00 00 00 00 07 00 00 00 00 00 
00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 
00 02 00 00 00 00 00 00 00 00 00 00 00 00 00 00 
00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 
FE FF 3F 00 00 00 00 00 00 00 00 00 00 00 00 00 
00 00 00 
'''.strip().replace('\n', '').replace(' ', ''))

log_enable_lte_all = bytes.fromhex('''
73 00 00 00 03 00 00 00 0B 00 00 00 09 02 00 00 
06 00 FF FF FF 03 0F 00 00 00 00 00 FF 01 00 00 
FE 0F FE 03 3F 00 3F 00 FF 87 00 00 7F FC 3C 00 
00 00 FF FE FF FF 3F BA FF FE 00 00 FF FF FF F7 
EB 7F FC 79 FF 00 A7 FF 1E 00 00 00 00 00 00 00 
00 00 
'''.strip().replace('\n', '').replace(' ', ''))

log_enable_tdscdma_all = bytes.fromhex('''
73 00 00 00 03 00 00 00 0D 00 00 00 07 02 00 00 
FF FF FF FF FF A3 1F 00 FF 01 FD 8F DF 1F 00 00 
FF FF 7F 00 00 00 FF 1F 00 00 00 00 3F 00 00 00 
FF FF FF FF FF 01 00 00 00 00 00 00 00 00 00 00 
00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 
00 
'''.strip().replace('\n', '').replace(' ', ''))

def parse_qxdm_ts(ts):
    # Epoch: 1980-01-06 00:00:00
    # 1 for 1/800s
    epoch = datetime.datetime(1980, 1, 6, 0, 0, 0)
    try:
        ts_delta = datetime.timedelta(seconds=ts / 800.)
    except:
        ts_delta = datetime.timedelta(seconds=0)
    return epoch + ts_delta

def xxd(buf):
    i = 0
    while i < len(buf):
        if (i + 16) < len(buf):
            print((' '.join(('%02x' % x) for x in buf[i:i+16])) + '\t' + (''.join((chr(x) if chr(x) in XXD_SET else '.') for x in buf[i:i+16])))
        else:
            print((' '.join(('%02x' % x) for x in buf[i:len(buf)])) + '   ' * (16 - (len(buf) - i)) + '\t' + (''.join((chr(x) if chr(x) in XXD_SET else '.') for x in buf[i:len(buf)])))
        i += 16
    print('-------- end --------')

def xxd_oneline(buf):
    print(' '.join(('%02x' % x) for x in buf))
    print('-------- end --------')

def warning(*objs):
    print('Warning: ', *objs, file=sys.stderr)

# Definition copied from libosmocore's include/osmocom/core/gsmtap.h

@unique
class gsmtap_type(IntEnum):
    UM = 0x01
    ABIS = 0x02
    UM_BURST = 0x03
    SIM = 0x04
    GB_LLC = 0x08
    GB_SNDCP = 0x09
    UMTS_RRC = 0x0c
    LTE_RRC = 0x0d
    LTE_MAC = 0x0e
    LTE_MAC_FRAMED = 0x0f
    OSMOCORE_LOG = 0x10
    QC_DIAG = 0x11
    LTE_NAS = 0x12

@unique
class gsmtap_channel(IntEnum):
    UNKNOWN = 0x00
    BCCH = 0x01
    CCCH = 0x02
    RACH = 0x03
    AGCH = 0x04
    PCH = 0x05
    SDCCH = 0x06
    SDCCH4 = 0x07
    SDCCH8 = 0x08
    TCH_F = 0x09
    TCH_H = 0x0a
    PACCH = 0x0b
    CBCH52 = 0x0c
    PDCH = 0x0d
    PTCCH = 0x0e
    CBCH51 = 0x0f

@unique
class gsmtap_umts_rrc_types(IntEnum):
    DL_DCCH = 0
    UL_DCCH = 1
    DL_CCCH = 2
    UL_CCCH = 3
    PCCH = 4
    DL_SHCCH = 5
    UL_SHCCH = 6
    BCCH_FACH = 7
    BCCH_BCH = 8
    MCCH = 9
    MSCH = 10
    HandoverToUTRANCommand = 11
    InterRATHandoverInfo = 12
    SystemInformation_BCH = 13
    System_Information_Container = 14
    UE_RadioAccessCapabilityInfo = 15
    MasterInformationBlock = 16
    SysInfoType1 = 17
    SysInfoType2 = 18
    SysInfoType3 = 19
    SysInfoType4 = 20
    SysInfoType5 = 21
    SysInfoType5bis = 22
    SysInfoType6 = 23
    SysInfoType7 = 24
    SysInfoType8 = 25
    SysInfoType9 = 26
    SysInfoType10 = 27
    SysInfoType11 = 28
    SysInfoType11bis = 29
    SysInfoType12 = 30
    SysInfoType13 = 31
    SysInfoType13_1 = 32
    SysInfoType13_2 = 33
    SysInfoType13_3 = 34
    SysInfoType13_4 = 35
    SysInfoType14 = 36
    SysInfoType15 = 37
    SysInfoType15bis = 38
    SysInfoType15_1 = 39
    SysInfoType15_1bis = 40
    SysInfoType15_2 = 41
    SysInfoType15_2bis = 42
    SysInfoType15_2ter = 43
    SysInfoType15_3 = 44
    SysInfoType15_3bis = 45
    SysInfoType15_4 = 46
    SysInfoType15_5 = 47
    SysInfoType15_6 = 48
    SysInfoType15_7 = 49
    SysInfoType15_8 = 50
    SysInfoType16 = 51
    SysInfoType17 = 52
    SysInfoType18 = 53
    SysInfoType19 = 54
    SysInfoType20 = 55
    SysInfoType21 = 56
    SysInfoType22 = 57
    SysInfoTypeSB1 = 58
    SysInfoTypeSB2 = 59
    ToTargetRNC_Container = 60
    TargetRNC_ToSourceRNC_Container = 61

@unique
class gsmtap_lte_rrc_types(IntEnum):
    DL_CCCH = 0
    DL_DCCH = 1
    UL_CCCH = 2
    UL_DCCH = 3
    BCCH_BCH = 4
    BCCH_DL_SCH = 5
    PCCH = 6
    MCCH = 7
    BCCH_BCH_MBMS = 8
    BCCH_DL_SCH_BR = 9
    BCCH_DL_SCH_MBMS = 10
    SC_MCCH = 11
    SBCCH_SL_BCH = 12
    SBCCH_SL_BCH_V2X = 13
    DL_CCCH_NB = 14
    DL_DCCH_NB = 15
    UL_CCCH_NB = 16
    UL_DCCH_NB = 17
    BCCH_BCH_NB = 18
    BCCH_BCH_TDD_NB = 19
    BCCH_DL_SCH_NB = 20
    PCCH_NB = 21
    SC_MCCH_NB = 22

def create_gsmtap_header(version = 2, payload_type = 0, timeslot = 0,
    arfcn = 0, signal_dbm = 0, snr_db = 0, frame_number = 0,
    sub_type = 0, antenna_nr = 0, sub_slot = 0,
    device_sec = 0, device_usec = 0):

    gsmtap_v2_hdr_def = '!BBBBHBBLBBBB'
    gsmtap_v3_hdr_def = '!BBBBHBBLBBBBQL'
    gsmtap_hdr = b''

    if version == 2:
        gsmtap_hdr = struct.pack(gsmtap_v2_hdr_def,
            2,                           # Version
            4,                           # Header Length
            payload_type,                # Type
            timeslot,                    # GSM Timeslot
            arfcn,                       # ARFCN
            signal_dbm,                  # Signal dBm
            snr_db,                      # SNR dB
            frame_number,                # Frame Number
            sub_type,                    # Subtype
            antenna_nr,                  # Antenna Number
            sub_slot,                    # Subslot
            0                            # Reserved
            )
    elif version == 3:
        gsmtap_hdr = struct.pack(gsmtap_v3_hdr_def,
            3,                           # Version
            7,                           # Header Length
            payload_type,                # Type
            timeslot,                    # GSM Timeslot
            arfcn,                       # ARFCN
            signal_dbm,                  # Signal dBm
            snr_db,                      # SNR dB
            frame_number,                # Frame Number
            sub_type,                    # Subtype
            antenna_nr,                  # Antenna Number
            sub_slot,                    # Subslot
            0,                           # Reserved
            device_sec,
            device_usec)
    else:
        assert (version == 2) or (version == 3), "GSMTAP version should be either 2 or 3"

    return gsmtap_hdr
