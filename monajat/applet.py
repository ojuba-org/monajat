# -*- coding: utf-8 -*-
import os, os.path
import itl
from monajat import Monajat
from utils import init_dbus
import locale, gettext

import glib
import gtk
import pynotify
import cgi
import math
import json
import time
from functools  import cmp_to_key
import gst

# in gnome3 ['actions', 'action-icons', 'body', 'body-markup', 'icon-static', 'persistence']
# in gnome2 ['actions', 'body', 'body-hyperlinks', 'body-markup', 'icon-static', 'sound']
# "resident"

class SoundPlayer:
  def __init__(self, fn=None, change_play_status=None):
    if not fn: fn=""
    self.fn=fn
    self.change_play_status=change_play_status
    self.gst_player = gst.element_factory_make("playbin2", "player")
    self.gst_player.set_property("uri", "file://" + fn)
    bus = self.gst_player.get_bus()
    bus.add_signal_watch()
    bus.connect("message", self.on_message)
    
  def play(self):
    fn=self.fn
    if fn and os.path.isfile(fn):
      self.gst_player.set_state(gst.STATE_PLAYING)
  
  def stop(self):
    self.gst_player.set_state(gst.STATE_NULL)
  
  def set_filename(self,fn):
    if not fn: fn=""
    self.fn=fn
    self.gst_player.set_property("uri", "file://" + fn)
    
  def on_message(self, bus, message):
    t = message.type
    print t
    if t == gst.MESSAGE_EOS:
      if self.change_play_status: self.change_play_status()
      self.gst_player.set_state(gst.STATE_NULL)
    elif t == gst.MESSAGE_ERROR:
      self.gst_player.set_state(gst.STATE_NULL)
      err, debug = message.parse_error()
      print "Error: %s" % err, debug


