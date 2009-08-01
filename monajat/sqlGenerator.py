#! /usr/bin/python
import sys, os, os.path

def parse(f):
  parsed={}
  a=open(f,"rt").readlines()
  key=None
  for n,l in enumerate(a):
    if l.startswith('@'):
      if key: parsed[key]='\n'.join(values)
      kv=l[1:].split('=',1)
      key=kv[0]
      if len(kv)==2: values=[kv[1]]
      else: values=[]
    else:
      if not key: raise SyntaxError, "error parsing file [%s] at line [%d]" % (f,n+1)
      values.append(l.strip())
  if key: parsed[key]='\n'.join(values)
  return parsed

if __name__ == "__main__":
  for f in sys.argv[1:]:
    print parse(f)

