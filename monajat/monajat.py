# -*- coding: utf-8 -*-
# -*- Mode: Python; py-indent-offset: 4 -*-
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
        self.h=HistoryEngine()
        self.tw=textwrap.TextWrapper()
        self.tw.break_on_hyphens=False
        self.width=width
        if width!=-1:    self.tw.width=width

        self.prefix=self.guess_prefix()
        self.db=os.path.join(self.prefix,'data.db')
        #self.db='/home/mjlad/PycharmProjects/monajat-master/monajat-data/data.db'
        print(self.db)
        self.cn=sqlite3.connect(self.db, check_same_thread = False)
        self.c=self.cn.cursor()
        self.langs=list(map(lambda a: a[0],self.c.execute(SQL_GET_LANGS).fetchall()))
        self.lang_boundary={}
        for l in self.langs:
            i=self.c.execute(SQL_GET_LANG_START, (l,)).fetchone()[0]
            f=self.c.execute(SQL_GET_LANG_END, (l,)).fetchone()[0]
            self.lang_boundary[l]=(i,f)
        self.cn.row_factory=sqlite3.Row
        self.c=self.cn.cursor()
        self.fallback_lang='ar'
        self.set_lang()
        self.cities_db=os.path.join(self.prefix,'cities.db')
        #self.cities_db = '/home/mjlad/PycharmProjects/monajat-master/monajat-data/cities.db'
        self.cities_cn=sqlite3.connect(self.cities_db)
        self.cities_cn.row_factory=sqlite3.Row
        self.cities_c=self.cities_cn.cursor()
        r=self.cities_c.execute('select v from params where k=?', ('ver',)).fetchone()
        print (dict(r))
        if r: self.cities_db_ver=r['v']
        else: self.cities_db_ver='0'

    def set_lang(self,lang=None):
        self.h.go_last()
        l=lang or self.guess_lang() or self.fallback_lang
        if l not in self.langs: l=self.fallback_lang
        self.lang=l

    def guess_lang(self):
        a=locale.getlocale(locale.LC_MESSAGES)
        if a and a[0]: a=a[0].split('_')
        else: return None
        return a[0]

    def guess_prefix(self):
        b='monajat'
        fallback_bin='/usr/bin/'
        fallback_prefix=os.path.join(fallback_bin,'..','share',b)
        e=os.path.realpath(os.path.dirname(sys.argv[0]) or fallback_bin)
        d=os.path.join(e,'monajat-data')
        if os.path.isdir(d): return d
        else:
            d=os.path.join(e,'..','share',b)
            if os.path.isdir(d): return d
            else: return fallback_prefix

    def get_prefix(self):
        return self.prefix

    def text_warp(self,text):
        l=text.split('\n\n')
        if self.width==-1:
            return "\n".join(map(lambda p: p.replace('\n',' '), l))
        else:
            return "\n".join(map(lambda p: self.tw.fill(p), l))

    def get(self,uid=None, lang=None):
        if not lang: lang=self.lang
        if lang not in self.langs: raise IndexError
        
        i,f=self.lang_boundary[lang]
        if not uid:
            uid=randint(i,f)
            self.h.push(uid)
        r=dict(self.c.execute(SQL_GET, (uid,)).fetchone())
        r['text']=self.text_warp(r['text'])
        if r['merits']: r['merits']=self.text_warp(r['merits'])
        return r

    def get_current(self):
        u=self.h.get_current()
        if not u: return self.get()
        return self.get(uid=u)

    def go_forward(self):
        u=self.h.go_forward()
        r=self.get(uid=u)
        return r

    def go_back(self):
        u=self.h.go_back()
        if not u: return self.get_current()
        r=self.get(uid=u)
        return r

    def go_first(self):
        u=self.h.go_first()
        if not u: return self.get_current()
        r=self.get(uid=u)
        return r

    def go_last(self):
        u=self.h.go_last()
        if not u: return self.get_current()
        r=self.get(uid=u)
        return r

    def clear(self):
        self.h.clear()
