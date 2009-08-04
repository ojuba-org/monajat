# -*- coding: utf-8 -*-
import os, os.path
from monajat import Monajat

import glib
import gtk
import pynotify

class applet(object):
  def __init__(self):
    self.__m=Monajat() # you may pass width like 20 chars
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
    self.__notify.set_property('summary', "Monajat" )
    if 'actions' in self.__notifycaps:
      self.__notify.add_action("previous", "previous", self.__notify_cb)
      self.__notify.add_action("next", "next", self.__notify_cb)
      self.__notify.add_action("copy", "copy", self.__notify_cb)
    #self.__notify.set_timeout(60)
    self.__next_cb()

  def __render_body(self, m):
    self.__notify.set_property('body', "%s" % (m) )
    
  def __hide_cb(self, w, *args): w.hide(); return True

  def __next_cb(self,*args):
    try: self.__notify.close()
    except glib.GError: pass
    self.__notify.set_property('body', "%s" % (self.__m.get()['text']) )
    self.__notify.show()

  def __prev_cb(self, *args):
    try: self.__notify.close()
    except glib.GError: pass
    self.__notify.set_property('body', "%s" % (self.__m.go_back()['text']) )
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
    self.about_dlg.set_name("Monajat")
    #self.about_dlg.set_version(version)
    self.about_dlg.set_copyright("Copyright © 2009 sabily.org")
    self.about_dlg.set_comments("Monajat supplications")
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
    self.about_dlg.set_website("http://git.ojuba.org/cgit/monajat/")
    self.about_dlg.set_website_label("http://git.ojuba.org/cgit/monajat/")
    self.about_dlg.set_authors(["Muayyad Saleh Alsadi <alsadi@ojuba.org>"])

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

    i = gtk.ImageMenuItem(gtk.STOCK_ABOUT)
    i.connect('activate', lambda *args: self.about_dlg.run())
    self.__menu.add(i)
    
    i = gtk.ImageMenuItem(gtk.STOCK_QUIT)
    i.connect('activate', gtk.main_quit)
    self.__menu.add(i)

    self.__menu.show_all()

  def __popup_cb(self, s, button, time):
    self.__menu.popup(None, None, gtk.status_icon_position_menu, button, time, s)

    
  def __notify_cb(self,notify,action):
    try: self.__notify.close()
    except glib.GError: pass
    if action=="exit": gtk.main_quit()
    elif action=="copy": self.__copy_cb()
    elif action=="next": self.__next_cb()
    elif action=="previous": self.__prev_cb()

def applet_main():
  a=applet()
  gtk.main()

if __name__ == "__main__":
  applet_main()

