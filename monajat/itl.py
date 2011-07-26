# -*- coding: utf-8 -*-
"""
ITL binding for python
"""
import time
from ctypes import *

class Date(Structure):
  """
  This holds the current date info.
  """
  _fields_ = [
    ('day', c_int),
    ('month', c_int),
    ('year', c_int),
  ]
  def update(self):
    """
    return True if changed
    """
    d=time.localtime()
    if d.tm_year==self.year and d.tm_mon==self.month and d.tm_mday==self.day: return False
    self.day, self.month, self.year = d.tm_mday, d.tm_mon, d.tm_year
    return True

class Location(Structure):
  """
  This holds the location info. 

  degreeLong	- Longitude in decimal degree.
  degreeLat	- Latitude in decimal degree.
  gmtDiff	- GMT difference at regular time.
  dst		- Daylight savings time switch (0 if not used).
  			Setting this to 1 should add 1 hour to all the
  			calculated prayer times
  seaLevel	- Height above Sea level in meters
  pressure	- Atmospheric pressure in millibars (the
  			astronomical standard value is 1010)
  temperature	- Temperature in Celsius degree (the astronomical
  			standard value is 10)
  """
  _fields_ = [
    ('degreeLong', c_double), # Longitude in decimal degree.
    ('degreeLat', c_double),  # Latitude in decimal degree.
    ('gmtDiff', c_double),    # GMT difference at regular time.
    ('dst', c_int),           # Daylight savings time switch (0 if not used).
                              # Setting this to 1 should add 1 hour to all the
                              # calculated prayer times
    ('seaLevel', c_double),   # Height above Sea level in meters
    ('pressure', c_double),   # Atmospheric pressure in millibars (the
                              # astronomical standard value is 1010)
    ('temperature', c_double) # Temperature in Celsius degree (the astronomical
                              # standard value is 10)
  ]

class Method(Structure):
  """
  This structure holds the calculation method used. NOTE: Before explicitly
  setting any of these values, it is more safe to default initialize them
  by calling 'getMethod(0, &method)'

        double fajrAng;     /* Fajr angle */
        double ishaaAng;    /* Ishaa angle */
        double imsaakAng;   /* The angle difference between Imsaak and Fajr (
                               default is 1.5)*/
        int fajrInv;        /* Fajr Interval is the amount of minutes between
                               Fajr and Shurooq (0 if not used) */
        int ishaaInv;       /* Ishaa Interval is the amount if minutes between
                               Ishaa and Maghrib (0 if not used) */
        int imsaakInv;      /* Imsaak Interval is the amount of minutes between
                               Imsaak and Fajr. The default is 10 minutes before
                               Fajr if Fajr Interval is set */
        int round;          /* Method used for rounding seconds:
                               0: No Rounding. "Prayer.seconds" is set to the
                                  amount of computed seconds.
                               1: Normal Rounding. If seconds are equal to
                                  30 or above, add 1 minute. Sets
                                  "Prayer.seconds" to zero.
                               2: Special Rounding. Similar to normal rounding
                                  but we always round down for Shurooq and
                                  Imsaak times. (default)
                               3: Aggressive Rounding. Similar to Special
                                  Rounding but we add 1 minute if the seconds
                                  value is equal to 1 second or more.  */
        int mathhab;        /* Assr prayer shadow ratio:
                               1: Shaf'i (default)
                               2: Hanafi */
        double nearestLat;  /* Latitude Used for the 'Nearest Latitude' extreme
                               methods. The default is 48.5 */
        int extreme;        /* Extreme latitude calculation method (see
                               below) */
        int offset;         /* Enable Offsets switch (set this to 1 to
                               activate). This option allows you to add or
                               subtract any amount of minutes to the daily
                               computed prayer times based on values (in
                               minutes) for each prayer in the offList array */     
        double offList[6];  /* For Example: If you want to add 30 seconds to
                               Maghrib and subtract 2 minutes from Ishaa:
                                    offset = 1
                                    offList[4] = 0.5
                                    offList[5] = -2
                               ..and than call getPrayerTimes as usual. */
  --
       Supported methods for Extreme Latitude calculations (Method.extreme) -
       (see the file "./doc/method-info.txt" for details) :
      
       0:  none. if unable to calculate, leave as 99:99
       1:  Nearest Latitude: All prayers Always
       2:  Nearest Latitude: Fajr Ishaa Always
       3:  Nearest Latitude: Fajr Ishaa if invalid
       4:  Nearest Good Day: All prayers Always
       5:  Nearest Good Day: Fajr Ishaa if invalid (default)
       6:  1/7th of Night: Fajr Ishaa Always
       7:  1/7th of Night: Fajr Ishaa if invalid
       8:  1/7th of Day: Fajr Ishaa Always
       9:  1/7th of Day: Fajr Ishaa if invalid
       10: Half of the Night: Fajr Ishaa Always
       11: Half of the Night: Fajr Ishaa if invalid
       12: Minutes from Shorooq/Maghrib: Fajr Ishaa Always (e.g. Maghrib=Ishaa)
       13: Minutes from Shorooq/Maghrib: Fajr Ishaa If invalid
  --
    /* This function is used to auto fill the Method structure with predefined
       data. The supported auto-fill methods for calculations at normal
       circumstances are:
    
      0: none. Set to default or 0
      1: Egyptian General Authority of Survey
      2: University of Islamic Sciences, Karachi (Shaf'i)
      3: University of Islamic Sciences, Karachi (Hanafi)
      4: Islamic Society of North America
      5: Muslim World League (MWL)
      6: Umm Al-Qurra, Saudi Arabia
      7: Fixed Ishaa Interval (always 90)
      8: Egyptian General Authority of Survey (Egypt)
      (see the file "./doc/method-info.txt" for more details)
    */
  """
  _fields_ = [
    ('fajrAng', c_double),
    ('ishaaAng', c_double),
    ('imsaakAng', c_double),
    ('fajrInv', c_int),
    ('ishaaInv', c_int),
    ('imsaakInv', c_int),
    ('round', c_int),
    ('mathhab', c_int),
    ('nearestLat', c_double),
    ('extreme', c_int),
    ('offset', c_int),
    ('offList', c_double*6),
  ]

