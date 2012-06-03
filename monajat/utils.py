# -*- coding: utf-8 -*-
# -*- Mode: Python; py-indent-offset: 4 -*-
import sys
bus, bus_name, bus_object=None,None,None
try:
    import dbus
    import dbus.service
    from dbus.mainloop.glib import DBusGMainLoop

    dbus_loop = DBusGMainLoop(set_as_default=True)
    bus = dbus.SessionBus()
except ImportError: pass

def init_dbus(cb, interface="org.ojuba.Monajat"):
    global bus_name, bus_object
    if not bus: return
    class Manager(dbus.service.Object):
        def __init__(self, cb, bus, path):
                    dbus.service.Object.__init__(self,bus,path)
                    self.cb=cb

        @dbus.service.method(interface, in_signature='as', out_signature='i')
        def call(self,a):
            return self.cb()

    # values from /usr/include/dbus-1.0/dbus/dbus-shared.h
    r=bus.request_name(interface, flags=0x4)
    if r!=1:
        print "Another process own this service, pass request to it: "
        trials=0; appletbus=False
        while(appletbus==False and trials<20):
            print ".",
            try:
                appletbus=bus.get_object(interface,"/Manager"); break
            except:
                appletbus=False
            time.sleep(1); trials+=1
        print "*"
        if appletbus: exit(appletbus.call(sys.argv[1:],dbus_interface=interface))
        else: print "unable to connect"
        exit(-1)
    bus_name = dbus.service.BusName(interface, bus)
    bus_object = Manager(cb, bus, '/Manager')

