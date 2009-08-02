# -*- coding: utf-8 -*-
import sys, os, os.path
import sqlite3
from glob import glob

clear_record={
  'lang':None,'ref':None,'id':None,
  'text':None,'links':None,'media':None
}

SCHEMA="""
CREATE TABLE "monajat" (
	"lang" TEXT,
	"ref" TEXT,
	"id" TEXT,
	"text" TEXT,
	"links" TEXT,
	"media" TEXT
);

CREATE INDEX LangIndex on monajat (lang);
CREATE INDEX RefIndex on monajat (ref);
"""

SQL_ADD_ROW="""INSERT INTO monajat (lang, ref, id, text, links, media) VALUES (:lang, :ref, :id, :text, :links, :media)"""



#SQL_GET_LANG_START="""SELECT rowid from nodes WHERE idNum=? LIMIT 1"""
def parse(f):
  #parsed={}
  parsed=clear_record
  a=map(lambda l: l.decode('utf-8').rstrip(),open(f,"rt").readlines())
  key=None
  for n,l in enumerate(a):
    if l.startswith(u'@'):
      if key: parsed[key]=u'\n'.join(values)
      kv=l[1:].split(u'=',1)
      key=kv[0].strip()
      if len(kv)==2: values=[kv[1]]
      else: values=[]
    else:
      if not key: raise SyntaxError, "error parsing file [%s] at line [%d]" % (f,n+1)
      values.append(l.strip())
  if key: parsed[key]=u'\n'.join(values)
  return parsed

def generate(prefix):
  db=os.path.join(prefix,'data.db')
  pat=os.path.join(prefix,'*','*.txt')
  files=glob(pat)
  files.sort()
  try: os.unlink(db)
  except OSError: pass
  cn=sqlite3.connect(db)
  c=cn.cursor()
  c.executescript(SCHEMA)
  c.execute('BEGIN TRANSACTION')
  #for f in sys.argv[1:]:
  for f in files:
    print "adding [%s]..." % f
    c.execute(SQL_ADD_ROW, parse(f))
  cn.commit()

if __name__ == "__main__":
  generate('monajat-data')

