# -*- coding: utf-8 -*-
import locale
try: locale.setlocale(locale.LC_ALL, '')
except locale.Error: pass
import textwrap
import sys, os, os.path
import sqlite3

from random import randint

class HistoryEngine():
  def __init__(self, size=10000):
    self.size=size
    self.stack=[]
    self.i=-1

  def get_current(self):
    if self.i>=0: return self.stack[self.i]
    else: return None

  def clear(self):
    self.i=-1
    self.stack=[]

  def go_back(self,n=1):
    if self.i>n-1:
      self.i-=n
      return self.get_current()
    return None

  def go_forward(self,n=1):
    if self.i<len(self.stack)-n:
      self.i+=n
      return self.get_current()
    return None

  def go_first(self):
    if len(self.stack)>0:
      self.i=0
      return self.get_current()
    return None

  def go_last(self):
    if len(self.stack)>0:
      self.i=len(self.stack)-1
      return self.get_current()
    return None

  def push(self,uid):
    self.stack=self.stack[-self.size+1:]
    self.stack.append(uid)
    self.i=len(self.stack)-1


SQL_GET_LANG_START="""SELECT rowid FROM monajat WHERE lang=? LIMIT 1"""
SQL_GET_LANG_END="""SELECT rowid FROM monajat WHERE lang=? ORDER BY rowid DESC LIMIT 1"""
SQL_GET_LANGS="""SELECT DISTINCT lang FROM monajat"""
SQL_GET="""SELECT rowid,* FROM monajat WHERE rowid=? LIMIT 1"""

class Monajat (object):
  def __init__(self, width=-1):
    self.__h=HistoryEngine()
    self.__tw=textwrap.TextWrapper()
    self.__tw.break_on_hyphens=False
    self.__width=width
    if width!=-1:  self.__tw.width=width

    self.__prefix=self.__guess_prefix()
    self.__db=os.path.join(self.__prefix,'data.db')
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
    self.fallback_lang='ar'
    self.set_lang()

  def set_lang(self,lang=None):
    self.__h.go_last()
    l=lang or self.__guess_lang() or self.fallback_lang
    if l not in self.langs: l=self.fallback_lang
    self.lang=l

  def __guess_lang(self):
    a=locale.getlocale(locale.LC_MESSAGES)
    if a and a[0]: a=a[0].split('_')
    else: return None
    return a[0]

  def __guess_prefix(self):
    b='monajat'
    fallback_bin='/usr/bin/'
    fallback_prefix=os.path.join(fallback_bin,'..','share',b)
    e=os.path.dirname(sys.argv[0]) or fallback_bin
    d=os.path.join(e,'monajat-data')
    if os.path.isdir(d): return d
    else:
      d=os.path.join(e,'..','share',b)
      if os.path.isdir(d): return d
      else: return fallback_prefix

  def get_prefix(self):
    return self.__prefix

  def __text_warp(self,text):
    l=text.split('\n\n')
    if self.__width==-1:
      return "\n".join(map(lambda p: p.replace('\n',' '), l))
    else:
      return "\n".join(map(lambda p: self.__tw.fill(p), l))

  def get(self,uid=None, lang=None):
    if not lang: lang=self.lang
    if lang not in self.langs: raise IndexError
    
    i,f=self.lang_boundary[lang]
    if not uid:
      uid=randint(i,f)
      self.__h.push(uid)
    r=dict(self.__c.execute(SQL_GET, (uid,)).fetchone())
    r['text']=self.__text_warp(r['text'])
    if r['merits']: r['merits']=self.__text_warp(r['merits'])
    return r

  def get_current(self):
    u=self.__h.get_current()
    if not u: return self.get()
    return self.get(uid=u)

  def go_forward(self):
    u=self.__h.go_forward()
    r=self.get(uid=u)
    return r

  def go_back(self):
    u=self.__h.go_back()
    if not u: return self.get_current()
    r=self.get(uid=u)
    return r

  def go_first(self):
    u=self.__h.go_first()
    if not u: return self.get_current()
    r=self.get(uid=u)
    return r

  def go_last(self):
    u=self.__h.go_last()
    if not u: return self.get_current()
    r=self.get(uid=u)
    return r

  def clear(self):
    self.__h.clear()
