# -*- coding: utf-8 -*-
import random as rd

def generate_key(**parameters):
    quartet='0123456789abcdef'
    if parameters['key generate']:
        key=''
        for i in range(32):
            key = key + quartet[rd.randint(0,15)]
        key_f=open(parameters['key file'], "w")
        print(key, file=key_f)
        key_f.close()
        key = (key + '\r').encode(parameters['encoding']) 
    else:
        key_f=open(parameters['key file'], "r")
        key = key_f.readline()
        key = (key[0:len(key)-1] + '\r').encode(parameters['encoding'])
        key_f.close()
    return key

def generate_plaintext(**parameters):
    rd.seed(1);
    quartet='0123456789abcdef'
    if parameters['plaintext generate']:
        plaintext=[]
        plain_f=open(parameters['plaintext file'], "w")
        for i in range(parameters['nb_plain']):
            plaintext.append('')
            for j in range(32):
                plaintext[i] = plaintext[i] + quartet[rd.randint(0,15)]
            print(plaintext[i], file=plain_f)
            plaintext[i] = (plaintext[i] + '\r').encode('utf-8')
        plain_f.close()
    else:
        plaintext=[]
        plain_f=open(parameters['plaintext file'], "r")
        for i in range(parameters['nb_plain']):
            plaintext.append(plain_f.readline())
            plaintext[i] = ((plaintext[i])[0:len(plaintext[i])-1] + '\r').encode('utf-8')
        plain_f.close()
    return plaintext

def load_plaintext(**parameters):
    plain=[]
    with open(parameters['plaintext file'], 'r') as f:
        for i in range(0,parameters['nb_plain']):
            plain.append([])
            s=f.readline()
            for j in range(0, 16):
                plain[len(plain)-1].append(int(s[j:j+2], 16))
                i=i+1
    return plain