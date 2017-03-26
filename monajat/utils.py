# -*- Mode: Python; py-indent-offset: 4 -*-
# vim: tabstop=4 shiftwidth=4 expandtab

import dbus
import dbus.bus
import dbus.service
import dbus.mainloop.glib

bus_interface="org.ojuba.Monajat"

    
class OjDBus(dbus.service.Object):
    def __init__ (self, app, bus, path='/', bus_interface="org.ojuba.Monajat"):
        self.app = app()
        dbus.service.Object.__init__ (self, bus, path, bus_interface)
        self.running = True
        
    @dbus.service.method(bus_interface, in_signature='', out_signature='')
    def start (self):
        self.app.dbus_cb()

def setup_dbus(gtk_app, bus_interface="org.ojuba.Monajat"):
    dbus.mainloop.glib.DBusGMainLoop (set_as_default=True)
    bus = dbus.SessionBus ()
    request = bus.request_name (bus_interface, dbus.bus.NAME_FLAG_DO_NOT_QUEUE)
    
    if request != dbus.bus.REQUEST_NAME_REPLY_EXISTS:
        app = OjDBus(gtk_app, bus, '/', bus_interface)
    else:
        print "Exiting: Application already running..."
        object = bus.get_object (bus_interface, "/")
        app = dbus.Interface (object, bus_interface)
        app.start()
        exit(-1)

