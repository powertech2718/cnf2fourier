#!/usr/bin/python3
import sys
import fileinput

# Read in the file
filedata = sys.stdin.readlines()
filedata = ''.join(filedata).rstrip()


filedata = filedata.replace('**', '^')
filedata = filedata.replace('^', '.^')
filedata = filedata.replace('*', '.*')


filedata = "function y = f(x)\ny=" + filedata +"\nendfunction\n" 

#if f is not None:
#    filedata += ","+f+","+t
#filedata += "));"

print(filedata)

