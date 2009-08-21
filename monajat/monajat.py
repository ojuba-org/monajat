# -*- coding: utf-8 -*-
import locale
try: locale.setlocale(locale.LC_ALL, '')
except locale.Error: pass
import textwrap
import sys, os, os.path
import sqlite3

from random import randint


SQL_GET_LANG_START="""SELECT rowid FROM monajat WHERE lang=? LIMIT 1"""
SQL_GET_LANG_END="""SELECT rowid FROM monajat WHERE lang=? ORDER BY rowid DESC LIMIT 1"""
SQL_GET_LANGS="""SELECT DISTINCT lang FROM monajat"""
SQL_GET="""SELECT rowid,* FROM monajat WHERE lang=? AND rowid=? LIMIT 1"""

class Monajat (object):
  def __init__(self, width=-1):
    self.__tw=textwrap.TextWrapper()
    self.__tw.break_on_hyphens=False
    self.__width=width
    if width!=-1:  self.__tw.width=width

    self.__stack=[]
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
    l=lang or self.__guess_lang() or self.fallback_lang
    if l not in self.langs: l=self.fallback_lang
    self.lang=l

  def __guess_lang(self):
    a=locale.getlocale(locale.LC_MESSAGES)[0].split('_')
    if not a: return None
    return a[0]

  def __guess_prefix(self):
    e=os.path.dirname(sys.argv[0])
    b='monajat'
    d=os.path.join(e,'monajat-data')
    if os.path.isdir(d): return d
    else: return os.path.join(e,'..','share',b)

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
    if not uid: uid=randint(i,f)
    r=dict(self.__c.execute(SQL_GET, (lang,uid)).fetchone())
    self.__stack.append(r['rowid'])
    r['text']=self.__text_warp(r['text'])
    if r['merits']: r['merits']=self.__text_warp(r['merits'])
    return r

  def get_last_one(self):
    return self.get(uid=self.__stack[-1])

  def go_back(self):
    u=self.__stack.pop()
    r=self.get(uid=u)
    self.__stack.pop()
    return r