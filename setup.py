#! /usr/bin/python3
from distutils.core import setup
from glob import *
import os, sys
# to install type: 
# python setup.py install --root=/

# list locales
locales=map(lambda i: ('share/'+i,[''+i+'/monajat.mo',]),glob('locale/*/LC_MESSAGES'))
# data files
data_files=[
    ('share/monajat', ['monajat-data/data.db', 'monajat-data/cities.db', 'monajat-data/athan.ogg', 'monajat-data/monajat.svg'] ),
    ('/etc/xdg/autostart',['monajat-autostart.desktop']),
]
data_files.extend(locales)

from distutils.command.build import build
from distutils.command.clean import clean

class my_build(build):
    def run(self):
        build.run(self)
        # generate data
        import monajat.sqlGenerator
        if not os.path.isfile('monajat-data/data.db'):
            monajat.sqlGenerator.generate('monajat-data')

class my_clean(clean):
    def run(self):
        clean.run(self)
        try: os.unlink('monajat-data/data.db')
        except OSError: pass

# do the install
setup (name='monajat', version='2.3.0',
            description='Monajat Islamic Supplications',
            author='Muayyad Saleh Alsadi',
            author_email='sabily.team@lists.launchpad.net',
            url='http://git.ojuba.org/cgit/monajat/about/',
            license='GPLv2',
            packages=['monajat'],
            scripts=['monajat-applet', 'monajat-mod'],
            cmdclass={'build': my_build, 'clean': my_clean},
            data_files=data_files

)
