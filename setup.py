#! /usr/bin/python
from distutils.core import setup
from glob import *
# to install type: 
# python setup.py install --root=/

# generate data
import monajat.sqlGenerator
monajat.sqlGenerator.generate('monajat-data')

# list locales
locales=map(lambda i: ('share/'+i,[''+i+'/monajat.mo',]),glob('locale/*/LC_MESSAGES'))
# data files
data_files=[
  ('share/monajat', ['monajat-data/data.db', 'monajat-data/monajat.svg'] ),
  ('bin',['monajat-applet','monajat-mod'] ),
  ('/etc/xdg/autostart',['monajat-autostart.desktop']),
]
data_files.extend(locales)

# do the install
setup (name='monajat', version='2.2.0',
      description='Monajat Islamic Supplications',
      author='Muayyad Saleh Alsadi',
      author_email='sabily.team@lists.launchpad.net',
      url='http://git.ojuba.org/cgit/monajat/about/',
      license='GPLv2',
      packages=['monajat'],
      data_files=data_files

)