class ConfigDlg(gtk.Dialog):
  def __init__(self, applet):
    gtk.Dialog.__init__(self)
    self.applet=applet
    self.m=applet.m
    self.set_size_request(300,400)
    self.set_resizable(False) # FIXME: reconsider this
    self.connect('delete-event', lambda w,*a: w.hide() or True)
    self.connect('response', lambda w,*a: w.hide() or True)
    self.set_title(_('Monajat Configuration'))
    self.add_button(_('Cancel'), gtk.RESPONSE_CANCEL)
    self.add_button(_('Save'), gtk.RESPONSE_OK)
    tabs=gtk.Notebook()
    self.get_content_area().add(tabs)
    vb=gtk.VBox()
    tabs.append_page(vb, gtk.Label(_('Generic')))
    self.auto_start = b = gtk.CheckButton(_("Auto start"))
    self.auto_start.set_active(not os.path.exists(self.applet.skip_auto_fn))
    vb.pack_start(b, False, False, 2)
    self.show_merits = b = gtk.CheckButton(_("Show merits"))
    self.show_merits.set_active(self.applet.conf['show_merits'])
    vb.pack_start(b, False, False, 2)
    hb = gtk.HBox()
    vb.pack_start(hb, False, False, 2)
    hb.pack_start(gtk.Label(_('Language:')), False, False, 2)
    self.lang = b = gtk.combo_box_new_text()
    hb.pack_start(b, False, False, 2)
    selected = 0
    for i,j in enumerate(self.applet.m.langs):
      b.append_text(j)
      if self.m.lang==j: selected=i
    b.set_active(selected)
    
    hb = gtk.HBox()
    vb.pack_start(hb, False, False, 2)
    hb.pack_start(gtk.Label(_('Time:')), False, False, 2)
    hb.pack_start(gtk.HBox(), True, True, 2)
    self.timeout = b = gtk.SpinButton(gtk.Adjustment(5, 0, 90, 5, 5))
    b.set_value(self.applet.conf['minutes'])
    hb.pack_start(b, False, False, 2)
    hb.pack_start(gtk.Label(_('minutes')), False, False, 2)

    vb=gtk.VBox()
    tabs.append_page(vb, gtk.Label(_('Location')))
    
    hb=gtk.HBox()
    vb.pack_start(hb, False, False, 2)
    e=gtk.Entry()
    e.connect('activate', self._city_search_cb)
    hb.pack_start(e, False, False, 2)
    
    s = gtk.TreeStore(str, bool, int) # label, is_city, id
    self.cities_tree=tree=gtk.TreeView(s)
    col=gtk.TreeViewColumn('Location', gtk.CellRendererText(), text=0)
    col.set_sizing(gtk.TREE_VIEW_COLUMN_AUTOSIZE)
    tree.insert_column(col, -1)
    tree.set_enable_search(True)
    tree.set_search_column(0)
    tree.set_headers_visible(False)
    tree.set_tooltip_column(0)
    
    scroll=gtk.ScrolledWindow()
    scroll.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_ALWAYS)
    scroll.add(tree)
    vb.pack_start(scroll, True, True, 2)

    self.sound_player = SoundPlayer(self.applet.conf['athan_media_file'], self.change_play_status)
    vb=gtk.VBox()
    tabs.append_page(vb, gtk.Label(_('Notification')))
    hb=gtk.HBox()
    vb.pack_start(hb, False, True, 3)
    hb.pack_start(gtk.Label(_('Sound:')), False, True, 2)
    self.sound_file = b = gtk.FileChooserButton(_('Choose Athan media file'))
    self.sound_file.set_filename(self.applet.conf['athan_media_file'])
    ff=gtk.FileFilter()
    ff.set_name(_('Sound Files'))
    ff.add_pattern('*.ogg')
    ff.add_pattern('*.mp3')
    b.add_filter(ff)
    ff=gtk.FileFilter()
    ff.set_name(_('All files'))
    ff.add_pattern('*')
    b.add_filter(ff)
    self.play_b=pb=gtk.Button(_('Play'))
    pb.connect('clicked', self.play_cb)
    hb.pack_end(pb, False, False, 2)
    hb.pack_end(b, True, True, 5)
    
    hb = gtk.HBox()
    vb.pack_start(hb, False, False, 3)
    self.notify_before_b = b = gtk.CheckButton(_("Notify before"))
    self.notify_before_t = t = gtk.SpinButton(gtk.Adjustment(5, 5, 20, 5, 5))
    b.set_active(self.applet.conf['notify_before_min']!=0)
    t.set_value(self.applet.conf['notify_before_min'])
    hb.pack_start(b,True,True,2)
    hb.pack_start(t,False,False,2)
    hb.pack_start(gtk.Label(_('minutes')),False,False,2)
    
    self._fill_cities()

  def change_play_status(self, status=None):
    if status==None: status=self.sound_player.gst_player.get_state()
    if status==gst.STATE_PLAYING:
      self.sound_file.set_sensitive(False)
      self.play_b.set_property('label', _('Stop'))
    else:
      self.sound_file.set_sensitive(True)
      self.play_b.set_property('label', _('Play'))

  def play_cb(self, b):
    fn=self.sound_file.get_filename()
    if not fn: fn=''
    if b.get_label() == _('Play'):
      if not os.path.isfile(fn): return
      self.change_play_status(gst.STATE_PLAYING)
      self.sound_player.set_filename(fn)
      self.sound_player.play()
    else:
      self.change_play_status(gst.STATE_NULL)
      self.sound_player.stop()

  def _city_search_cb(self, e):
    # FIXME: if same as last successful search text don't update first_match_path
    # FIXME: and if self.city_found same as first_match_path highlight in red
    txt=e.get_text().strip()
    e.modify_base(gtk.STATE_NORMAL, None)
    tree=self.cities_tree
    store, p=tree.get_selection().get_selected_rows()
    if p: current=p[0]
    else: current=None
    limit=None
    def tree_walk_cb(model, path, i):
      if current and path<=current: return False
      if limit and path>=limit: return True
      if txt in store.get_value(i,0):
        tree.expand_to_path(path)
        tree.scroll_to_cell(path)
        tree.get_selection().select_iter(i)
        self.city_found=path
        return True
    self.city_found=None
    store.foreach(tree_walk_cb)
    if not self.city_found:
      limit=current
      current=None
      store.foreach(tree_walk_cb)
      if not self.city_found:
        e.modify_base(gtk.STATE_NORMAL, gtk.gdk.color_parse("#FFCCCC"))
    
  def _fill_cities(self):
    tree=self.cities_tree
    s=tree.get_model()
    rows=self.m.cities_c.execute('SELECT * FROM cities')
    country, country_i = None, None
    state, state_i=None, None
    city_path=None
    for R in rows:
      r=dict(R)
      if country!=r['country']:
        country_i=s.append(None,(r['country'], False, 0))
      if state!=r['state']:
        state_i=s.append(country_i,(r['state'], False, 0))
      country=r['country']
      state=r['state']
      city=u'%s - %s' % (r['name'], r['locale_name'])
      #city=r['name']
      city_i=s.append(state_i,(city, True, r['id']))
      if self.applet.conf.get('city_id',None)==r['id']: city_path=s.get_path(city_i)
    if city_path:
      tree.expand_to_path(city_path)
      tree.get_selection().select_path(city_path)
      tree.scroll_to_cell(city_path)

  def run(self, *a, **kw):
    self.auto_start.set_active(not os.path.exists(self.applet.skip_auto_fn))
    return gtk.Dialog.run(self, *a, **kw)

