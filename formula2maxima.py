#!/usr/bin/python3
import sys
import fileinput

# Read in the file
filedata = sys.stdin.readlines()
filedata = ''.join(filedata).rstrip()


filedata = filedata.replace('pi', '%pi')
filedata = filedata.replace('I', '%i')


filedata = "f(x) := " + filedata +";\n"
filedata += "float(integrate(f(x),x,0,8));\n"

#if f is not None:
#    filedata += ","+f+","+t
#filedata += "));"

print(filedata)

