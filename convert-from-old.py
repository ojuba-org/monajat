#! /usr/bin/python
import sys, os, os.path
import re
import textwrap
from glob import glob
lines_re=re.compile(r"""\<line[^>]*\>(.*?)\</line\>""",re.M | re.S)
desc_re=re.compile(r"""\<description[^>]*\>-?(.*?)-?\</description\>""",re.M | re.S)
space_re=re.compile(r"""([ \t]+)""",re.M)
digits_re=re.compile(r"""(\d+)""",re.M)
tw=textwrap.TextWrapper()
#tw.initial_indent=''
#tw.subsequent_indent=''
tw.break_on_hyphens=False

for i in glob('doa/??/*.xml'):
    fo=i[:-3].lower()+'txt'
    lang=i[4:6]
    r=os.path.basename(i)[0].upper()
    n=digits_re.findall(i)
    c=open(i,"rt").read().decode('utf-8').replace(u'\u200F','')
    l="\n".join(map(lambda i: space_re.sub(' ',i).strip(),lines_re.findall(c))).strip()
    # d is ignored because we want unified d
    d=" ".join(map(lambda i: space_re.sub(' ',i).strip(),desc_re.findall(c))).strip()

    t="\n".join(map(lambda p: tw.fill(p), l.split('\n\n')))
    if n: D=':'.join(n)
    else: D=d
    o="""@lang=%s
@ref=%s
@id=%s
@text
%s""" % (lang,r,D,t)
    open(fo,"wt").write(o.encode('utf-8'))