class applet(object):
  skip_auto_fn=os.path.expanduser('~/.monajat-applet-skip-auto')
  def __init__(self):
    self.conf_dlg=None
    self.chngbody=time.time()
    self.minutes_counter=0
    self.m=Monajat() # you may pass width like 20 chars
    self.sound_player=SoundPlayer()
    self.load_conf()
    self.prayer_items=[]
    kw=self.conf_to_prayer_args()
    self.prayer=itl.PrayerTimes(**kw)
    l=filter(lambda i: i.startswith('ar_') and "_" in i and '.' not in i, locale.locale_alias.keys())
    if l:
      l,c=l[0].split('_',1)
      l=l+"_"+c.upper()+".UTF-8"
      os.environ['LC_MESSAGES']=l
      locale.setlocale(locale.LC_MESSAGES, l)
    ld=os.path.join(self.m.get_prefix(),'..','locale')
    gettext.install('monajat', ld, unicode=0)
    self.ptnames=[_("Fajr"), _("Sunrise"), _("Dhuhr"), _("Asr"), _("Maghrib"), _("Isha'a")]
    self.clip1=gtk.Clipboard(selection="CLIPBOARD")
    self.clip2=gtk.Clipboard(selection="PRIMARY")
    self.init_about_dialog()
    self.init_menu()
    #self.s=gtk.status_icon_new_from_file(os.path.join(self.m.get_prefix(),'monajat.svg'))
    #self.s.connect('popup-menu',self.popup_cb)
    #self.s.connect('activate',self.next_cb)
    pynotify.init('MonajatApplet')
    self.notifycaps = pynotify.get_server_caps ()
    print self.notifycaps
    self.notify=pynotify.Notification("MonajatApplet")
    self.notify.set_property('icon-name','monajat')
    self.notify.set_property('summary', _("Monajat") )
    if 'actions' in self.notifycaps:
      self.notify.add_action("previous", _("previous"), self.notify_cb)
      self.notify.add_action("next", _("next"), self.notify_cb)
      self.notify.add_action("copy", _("copy"), self.notify_cb)
    self.notify.set_timeout(5000)
    #self.notify.set_urgency(pynotify.URGENCY_LOW)
    self.notify.set_hint('resident', True)
    #self.notify.set_hint('transient', True)

    self.statusicon = gtk.StatusIcon ()
    #self.notify.attach_to_status_icon(self.statusicon)
    self.statusicon.connect('popup-menu',self.popup_cb)
    self.statusicon.connect('activate',self.next_cb)
    self.statusicon.set_title(_("Monajat"))
    self.statusicon.set_from_file(os.path.join(self.m.get_prefix(),'monajat.svg'))

    self.notif_last_athan=-1
    self.next_athan_delta=-1
    self.next_athan_i=-1
    self.last_athan=-1
    self.last_time=0
    self.first_notif_done=False
    self.start_time=time.time()
    glib.timeout_add_seconds(1, self.timer_cb)

  def config_cb(self, *a):
    if self.conf_dlg==None:
      self.conf_dlg=ConfigDlg(self)
      self.conf_dlg.show_all()
    r=self.conf_dlg.run()
    if r==gtk.RESPONSE_OK:
      self.save_auto_start()
      self.save_conf()

  def default_conf(self):
    self.conf={}
    self.conf['show_merits']='1'
    self.conf['lang']=self.m.lang
    self.conf['minutes']='10'
    self.conf['athan_media_file']=os.path.join(self.m.prefix, 'athan.ogg')
    self.conf['notify_before_min']='10'

  def conf_to_prayer_args(self):
    kw={}
    if not self.conf.has_key('city_id'): return kw
    c=self.m.cities_c
    try: c_id=int(self.conf['city_id'])
    except ValueError: return kw
    except TypeError: return kw
    r=c.execute('SELECT * FROM cities AS c LEFT JOIN dst AS d ON d.i=dst_id WHERE c.id=?', (c_id,)).fetchone()
    # FIXME: if not r: defaults to Makka
    kw=dict(r)
    if "alt" not in kw or not kw["alt"]: kw["alt"]=0.0
    kw["tz"]=kw["utc"]
    # NOTE: get DST from machine local setting
    kw["dst"]=time.daylight
    # FIXME: dst should have the following 3 options
    # a. auto from system, b. auto from algorithm, c. specified to 0/1 by user
    #dst=kw["dst_id"]
    #if not dst: kw["dst"]=0
    #else:
    #  # FIXME: add DST logic here
    #  kw["dst"]=1
    print kw
    #lat=21.43, lon=39.77, tz=3.0, dst=0, alt=0, pressure=1010, temp=10
    return kw


  def parse_conf(self, s):
    self.default_conf()
    l1=map(lambda k: k.split('=',1), filter(lambda j: j,map(lambda i: i.strip(),s.splitlines())) )
    l2=map(lambda a: (a[0].strip(),a[1].strip()),filter(lambda j: len(j)==2,l1))
    r=dict(l2)
    self.conf.update(dict(l2))
    return len(l1)==len(l2)

  def load_conf(self):
    s=''
    fn=os.path.expanduser('~/.monajat-applet.rc')
    if os.path.exists(fn):
      try: s=open(fn,'rt').read()
      except OSError: pass
    self.parse_conf(s)
    if self.conf.has_key('city_id'):
      # make sure city_id is set using the same db
      if not self.conf.has_key('cities_db_ver') or \
        self.conf['cities_db_ver']!=self.m.cities_db_ver:
          del self.conf['city_id']
      # make sure it's integer
      try: c_id=int(self.conf['city_id'])
      except ValueError: del self.conf['city_id']
      except TypeError: del self.conf['city_id']
      else: self.conf['city_id']=c_id
    # set athan media file exists
    self.sound_player.set_filename(self.conf['athan_media_file'])
    # fix types
    try: self.conf['minutes']=math.ceil(float(self.conf['minutes'])/5.0)*5
    except ValueError: self.conf['minutes']=0
    try: self.conf['show_merits']=int(self.conf['show_merits']) 
    except ValueError: self.conf['show_merits']=1
    try: self.conf['notify_before_min']=int(float(self.conf['notify_before_min']))
    except ValueError: self.conf['notify_before_min']=10
    self.m.set_lang(self.conf['lang'])
    self.m.clear()

  def apply_conf(self):
    kw=self.conf_to_prayer_args()
    self.prayer=itl.PrayerTimes(**kw)
    self.update_prayer()
    self.sound_player.set_filename(self.conf['athan_media_file'])
    self.m.clear()
    self.m.set_lang(self.conf['lang'])
    self.render_body(self.m.go_forward())

  def save_conf(self):
    self.conf['cities_db_ver']=self.m.cities_db_ver
    self.conf['show_merits']=int(self.conf_dlg.show_merits.get_active())
    self.conf['lang']=self.conf_dlg.lang.get_active_text()
    self.conf['minutes']=int(self.conf_dlg.timeout.get_value())
    self.conf['athan_media_file']=self.conf_dlg.sound_file.get_filename()
    self.conf['notify_before_min']=int(self.conf_dlg.notify_before_b.get_active() and self.conf_dlg.notify_before_t.get_value())
    m, p=self.conf_dlg.cities_tree.get_selection().get_selected_rows()
    if p:
      city_id=m[p[0]][2]
      if city_id: self.conf['city_id']=city_id
    print "** saving conf", self.conf
    fn=os.path.expanduser('~/.monajat-applet.rc')
    s='\n'.join(map(lambda k: "%s=%s" % (k,str(self.conf[k])), self.conf.keys()))
    try: open(fn,'wt').write(s)
    except OSError: pass
    self.apply_conf()

  def athan_show_notif(self):
    self.last_time=time.time()
    self.first_notif_done=True
    s=self.ptnames[self.last_athan]
    self.notify.set_property('body', _('''It's now time for %s prayer''') % s)
    self.notify.show()

  def athan_notif_cb(self):
    i, t, dt=self.prayer.get_next_time_stamp()
    if i<0: return False
    dt=max(dt, 0)
    i=i%6
    self.next_athan_delta=dt
    self.next_athan_i=i
    if dt<30 and i!=self.last_athan:
      print "it's time for prayer number:", i
      self.last_athan=i
      self.sound_player.play()
      self.athan_show_notif()
      return True
    return False

  def timer_cb(self, *args):
    dt=int(time.time()-self.last_time)
    if self.prayer.update():
      self.update_prayer()
    if self.athan_notif_cb(): return True
    if not self.first_notif_done:
      if int(time.time()-self.start_time)>=10:
        self.next_cb()
      return True
    if self.conf['notify_before_min'] and self.next_athan_delta<=self.conf['notify_before_min']*60 and self.next_athan_i!=self.notif_last_athan:
      self.notif_last_athan=self.next_athan_i
      self.next_cb()
    elif self.conf['minutes'] and dt>=self.conf['minutes']*60:
      self.next_cb()
    return True

  def hide_cb(self, w, *args): w.hide(); return True

  def fuzzy_delta(self):
    if self.next_athan_i<0: return ""
    t=max(int(self.next_athan_delta),0)
    d={"prayer":self.ptnames[self.next_athan_i]}
    d['hours']=t/3600
    t%=3600
    d['minutes']=t/60
    if d["hours"]:
      if d["minutes"]<5:
        r=_("""%(hours)d hours till %(prayer)s prayer""") % d
      else:
        r=_("""%(hours)d hours and %(minutes)d minutes till %(prayer)s prayer""") % d
    elif d["minutes"]>=2:
      r=_("""less than %(minutes)d minutes till %(prayer)s prayer""") % d
    else:
      r=_("""less than a minute till %(prayer)s prayer""") % d
    if "body-markup" in self.notifycaps:
      return "<b>%s</b>\n\n" % cgi.escape(r)
    return "%s\n\n" % r

  def render_body(self, m):
    merits=m['merits']
    if not self.conf['show_merits']: merits=None
    if "body-markup" in self.notifycaps:
      body=cgi.escape(m['text'])
      if merits: body+="""\n\n<b>%s</b>: %s""" % (_("Its Merits"),cgi.escape(merits))
    else:
      body=m['text']
      if merits: body+="""\n\n** %s **: %s""" % (_("Its Merits"),merits)
    
    if "body-hyperlinks" in self.notifycaps:
      L=[]
      links=m.get('links',u'').split(u'\n')
      for l in links:
        ll=l.split(u'\t',1)
        url=cgi.escape(ll[0])
        if len(ll)>1: t=cgi.escape(ll[1])
        else: t=url
        L.append(u"""<a href='%s'>%s</a>""" % (url,t))
      l=u"\n\n".join(L)
      body+=u"\n\n"+l
    # if we are close to time show it before supplication
    if self.next_athan_delta>=0 and self.next_athan_delta<=600:
      body=self.fuzzy_delta()+body
    else:
      body=body+"\n\n"+self.fuzzy_delta()
    #timeNP,isnear, istime = self.nextprayer_note(self.get_nextprayer(self.prayer.get_prayers()))
    #if not isnear: body+=timeNP
    #else: body=timeNP+body
    self.notify.set_property('body', body)
    return body

  def dbus_cb(self, *args):
    self.minutes_counter=1
    self.next_cb()
    return 0

  def next_cb(self,*args):
    self.last_time=time.time()
    self.first_notif_done=True
    try: self.notify.close()
    except glib.GError: pass
    self.render_body(self.m.go_forward())
    self.notify.show()
    return True

  def prev_cb(self, *args):
    self.last_time=time.time()
    try: self.notify.close()
    except glib.GError: pass
    self.render_body(self.m.go_back())
    self.notify.show()

  def copy_cb(self,*args):
    r=self.m.get_current()
    self.clip1.set_text(r['text'])
    self.clip2.set_text(r['text'])

  def init_about_dialog(self):
    # FIXME: please add more the authors
    self.about_dlg=gtk.AboutDialog()
    self.about_dlg.set_default_response(gtk.RESPONSE_CLOSE)
    self.about_dlg.connect('delete-event', self.hide_cb)
    self.about_dlg.connect('response', self.hide_cb)
    try: self.about_dlg.set_program_name("Monajat")
    except: pass
    self.about_dlg.set_name(_("Monajat"))
    #self.about_dlg.set_version(version)
    self.about_dlg.set_copyright("Copyright © 2009 sabily.org")
    self.about_dlg.set_comments(_("Monajat supplications"))
    self.about_dlg.set_license("""\
    This program is free software; you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation; either version 2 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.
""")
    self.about_dlg.set_website("https://launchpad.net/monajat")
    self.about_dlg.set_website_label("Monajat web site")
    self.about_dlg.set_authors(["Fadi al-katout <cutout33@gmail.com>",
                                "Muayyad Saleh Alsadi <alsadi@ojuba.org>",
                                "Ehab El-Gedawy <ehabsas@gmail.com>",
                                "Mahyuddin Susanto <udienz@ubuntu.com>",
                                "عبدالرحيم دوبيلار <abdulrahiem@sabi.li>",
                                "أحمد المحمودي (Ahmed El-Mahmoudy) <aelmahmoudy@sabily.org>"])
  def save_auto_start(self):
    b=self.conf_dlg.auto_start.get_active()
    if b and os.path.exists(self.skip_auto_fn):
      try: os.unlink(self.skip_auto_fn)
      except OSError: pass
    elif not b:
      open(self.skip_auto_fn,'wt').close()
  
  def update_prayer(self):
    if not self.prayer_items: return
    pt=self.prayer.get_prayers()
    j=0
    ptn=list(self.ptnames)
    ptn[1]=''
    for p,t in zip(ptn, pt):
      if not p: continue
      i = gtk.MenuItem
      self.prayer_items[j].set_label(u"%-10s %s" % (p, t.format(),))
      j+=1
  
  def init_menu(self):
    self.menu = gtk.Menu()
    i = gtk.ImageMenuItem(gtk.STOCK_COPY)
    i.set_always_show_image(True)
    i.connect('activate', self.copy_cb)
    self.menu.add(i)

    i = gtk.ImageMenuItem(gtk.STOCK_GO_FORWARD)
    i.set_always_show_image(True)
    i.connect('activate', self.next_cb)
    self.menu.add(i)

    i = gtk.ImageMenuItem(gtk.STOCK_GO_BACK)
    i.set_always_show_image(True)
    i.connect('activate', self.prev_cb)
    self.menu.add(i)

    self.menu.add(gtk.SeparatorMenuItem())

    self.prayer_items=[]
    for j in range(5):
      i = gtk.MenuItem("-")
      self.prayer_items.append(i)
      self.menu.add(i)
    self.update_prayer()

    self.menu.add(gtk.SeparatorMenuItem())
    
    i = gtk.MenuItem(_("Configure"))
    i.connect('activate', self.config_cb)
    self.menu.add(i)
    
    self.menu.add(gtk.SeparatorMenuItem())

    i = gtk.ImageMenuItem(gtk.STOCK_ABOUT)
    i.set_always_show_image(True)
    i.connect('activate', lambda *args: self.about_dlg.run())
    self.menu.add(i)
    
    i = gtk.ImageMenuItem(gtk.STOCK_QUIT)
    i.set_always_show_image(True)
    i.connect('activate', gtk.main_quit)
    self.menu.add(i)

    self.menu.show_all()

  def popup_cb(self, s, button, time):
    self.menu.popup(None, None, gtk.status_icon_position_menu, button, time, s)

  def time_set_cb(self, m, t):
    self.conf['minutes']=t
    self.minutes_counter=1
    self.save_conf()

  def lang_cb(self, m, l):
    if not m.get_active(): return
    self.m.set_lang(l)
    self.save_conf()

  def notify_cb(self,notify,action):
    try: self.notify.close()
    except glib.GError: pass
    if action=="exit": gtk.main_quit()
    elif action=="copy": self.copy_cb()
    elif action=="next": self.next_cb()
    elif action=="previous": self.prev_cb()

def applet_main():
  gtk.window_set_default_icon_name('monajat')
  a=applet()
  init_dbus(a.dbus_cb)
  gtk.main()

if __name__ == "__main__":
  applet_main()

