# -*- coding: utf-8 -*-
import sys, os, os.path
import sqlite3

from random import randint

SQL_GET_LANG_START="""SELECT rowid FROM monajat WHERE lang=? LIMIT 1"""
SQL_GET_LANG_END="""SELECT rowid FROM monajat WHERE lang=? ORDER BY rowid DESC LIMIT 1"""
SQL_GET_LANGS="""SELECT DISTINCT lang FROM monajat"""
SQL_GET="""SELECT * FROM monajat WHERE lang=? AND rowid=? LIMIT 1"""

class Monajat (object):
  def __init__(self,prefix):
    self.__db=os.path.join(prefix,'data.db')
    self.__cn=sqlite3.connect(self.__db)
    self.__c=self.__cn.cursor()
    self.langs=map(lambda a: a[0],self.__c.execute(SQL_GET_LANGS).fetchall())
    self.lang_boundary={}
    for l in self.langs:
      i=self.__c.execute(SQL_GET_LANG_START, (l,)).fetchone()[0]
      f=self.__c.execute(SQL_GET_LANG_END, (l,)).fetchone()[0]
      self.lang_boundary[l]=(i,f)
    self.__cn.row_factory=sqlite3.Row
    self.__c=self.__cn.cursor()

  def get(self,lang=None):
    if not lang: lang='ar'
    if lang not in self.langs: raise IndexError
    i,f=self.lang_boundary[lang]
    row=randint(i,f)
    return self.__c.execute(SQL_GET, (lang,row)).fetchone()

def guess_prefix():
  e=os.path.dirname(sys.argv[0])
  b=os.path.basename(sys.argv[0])
  d=os.path.join(e,'monajat-data')
  if os.path.isdir(d): return d
  else: return os.path.join(e,'..','share',b)

if __name__ == "__main__":
  m=Monajat(guess_prefix())
  print m.get()['text']