class Prayer(Structure):
  """
    This structure holds the prayer time output for a single prayer. */
        int hour;       /* prayer time hour */
        int minute;     /* prayer time minute */
        int second;     /* prayer time second */
        int isExtreme;  /* Extreme calculation status. The 'getPrayerTimes'
                           function sets this variable to 1 to indicate that
                           this particular prayer time has been calculated
                           through extreme latitude methods and NOT by
                           conventional means of calculation. */ 
  """
  _fields_ = [
    ('hour', c_int),
    ('minute', c_int),
    ('second', c_int),
    ('isExtreme', c_int),
  ]
  def format(self, h=12):
    if h!=12:
      return "%02d:%02d" % (self.hour, self.minute,)
    return "%02d:%02d %s" % ((self.hour % 12) or 12, self.minute, self.hour>=12 and "PM" or "AM")

try: itl=cdll.LoadLibrary("libitl.so.0")
except OSError as e: raise e

def getMethod(i, method=None):
  """
  returns the set method
  """
  if method==None:
    method=Method()
  itl.getMethod(7, pointer(method))
  return method

def getPrayerTimes(loc, method, date, ptList=None):
  if ptList==None:
    ptList=(Prayer*6)()
  itl.getPrayerTimes(pointer(loc), pointer(method), pointer(date), pointer(ptList))
  return ptList



class PrayerTimes:
  def __init__(self, method_n=6, lat=21.43, lon=39.77, tz=3.0, dst=0, alt=0, pressure=1010, temp=10, **kw):
    """
    location defaults to Mecca
    method defaults to Umm Al-Qurra
    """
    self.location=Location()
    self.date=Date()
    self.stamps=[]
    self.stamp_date=Date()
    self.method=Method()
    self.ptList=(Prayer*6)()
    self.location.degreeLong=lon
    self.location.degreeLat=lat
    self.location.gmtDiff=tz
    self.location.dst=dst
    print tz,dst
    self.location.seaLevel = alt
    self.location.pressure = pressure
    self.location.temperature= temp
    self.set_method(method_n)
  
  def set_location(self, lat=21.43, lon=39.77, tz=3.0, dst=0, alt=0, pressure=1010, temp=10):
    self.location.degreeLong=lon
    self.location.degreeLat=lat
    self.location.gmtDiff=tz
    self.location.dst=dst
    self.location.seaLevel = alt
    self.location.pressure = pressure
    self.location.temperature= temp
    # self.get_prayers(False) not needed as implied by next line
    self.get_prayer_time_stamps(False)

  def set_method(self, n):
    getMethod(n, self.method)
    self.get_prayers(False)
    return self.method

  def update(self):
    if not self.date.update(): return False
    self.get_prayers(False)
    return True

  def get_prayers(self, cache=True):
    if cache and not self.date.update(): return self.ptList
    return getPrayerTimes(self.location, self.method, self.date, self.ptList)

  def get_prayer_time_stamps(self, cache=True):
    if cache and self.stamps and not self.stamp_date.update(): return self.stamps
    t=int(time.time())
    d=time.localtime()
    t-=d.tm_hour*3600+d.tm_min*60+d.tm_sec
    self.stamps=map(lambda p: t+p.hour*3600+p.minute*60+p.second, self.get_prayers(cache))
    self.stamps.append(self.stamps[0]+86400)
    return self.stamps

  def get_next_time_stamp(self, delta=0.0):
    t=time.time()
    l=self.get_prayer_time_stamps()
    for i,j in enumerate(l):
      if i==1: continue
      if t-j<=delta: return i, j, j-t
    return -1, -1, -1

  def get_date_prayers(self, y, m, d, ptList=None):
    date=Date()
    date.day=d
    date.month=m
    date.year=y
    return getPrayerTimes(self.location, self.method, date, ptList)


if __name__ == "__main__":
    # high level examples for Mecca
    pt=PrayerTimes()
    for i in pt.get_prayers():
      print i.hour, i.minute, i.second
    # low level examples for Abu Dhabi
    loc=Location()
    date=Date()
    # fill the Date structure
    date.update()
    # fill the location info. structure
    loc.degreeLat = 24.4833
    loc.degreeLong = 54.35
    loc.gmtDiff = 4
    loc.dst = 0
    loc.seaLevel = 0
    loc.pressure = 1010
    loc.temperature= 10
    # auto fill the method structure. Have a look at prayer.h for a
    # list of supported methods
    method=getMethod(7)
    method.round = 0
    ptList=getPrayerTimes(loc, method, date)
    for i in ptList:
      print i.hour, i.minute, i.second


