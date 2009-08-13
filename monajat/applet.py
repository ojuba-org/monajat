# -*- coding: utf-8 -*-
import os, os.path
from monajat import Monajat
from utils import init_dbus
import gettext

import glib
import gtk
import pynotify
import cgi

class applet(object):
  def __init__(self):
    self.__minutes_counter=0
    self.__minutes=10
    self.__m=Monajat() # you may pass width like 20 chars
    ld=os.path.join(self.__m.get_prefix(),'..','locale')
    gettext.install('monajat', ld, unicode=0)
    self.__clip1=gtk.Clipboard(selection="CLIPBOARD")
    self.__clip2=gtk.Clipboard(selection="PRIMARY")
    self.__init_about_dialog()
    self.__init_menu()
    self.__s=gtk.status_icon_new_from_file(os.path.join(self.__m.get_prefix(),'monajat.svg'))
    self.__s.connect('popup-menu',self.__popup_cb)
    self.__s.connect('activate',self.__next_cb)
    pynotify.init('MonajatApplet')
    self.__notifycaps = pynotify.get_server_caps ()
    self.__notify=pynotify.Notification("MonajatApplet")
    self.__notify.attach_to_status_icon(self.__s)
    self.__notify.set_property('icon-name','monajat')
    self.__notify.set_property('summary', _("Monajat") )
    if 'actions' in self.__notifycaps:
      self.__notify.add_action("previous", _("previous"), self.__notify_cb)
      self.__notify.add_action("next", _("next"), self.__notify_cb)
      self.__notify.add_action("copy", _("copy"), self.__notify_cb)
    #self.__notify.set_timeout(60)
    glib.timeout_add_seconds(10, self.__start_timer)
  
  def __start_timer(self, *args):
    glib.timeout_add_seconds(60, self.__timed_cb)
    self.__next_cb()
    return False

  def __timed_cb(self, *args):
    if not self.__minutes: return True
    if self.__minutes_counter % self.__minutes == 0:
      self.__minutes_counter=1
      self.__next_cb()
    else:
      self.__minutes_counter+=1
    return True

  def __hide_cb(self, w, *args): w.hide(); return True

  def __render_body(self, m):
    merits=m['merits']
    if not self.__show_merits.get_active(): merits=None
    if "body-markup" in self.__notifycaps:
      body=cgi.escape(m['text'])
      if merits: body+="""\n\n<b>%s</b>: %s""" % (_("Its Merits"),cgi.escape(merits))
    else:
      body=m['text']
      if merits: body+="""\n\n** %s **: %s""" % (_("Its Merits"),merits)
    
    if "body-hyperlinks" in self.__notifycaps:
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
    self.__notify.set_property('body', body)
  def dbus_cb(self, *args):
    self.__minutes_counter=1
    self.__next_cb()
    return 0

  def __next_cb(self,*args):
    try: self.__notify.close()
    except glib.GError: pass
    self.__render_body(self.__m.get())
    self.__notify.show()
    return True

  def __prev_cb(self, *args):
    try: self.__notify.close()
    except glib.GError: pass
    self.__render_body(self.__m.go_back())
    self.__notify.show()

  def __copy_cb(self,*args):
    r=self.__m.get_last_one()
    self.__clip1.set_text(r['text'])
    self.__clip2.set_text(r['text'])

  def __init_about_dialog(self):
    # FIXME: please add more the authors
    self.about_dlg=gtk.AboutDialog()
    self.about_dlg.set_default_response(gtk.RESPONSE_CLOSE)
    self.about_dlg.connect('delete-event', self.__hide_cb)
    self.about_dlg.connect('response', self.__hide_cb)
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
                                "Mahyuddin Susanto <udienz@ubuntu.com>",
                                "عبدالرحيم دوبيلار <abdulrahiem@sabi.li>",
                                "أحمد المحمودي (Ahmed El-Mahmoudy) <aelmahmoudy@sabily.org>"])

  def __init_menu(self):
    self.__menu = gtk.Menu()
    i = gtk.ImageMenuItem(gtk.STOCK_COPY)
    i.connect('activate', self.__copy_cb)
    self.__menu.add(i)

    i = gtk.ImageMenuItem(gtk.STOCK_GO_FORWARD)
    i.connect('activate', self.__next_cb)
    self.__menu.add(i)

    i = gtk.ImageMenuItem(gtk.STOCK_GO_BACK)
    i.connect('activate', self.__prev_cb)
    self.__menu.add(i)

    self.__menu.add(gtk.SeparatorMenuItem())

    self.__show_merits = gtk.CheckMenuItem(_("Show merits"))
    self.__show_merits.set_active(True)
    self.__menu.add(self.__show_merits)

    self.__lang_menu = gtk.Menu()
    i=None
    for j in self.__m.langs:
      i= gtk.RadioMenuItem(i, j)
      i.set_active(self.__m.lang==j)
      i.connect('activate', self.__lang_cb, j)
      self.__lang_menu.add(i)
    
    i= gtk.MenuItem(_("Language"))
    i.set_submenu(self.__lang_menu)
    self.__menu.add(i)

    self.__time_menu = gtk.Menu()
    i=None
    for j in range(0,31,5):
      i= gtk.RadioMenuItem(i, str(j))
      i.set_active(self.__minutes ==j)
      i.connect('activate', self.__time_set_cb, j)
      self.__time_menu.add(i)

    i= gtk.MenuItem(_("Time in minutes"))
    i.set_submenu(self.__time_menu)
    self.__menu.add(i)


    self.__menu.add(gtk.SeparatorMenuItem())
    i = gtk.ImageMenuItem(gtk.STOCK_ABOUT)
    i.connect('activate', lambda *args: self.about_dlg.run())
    self.__menu.add(i)
    
    i = gtk.ImageMenuItem(gtk.STOCK_QUIT)
    i.connect('activate', gtk.main_quit)
    self.__menu.add(i)

    self.__menu.show_all()

  def __popup_cb(self, s, button, time):
    self.__menu.popup(None, None, gtk.status_icon_position_menu, button, time, s)

  def __time_set_cb(self, m, t):
    self.__minutes=t
    self.__minutes_counter=1

  def __lang_cb(self, m, l):
    self.__m.set_lang(l)

  def __notify_cb(self,notify,action):
    try: self.__notify.close()
    except glib.GError: pass
    if action=="exit": gtk.main_quit()
    elif action=="copy": self.__copy_cb()
    elif action=="next": self.__next_cb()
    elif action=="previous": self.__prev_cb()

def applet_main():
  a=applet()
  init_dbus(a.dbus_cb)
  gtk.main()

if __name__ == "__main__":
  applet_main()

