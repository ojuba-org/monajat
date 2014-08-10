# -*- coding: utf-8 -*-
# -*- Mode: Python; py-indent-offset: 4 -*-
import os, os.path
import itl
from monajat import Monajat
from utils import init_dbus
import locale, gettext
import re

from gi.repository import Gtk, Gdk, Notify, Gst, GObject
import cgi
import math
import json
import time

# in gnome3 ['actions', 'action-icons', 'body', 'body-markup', 'icon-static', 'persistence']
# in gnome2 ['actions', 'body', 'body-hyperlinks', 'body-markup', 'icon-static', 'sound']
# "resident"

class SoundPlayer(object):
    def __init__(self, fn = "", change_play_status = None):
        """ SoundPlayer Using gst """
        self.fn = fn
        self.change_play_status = change_play_status
        Gst.init_check(None)
        self.gst_player = Gst.ElementFactory.make("playbin", "Ojuba-SoundPlayer")
        self.gst_player.set_property("uri", "file://" + fn)
        bus = self.gst_player.get_bus()
        bus.add_signal_watch()
        #bus.connect("message", self.on_message)
        bus.connect('message::eos', self.on_message)
        bus.connect('message::error', self.on_message)
        
    def play(self):
        fn = self.fn
        if fn and os.path.isfile(fn):
            self.gst_player.set_state(Gst.State.PLAYING)
    
    def stop(self):
        self.gst_player.set_state(Gst.State.NULL)
    
    def set_filename(self,fn):
        if not fn or not os.path.isfile(fn):
            return
        self.fn = fn
        self.gst_player.set_property("uri", "file://" + fn)
        
    def on_message(self, bus, message):
        if message:
            print message
        self.gst_player.set_state(Gst.State.NULL)

normalize_tb = {
65: 97, 66: 98, 67: 99, 68: 100, 69: 101, 70: 102, 71: 103, 72: 104, 73: 105, 74: 106, 75: 107, 76: 108, 77: 109, 78: 110, 79: 111, 80: 112, 81: 113, 82: 114, 83: 115, 84: 116, 85: 117, 86: 118, 87: 119, 88: 120, 89: 121, 90: 122,
1600: None, 1569: 1575, 1570: 1575, 1571: 1575, 1572: 1575, 1573: 1575, 1574: 1575,
1577: 1607, # teh marboota ->    haa
1611: None, 1612: None, 1613: None, 1614: None, 1615: None, 1616: None, 1617: None, 1618: None, 1609: 1575}

def to_uincode(Str):
    try:
        Str = str(Str)
    except UnicodeEncodeError:
        pass
    if type(Str) == unicode:
        return Str.translate(normalize_tb)
    else:
        return Str.decode('utf-8').translate(normalize_tb)
        
class ConfigDlg(Gtk.Dialog):
    def __init__(self, applet):
        Gtk.Dialog.__init__(self)
        self.applet = applet
        self.m = applet.m
        self.cities_ls = self.get_cities()
        #self.set_size_request(300,400)
        self.set_resizable(False) # FIXME: reconsider this
        self.connect('delete-event', lambda w,*a: w.hide() or True)
        self.connect('response', lambda w,*a: w.hide() or True)
        self.set_title(_('Monajat Configuration'))
        self.add_button(_('Cancel'), Gtk.ResponseType.CANCEL)
        self.add_button(_('Save'), Gtk.ResponseType.OK)
        tabs = Gtk.Notebook()
        tabs.set_size_request(-1,350)
        self.get_content_area().add(tabs)
        vb = Gtk.VBox(False, 2)
        tabs.append_page(vb, Gtk.Label(_('Generic')))
        self.auto_start = b = Gtk.CheckButton(_("Auto start"))
        self.auto_start.set_active(not os.path.exists(self.applet.skip_auto_fn))
        vb.pack_start(b, False, False, 2)
        self.show_merits = b = Gtk.CheckButton(_("Show merits"))
        self.show_merits.set_active(self.applet.conf['show_merits'])
        vb.pack_start(b, False, False, 2)
        self.daylight_savings_time = b = Gtk.CheckButton(_("daylight_savings_time"))
        self.daylight_savings_time.set_active(self.applet.conf['daylight_savings_time'])
        vb.pack_start(b, False, False, 2)        
        hb = Gtk.HBox()
        vb.pack_start(hb, False, False, 2)
        hb.pack_start(Gtk.Label(_('method:')), False, False, 2)
        self.pt_method = b = Gtk.ComboBoxText.new()
        hb.pack_end(b, False, False, 2)
        b.append_text("none. Set to default")
        b.append_text("Egyptian General Authority of Survey")
        b.append_text("University of Islamic Sciences, Karachi (Shaf'i)")
        b.append_text("University of Islamic Sciences, Karachi (Hanafi)")
        b.append_text("Islamic Society of North America")
        b.append_text("Muslim World League (MWL)")
        b.append_text("Umm Al-Qurra, Saudi Arabia")
        b.append_text("Fixed Ishaa Interval (always 90)")
        b.append_text("Egyptian General Authority of Survey (Egypt)")
        b.set_active(self.applet.conf['pt_method'])      
        hb = Gtk.HBox()
        vb.pack_start(hb, False, False, 2)
        hb.pack_start(Gtk.Label(_('Language:')), False, False, 2)
        self.lang = b = Gtk.ComboBoxText.new()
        hb.pack_end(b, False, False, 2)
        selected = 0
        for i,j in enumerate(self.applet.m.langs):
            b.append_text(j)
            if self.m.lang == j:
                selected=i
        b.set_active(selected)
        
        hb = Gtk.HBox()
        vb.pack_start(hb, False, False, 2)
        hb.pack_start(Gtk.Label(_('Time:')), False, False, 2)
        hb.pack_start(Gtk.HBox(), True, True, 2)
        adj = Gtk.Adjustment(5, 0, 90, 5, 5)
        self.timeout = b = Gtk.SpinButton()
        b.set_adjustment(adj)
        b.set_value(self.applet.conf['minutes'])
        hb.pack_start(b, False, False, 2)
        hb.pack_start(Gtk.Label(_('minutes')), False, False, 2)

        vb = Gtk.VBox(False, 2)
        tabs.append_page(vb, Gtk.Label(_('Location')))
        
        hb = Gtk.HBox()
        hb.pack_start(Gtk.Label(_('Current city:')), False, False, 2)
        vb.pack_start(hb, False, False, 6)
        hb = Gtk.HBox()
        vb.pack_start(hb, False, False, 2)
        # read cuurent city full name
        c = self.get_city('id', self.applet.conf['city_id'])
        if c:
            c = c[0]
            self.user_city = c['name']
        else:
            c = {}
            c['country'] = _('Please, Secify your city')
            c['state'] = ''
            c['name'] = ''
            c['locale_name'] = ''
            self.user_city = 'Makka'
        # set locale_name='' instead of None
        c['locale_name'] = c['locale_name'] or ''
        cl = '%(country)s - %(state)s - %(name)s %(locale_name)s' % c
        self.cur_city_l = l = Gtk.Entry()
        l.set_editable(False)
        l.set_text(cl)
        hb.pack_start(l, True, True, 2)
        
        hb = Gtk.HBox()
        hb.pack_start(Gtk.Label(_('Change city:')), False, False, 2)
        vb.pack_start(hb, False, False, 8)
        self.Search_e = e = Gtk.Entry()
        e.connect('activate', self._city_search_cb)
        hb.pack_start(e, True, True, 2)
        
        s = Gtk.TreeStore(str, bool, int, str) # label, is_city, id, normalized label
        self.cities_tree = tree = Gtk.TreeView(s)
        col = Gtk.TreeViewColumn('Location', Gtk.CellRendererText(), text=0)
        col.set_sizing(Gtk.TreeViewColumnSizing.AUTOSIZE)
        tree.insert_column(col, -1)
        tree.set_enable_search(True)
        tree.set_search_column(3)
        tree.set_headers_visible(False)
        tree.set_tooltip_column(0)
        
        scroll = Gtk.ScrolledWindow()
        scroll.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.ALWAYS)
        scroll.add(tree)
        vb.pack_start(scroll, True, True, 2)
        self.sound_player = SoundPlayer(self.applet.conf['athan_media_file'],
                                        self.change_play_status)

        vb = Gtk.VBox(False, 2)
        tabs.append_page(vb, Gtk.Label(_('Edit_pt')))
        
        self.Edit_pt = b = Gtk.CheckButton(_("Edit_pt"))
        self.Edit_pt.set_active(self.applet.conf['Edit_pt'])
        vb.pack_start(b, False, False, 2)

        hb = Gtk.HBox()
        vb.pack_start(hb, False, False, 2)
        hb.pack_start(Gtk.Label(_('Fajr')), False, False, 2)
        hb.pack_start(Gtk.HBox(), True, True, 2)
        adj = Gtk.Adjustment(5, -60, 60, 1, 5)
        self.Fajr_min = b = Gtk.SpinButton()
        b.set_adjustment(adj)
        b.set_value(self.applet.conf['Fajr_minutes'])
        hb.pack_start(b, False, False, 2)
        hb.pack_start(Gtk.Label(_('minutes')), False, False, 2)
        
        hb = Gtk.HBox()
        vb.pack_start(hb, False, False, 2)
        hb.pack_start(Gtk.Label(_('Sunrise')), False, False, 2)
        hb.pack_start(Gtk.HBox(), True, True, 2)
        adj = Gtk.Adjustment(5, -60, 60, 1, 5)
        self.Shrooq_min = b = Gtk.SpinButton()
        b.set_adjustment(adj)
        b.set_value(self.applet.conf['Shrooq_minutes'])
        hb.pack_start(b, False, False, 2)
        hb.pack_start(Gtk.Label(_('minutes')), False, False, 2)
        
        hb = Gtk.HBox()
        vb.pack_start(hb, False, False, 2)
        hb.pack_start(Gtk.Label(_('Dhuhr')), False, False, 2)
        hb.pack_start(Gtk.HBox(), True, True, 2)
        adj = Gtk.Adjustment(5, -60, 60, 1, 5)
        self.Zuhr_min = b = Gtk.SpinButton()
        b.set_adjustment(adj)
        b.set_value(self.applet.conf['Zuhr_minutes'])
        hb.pack_start(b, False, False, 2)
        hb.pack_start(Gtk.Label(_('minutes')), False, False, 2)
        
        hb = Gtk.HBox()
        vb.pack_start(hb, False, False, 2)
        hb.pack_start(Gtk.Label(_('Asr')), False, False, 2)
        hb.pack_start(Gtk.HBox(), True, True, 2)
        adj = Gtk.Adjustment(5, -60, 60, 1, 5)
        self.Asr_min = b = Gtk.SpinButton()
        b.set_adjustment(adj)
        b.set_value(self.applet.conf['Asr_minutes'])
        hb.pack_start(b, False, False, 2)
        hb.pack_start(Gtk.Label(_('minutes')), False, False, 2)
        
        hb = Gtk.HBox()
        vb.pack_start(hb, False, False, 2)
        hb.pack_start(Gtk.Label(_('Maghrib')), False, False, 2)
        hb.pack_start(Gtk.HBox(), True, True, 2)
        adj = Gtk.Adjustment(5, -60, 60, 1, 5)
        self.Maghrib_min = b = Gtk.SpinButton()
        b.set_adjustment(adj)
        b.set_value(self.applet.conf['Maghrib_minutes'])
        hb.pack_start(b, False, False, 2)
        hb.pack_start(Gtk.Label(_('minutes')), False, False, 2)
        
        hb = Gtk.HBox()
        vb.pack_start(hb, False, False, 2)
        hb.pack_start(Gtk.Label(_("Isha'a")), False, False, 2)
        hb.pack_start(Gtk.HBox(), True, True, 2)
        adj = Gtk.Adjustment(5, -60, 60, 1, 5)
        self.Ishaa_min = b = Gtk.SpinButton()
        b.set_adjustment(adj)
        b.set_value(self.applet.conf['Ishaa_minutes'])
        hb.pack_start(b, False, False, 2)
        hb.pack_start(Gtk.Label(_('minutes')), False, False, 2)
        
        hb = Gtk.HBox()
        vb.pack_start(hb, False, False, 2)
        self.clear = cb = Gtk.Button(_('Clear'))
        cb.connect('clicked', self.clear_pt_changes)
        hb.pack_end(cb, False, False, 2)

        vb = Gtk.VBox(False, 2)
        tabs.append_page(vb, Gtk.Label(_('Notification')))
        hb = Gtk.HBox()
        vb.pack_start(hb, False, True, 3)
        hb.pack_start(Gtk.Label(_('Sound:')), False, True, 2)
        self.sound_file = b = Gtk.FileChooserButton(_('Choose Athan media file'))
        
        if os.path.isfile(self.applet.conf['athan_media_file']):
            self.sound_file.set_filename(self.applet.conf['athan_media_file'])
        ff = Gtk.FileFilter()
        ff.set_name(_('Sound Files'))
        ff.add_pattern('*.ogg')
        ff.add_pattern('*.mp3')
        b.add_filter(ff)
        ff = Gtk.FileFilter()
        ff.set_name(_('All files'))
        ff.add_pattern('*')
        b.add_filter(ff)
        self.play_b = pb = Gtk.Button(_('Play'))
        pb.connect('clicked', self.play_cb)
        hb.pack_end(pb, False, False, 2)
        hb.pack_end(b, True, True, 5)
        
        hb = Gtk.HBox()
        vb.pack_start(hb, False, False, 3)
        self.notify_before_b = b = Gtk.CheckButton(_("Notify before"))
        adj = Gtk.Adjustment(5, 5, 20, 5, 5)
        self.notify_before_t = t = Gtk.SpinButton()
        t.set_adjustment(adj)
        b.set_active(self.applet.conf['notify_before_min'] != 0)
        t.set_value(self.applet.conf['notify_before_min'])
        hb.pack_start(b,True,True,2)
        hb.pack_start(t,False,False,2)
        hb.pack_start(Gtk.Label(_('minutes')),False,False,2)
        self._city_search_cb(self.Search_e, self.user_city)
        #self._fill_cities()

    def clear_pt_changes(self, b):
        self.Fajr_min.set_value(0)
        self.Shrooq_min.set_value(0)
        self.Zuhr_min.set_value(0)
        self.Asr_min.set_value(0)
        self.Maghrib_min.set_value(0)
        self.Ishaa_min.set_value(0)           
        
    def change_play_status(self, status = None):
        if status == None:
            status = self.sound_player.gst_player.get_state()
        if status == Gst.State.PLAYING:
            self.sound_file.set_sensitive(False)
            self.play_b.set_property('label', _('Stop'))
        else:
            self.sound_file.set_sensitive(True)
            self.play_b.set_property('label', _('Play'))

    def play_cb(self, b):
        fn = self.sound_file.get_filename()
        if not fn:
            fn = ''
        if b.get_label() == _('Play'):
            if not os.path.isfile(fn):
                return
            self.change_play_status(Gst.State.PLAYING)
            self.sound_player.set_filename(fn)
            self.sound_player.play()
        else:
            self.change_play_status(Gst.State.NULL)
            self.sound_player.stop()

    def get_cities(self):
        rows = self.m.cities_c.execute('SELECT * FROM cities')
        rows = map(lambda a: dict(a), rows.fetchall())
        return rows
        
    def get_city(self, f='id', v=''):
        '''
            filter self.cities_ls
        '''
        return filter(lambda a: a[f] == v, self.cities_ls)
        
    def _city_search_cb(self, e, v = None):
        e.modify_fg(Gtk.StateType.NORMAL, None)
        if v:
            txt = v
        else:
            txt = e.get_text().strip().lower()
        txt = to_uincode(txt)
        if self.user_city == txt:
            self._search_cb(txt)
            return
        else:
            self.user_city = txt
        rows = filter(lambda a: txt in str(a['name']).lower() or \
                                txt in to_uincode(a['locale_name']) or \
                                txt in str(a['state']).lower() or \
                                txt in str(a['country']).lower(), self.cities_ls)
       
        country, country_i = None, None
        state, state_i = None, None
        city_path = None
        s = self.cities_tree.get_model()
        s.clear()
        for r in rows:
            #r = dict(R)
            if country != r['country']:
                country_i = s.append(None,
                                     (r['country'],
                                     False,
                                     0,
                                     r['country'].lower().translate(normalize_tb)))
            if state != r['state']:
                state_i = s.append(country_i,(r['state'],
                                   False,
                                   0,
                                   r['state'].lower().translate(normalize_tb)))
            country = r['country']
            state = r['state']
            if r['locale_name']:
                city = u'%s - %s' % (r['name'], r['locale_name'])
            else:
                city = r['name']
            city_i = s.append(state_i,(city,
                                      True,
                                      r['id'],
                                      city.lower().translate(normalize_tb)))
        self._search_cb(txt)
    
    def _search_cb(self, txt):
        # FIXME: if same as last successful search text don't update first_match_path
        # FIXME: and if self.city_found same as first_match_path highlight in red
        # we can use self.search_last_path to fix search
        if type(txt) == unicode:
            txt = txt.encode('utf-8')
        e = self.Search_e
        e.modify_fg(Gtk.StateType.NORMAL, None)
        tree = self.cities_tree
        store, p = tree.get_selection().get_selected_rows()
        if p:
            current = p[0]
        else:
            current = None
        limit = None
        def tree_walk_cb(model, path, i, *a):
            if current and path <= current:
                return False
            if limit and path >= limit:
                return True
            f = txt in store.get_value(i, 3)
            if f:
                tree.expand_to_path(path)
                tree.scroll_to_cell(path)
                tree.get_selection().select_iter(i)
                self.city_found = path
                return True
        self.city_found = None
        store.foreach(tree_walk_cb, tree)
        if not self.city_found:
            limit = current
            current = None
            store.foreach(tree_walk_cb, tree)
            if not self.city_found:
                e.modify_fg(Gtk.StateType.NORMAL, Gdk.color_parse("#FF0000"))
                
    def _fill_cities(self):
        # FIXME: rerwite one fuction for fill cities and search, to reduce time
        tree = self.cities_tree
        s = tree.get_model()
        rows = self.m.cities_c.execute('SELECT * FROM cities')
        country, country_i = None, None
        state, state_i = None, None
        city_path = None
        for R in rows:
            r = dict(R)
            if country != r['country']:
                country_i = s.append(None,
                                     (r['country'],
                                     False,
                                     0,
                                     r['country'].lower().translate(normalize_tb)))
            if state != r['state']:
                state_i = s.append(country_i,(r['state'],
                                   False,
                                   0,
                                   r['state'].lower().translate(normalize_tb)))
            country = r['country']
            state = r['state']
            if r['locale_name']:
                city=u'%s - %s' % (r['name'], r['locale_name'])
            else:
                city=r['name']
            city_i = s.append(state_i,(city,
                                      True,
                                      r['id'],
                                      city.lower().translate(normalize_tb)))
            if self.applet.conf.get('city_id',None) == r['id']:
                city_path = s.get_path(city_i)
        if city_path:
            tree.expand_to_path(city_path)
            tree.get_selection().select_path(city_path)
            tree.scroll_to_cell(city_path)

    def run(self, *a, **kw):
        self.auto_start.set_active(not os.path.exists(self.applet.skip_auto_fn))
        return Gtk.Dialog.run(self, *a, **kw)

class applet(object):
    locale_re = re.compile('^[a-z]+_[A-Z]+$', re.I)
    skip_auto_fn = os.path.expanduser('~/.monajat-applet-skip-auto')
    
    def _init_locale(self, lang):
        try:
            l = locale.setlocale(locale.LC_MESSAGES, (lang, 'UTF-8'))
        except:
            pass
        else:
            if l:
                os.environ['LC_MESSAGES'] = l
            return
        for l in locale.locale_alias.keys():
            if not l.startswith(lang+'_') or not self.locale_re.match(l):
                continue
            l, c = l.split('_',1)
            l = l + "_" + c.upper() + ".UTF-8"
            try:
                locale.setlocale(locale.LC_MESSAGES, l)
            except locale.Error:
                pass
            else:
                os.environ['LC_MESSAGES'] = l
                return

    def __init__(self):
        self.conf_dlg = None
        self.chngbody = time.time()
        self.minutes_counter = 0
        self.m = Monajat() # you may pass width like 20 chars
        self.sound_player = SoundPlayer()
        self.load_conf()
        self.prayer_items = []
        kw = self.conf_to_prayer_args()
        self.prayer = itl.PrayerTimes(**kw)
        
        self.prayer.method.extreme=int(self.conf['pt_method'])
        self.prayer.method.offset=self.conf['Edit_pt']
        if self.conf['Edit_pt'] == 1:
            self.prayer.method.offList[0]=self.conf['Fajr_minutes']
            self.prayer.method.offList[1]=self.conf['Shrooq_minutes']
            self.prayer.method.offList[2]=self.conf['Zuhr_minutes']
            self.prayer.method.offList[3]=self.conf['Asr_minutes']
            self.prayer.method.offList[4]=self.conf['Maghrib_minutes']
            self.prayer.method.offList[5]=self.conf['Ishaa_minutes']

        self._init_locale(self.m.lang)
        ld = os.path.join(self.m.get_prefix(), '..', 'locale')
        gettext.install('monajat', ld, unicode=0)
        self.ptnames = [_("Fajr"),
                        _("Sunrise"),
                        _("Dhuhr"),
                        _("Asr"),
                        _("Maghrib"),
                        _("Isha'a")]
        self.clip1 = Gtk.Clipboard.get(Gdk.SELECTION_CLIPBOARD)
        self.clip2 = Gtk.Clipboard.get(Gdk.SELECTION_PRIMARY)
        self.init_menu()
        

        self.statusicon = Gtk.StatusIcon ()
        self.statusicon.connect('popup-menu',self.popup_cb)
        self.statusicon.connect('activate',self.next_cb)
        self.statusicon.set_title(_("Monajat"))
        self.statusicon.set_from_file(os.path.join(self.m.get_prefix(),'monajat.svg'))
        
        Notify.init(_("Monajat"))
        self.init_notify_cb()
        print self.notifycaps
        
        self.notif_last_athan = -1
        self.next_athan_delta = -1
        self.next_athan_i = -1
        self.last_athan = -1
        self.last_time = 0
        self.first_notif_done = False
        self.start_time = time.time()
        GObject.timeout_add(1, self.timer_cb)

    def init_notify_cb(self):
        self.notifycaps = Notify.get_server_caps ()
        self.notify = Notify.Notification()
        self.notify.set_property('icon-name', os.path.join(self.m.get_prefix(),'monajat.svg'))
        self.notify.set_property('summary', _("Monajat") )
        if 'actions' in self.notifycaps:
            self.notify.add_action("previous", _("Back"), self.notify_cb, None)
            self.notify.add_action("next", _("Forward"), self.notify_cb, None)
            self.notify.add_action("copy", _("copy"), self.notify_cb, None)
        
    def show_notify_cb(self, body, *args):
        self.notify.set_property('body', body )
        self.notify.show()
        
    def config_cb(self, *a):
        if self.conf_dlg == None:
            self.conf_dlg = ConfigDlg(self)
            self.conf_dlg.show_all()
        r = self.conf_dlg.run()
        if r == Gtk.ResponseType.OK:
            self.save_auto_start()
            self.save_conf()

    def default_conf(self):
        self.conf = {}
        self.conf['show_merits'] = '1'
        self.conf['daylight_savings_time']='1'
        self.conf['pt_method']='6'
        self.conf['Edit_pt']='0'
        self.conf['Fajr_minutes']='0'
        self.conf['Shrooq_minutes']='0'
        self.conf['Zuhr_minutes']='0'
        self.conf['Asr_minutes']='0'
        self.conf['Maghrib_minutes']='0'
        self.conf['Ishaa_minutes']='0'
        self.conf['lang'] = self.m.lang
        self.conf['minutes'] = '10'
        self.conf['athan_media_file'] = os.path.join(self.m.prefix, 'athan.ogg')
        print self.conf['athan_media_file']
        self.conf['notify_before_min'] = '10'

    def conf_to_prayer_args(self):
        kw = {}
        if not self.conf.has_key('city_id'): return kw
        c = self.m.cities_c
        try:
            c_id = int(self.conf['city_id'])
        except ValueError:
            return kw
        except TypeError:
            return kw
        r = c.execute('SELECT * FROM cities AS c LEFT JOIN dst AS d ON d.i=dst_id WHERE c.id=?', (c_id,)).fetchone()
        # set defaults to Makkah (14244)
        if not r:
            r = c.execute('SELECT * FROM cities AS c LEFT JOIN dst AS d ON d.i=dst_id WHERE c.id=?',
                          (14244,)).fetchone()
        kw = dict(r)
        if "alt" not in kw or not kw["alt"]:
            kw["alt"] = 0.0
        kw["tz"] = kw["utc"]
        # NOTE: get DST from machine local setting
        #kw["dst"] = time.localtime().tm_isdst
        kw["dst"] = self.conf['daylight_savings_time']
        # FIXME: dst should have the following 3 options
        # a. auto from system, b. auto from algorithm, c. specified to 0/1 by user
        #dst=kw["dst_id"]
        #if not dst: kw["dst"]=0
        #else:
        #    # FIXME: add DST logic here
        #    kw["dst"]=1
        print kw
        #lat=21.43, lon=39.77, tz=3.0, dst=0, alt=0, pressure=1010, temp=10
        return kw


    def parse_conf(self, s):
        self.default_conf()
        l1 = map(lambda k: k.split('=',1),
                 filter(lambda j: j,
                 map(lambda i: i.strip(),s.splitlines())) )
        l2 = map(lambda a: (a[0].strip(),a[1].strip()),filter(lambda j: len(j)==2,l1))
        r = dict(l2)
        self.conf.update(dict(l2))
        return len(l1) == len(l2)

    def load_conf(self):
        s = ''
        fn = os.path.expanduser('~/.monajat-applet.rc')
        if os.path.exists(fn):
            try:
                s = open(fn,'rt').read()
            except OSError:
                pass
        self.parse_conf(s)
        if self.conf.has_key('city_id'):
            # make sure city_id is set using the same db
            if not self.conf.has_key('cities_db_ver') \
               or self.conf['cities_db_ver'] != self.m.cities_db_ver:
                   del self.conf['city_id']
            # make sure it's integer
            try:
                c_id = int(self.conf['city_id'])
            except ValueError:
                self.conf['city_id'] =  14244
            except TypeError:
                self.conf['city_id'] = 14244
            else:
                self.conf['city_id'] = c_id
        else:
            # set default to makkah (14244)
            self.conf['city_id'] = 14244
        # set athan media file exists
        self.sound_player.set_filename(self.conf['athan_media_file'])
        # fix types
        try:
            self.conf['minutes'] = math.ceil(float(self.conf['minutes'])/5.0)*5
        except ValueError:
            self.conf['minutes'] = 0
        try:
            self.conf['show_merits'] = int(self.conf['show_merits']) 
        except ValueError:
            self.conf['show_merits'] = 1
        try:
            self.conf['daylight_savings_time'] = int(self.conf['daylight_savings_time']) 
        except ValueError:
            self.conf['daylight_savings_time'] = 1            
        try:
            self.conf['pt_method'] = int(self.conf['pt_method']) 
        except ValueError:
            self.conf['pt_method'] = 6        
        try:
            self.conf['Edit_pt'] = int(self.conf['Edit_pt']) 
        except ValueError:
            self.conf['Edit_pt'] = 0            
        try:
            self.conf['Fajr_minutes'] = int(self.conf['Fajr_minutes']) 
        except ValueError:
            self.conf['Fajr_minutes'] = 0            
        try:
            self.conf['Shrooq_minutes'] = int(self.conf['Shrooq_minutes']) 
        except ValueError:
            self.conf['Shrooq_minutes'] = 0            
        try:
            self.conf['Zuhr_minutes'] = int(self.conf['Zuhr_minutes']) 
        except ValueError:
            self.conf['Zuhr_minutes'] = 0            
        try:
            self.conf['Asr_minutes'] = int(self.conf['Asr_minutes']) 
        except ValueError:
            self.conf['Asr_minutes'] = 0            
        try:
            self.conf['Maghrib_minutes'] = int(self.conf['Maghrib_minutes']) 
        except ValueError:
            self.conf['Maghrib_minutes'] = 0             
        try:
            self.conf['Ishaa_minutes'] = int(self.conf['Ishaa_minutes']) 
        except ValueError:
            self.conf['Ishaa_minutes'] = 0    
        try:
            self.conf['notify_before_min'] = int(float(self.conf['notify_before_min']))
        except ValueError:
            self.conf['notify_before_min'] = 10
        self.m.set_lang(self.conf['lang'])
        self.m.clear()

    def apply_conf(self):
        kw = self.conf_to_prayer_args()
        self.prayer = itl.PrayerTimes(**kw)

        self.prayer.method.extreme=int(self.conf['pt_method'])
        self.prayer.method.offset=self.conf['Edit_pt']
        if self.conf['Edit_pt'] == 1:
            self.prayer.method.offList[0]=self.conf['Fajr_minutes']
            self.prayer.method.offList[1]=self.conf['Shrooq_minutes']
            self.prayer.method.offList[2]=self.conf['Zuhr_minutes']
            self.prayer.method.offList[3]=self.conf['Asr_minutes']
            self.prayer.method.offList[4]=self.conf['Maghrib_minutes']
            self.prayer.method.offList[5]=self.conf['Ishaa_minutes']

        self.update_prayer()
        self.sound_player.set_filename(self.conf['athan_media_file'])
        self.m.clear()
        self.m.set_lang(self.conf['lang'])
        self.render_body(self.m.go_forward())

    def save_conf(self):
        self.conf['cities_db_ver'] = self.m.cities_db_ver
        self.conf['show_merits'] = int(self.conf_dlg.show_merits.get_active())
        self.conf['daylight_savings_time'] = int(self.conf_dlg.daylight_savings_time.get_active())
        self.conf['pt_method'] = int(self.conf_dlg.pt_method.get_active())
        self.conf['Edit_pt']=int(self.conf_dlg.Edit_pt.get_active())
        self.conf['Fajr_minutes']=int(self.conf_dlg.Fajr_min.get_value())
        self.conf['Shrooq_minutes']=int(self.conf_dlg.Shrooq_min.get_value())
        self.conf['Zuhr_minutes']=int(self.conf_dlg.Zuhr_min.get_value())
        self.conf['Asr_minutes']=int(self.conf_dlg.Asr_min.get_value())
        self.conf['Maghrib_minutes']=int(self.conf_dlg.Maghrib_min.get_value())
        self.conf['Ishaa_minutes']=int(self.conf_dlg.Ishaa_min.get_value())
        self.conf['lang'] = self.conf_dlg.lang.get_active_text()
        self.conf['minutes'] = int(self.conf_dlg.timeout.get_value())
        self.conf['athan_media_file'] = self.conf_dlg.sound_file.get_filename()
        self.conf['notify_before_min'] = int(self.conf_dlg.notify_before_b.get_active() \
                                            and self.conf_dlg.notify_before_t.get_value())
        m, p = self.conf_dlg.cities_tree.get_selection().get_selected_rows()
        if p:
            city_id = m[p[0]][2]
            if city_id:
                self.conf['city_id'] = city_id
        print "** saving conf", self.conf
        fn = os.path.expanduser('~/.monajat-applet.rc')
        s = '\n'.join(map(lambda k: "%s=%s" % (k,str(self.conf[k])), self.conf.keys()))
        try:
            open(fn,'wt').write(s)
        except OSError:
            pass
        self.apply_conf()

    def athan_show_notif(self):
        self.last_time = time.time()
        self.first_notif_done = True
        s = self.ptnames[self.last_athan]
        self.show_notify_cb(_('''It's now time for %s prayer''') % s)
        return True

    def athan_notif_cb(self):
        i, t, dt = self.prayer.get_next_time_stamp()
        if i < 0:
            return False
        dt = max(dt, 0)
        i = i%6
        self.next_athan_delta = dt
        self.next_athan_i = i
        if dt < 30 and i != self.last_athan:
            print "it's time for prayer number:", i
            self.last_athan = i
            self.sound_player.play()
            self.athan_show_notif()
            return True
        return False

    def timer_cb(self, *args):
        if not 'actions' in self.notifycaps:
            self.init_notify_cb()
            print self.notifycaps
        dt = int(time.time()-self.last_time)
        if self.prayer.update():
            self.update_prayer()
        if self.athan_notif_cb(): return True
        if not self.first_notif_done:
            if int(time.time()-self.start_time) >= 10:
                self.next_cb()
            return True
        if self.conf['notify_before_min'] \
           and self.next_athan_delta <= self.conf['notify_before_min']*60 \
           and self.next_athan_i != self.notif_last_athan:
               self.notif_last_athan = self.next_athan_i
               self.next_cb()
        elif self.conf['minutes'] and dt >= self.conf['minutes']*60:
               self.next_cb()
        return True

    def fuzzy_delta(self):
        if self.next_athan_i < 0 :
            return ""
        t = max(int(self.next_athan_delta), 0)
        d = {"prayer" : self.ptnames[self.next_athan_i]}
        d['hours'] = t/3600
        t %= 3600
        d['minutes'] = t/60
        if d["hours"]:
            if d["minutes"] < 5:
                r = _("""%(hours)d hours till %(prayer)s prayer""") % d
            else:
                r = _("""%(hours)d hours and %(minutes)d minutes till %(prayer)s prayer""") % d
        elif d["minutes"] >= 2:
            r = _("""less than %(minutes)d minutes till %(prayer)s prayer""") % d
        else:
            r = _("""less than a minute till %(prayer)s prayer""") % d
        if "body-markup" in self.notifycaps:
            return "<b>%s</b>\n\n" % cgi.escape(r)
        return "%s\n\n" % r

    def body_to_str(self, body):
        if type(body) == unicode:
            return body.encode('utf-8')
        return body
        
    def render_body(self, m):
        merits = m['merits']
        if not self.conf['show_merits']:
            merits = None
        if "body-markup" in self.notifycaps:
            body = cgi.escape(m['text'])
            if merits:
                body = """{}\n\n<b>{}</b>: {}""".format(self.body_to_str(body),
                                                        _("Its Merits"),
                                                        self.body_to_str(cgi.escape(merits)))
        else:
            body = m['text']
            if merits:
                body = """{}\n\n** {} **: {}""".format(self.body_to_str(body),
                                                       _("Its Merits"),
                                                       self.body_to_str(merits))
        if type(body) == unicode:
                body = body.encode('utf-8')
        if "body-hyperlinks" in self.notifycaps:
            L = []
            links = m.get('links',u'').split(u'\n')
            for l in links:
                ll = l.split(u'\t',1)
                url = cgi.escape(ll[0])
                if len(ll) > 1:
                    t = cgi.escape(ll[1])
                else:
                    t = url
                print url, t
                L.append(u"""<a href='{}'>{}</a>""".format(url,t))
            l = u"\n\n".join(L)
            body += self.body_to_str("\n\n" + l)
        # if we are close to time show it before supplication
        if self.next_athan_delta >= 0 and self.next_athan_delta <= 600:
            body = self.fuzzy_delta() + self.body_to_str(body)
        else:
            body = """{}\n\n{}""".format(self.body_to_str(body), self.fuzzy_delta())
            #body = body + "\n\n" + self.fuzzy_delta()
        #timeNP,isnear, istime = self.nextprayer_note(self.get_nextprayer(self.prayer.get_prayers()))
        #if not isnear: body+=timeNP
        #else: body=timeNP+body
        self.show_notify_cb(body)
        return body

    def dbus_cb(self, *args):
        self.minutes_counter = 1
        self.next_cb()
        return 0

    def next_cb(self, *args):
        self.last_time = time.time()
        self.first_notif_done = True
        self.render_body(self.m.go_forward())
        return True

    def prev_cb(self, *args):
        self.first_notif_done = True
        self.render_body(self.m.go_back())
        return True

    def copy_cb(self, *args):
        r = self.m.get_current()
        self.clip1.set_text(r['text'], -1)
        self.clip2.set_text(r['text'], -1)

    def show_about_dialog(self):
        # FIXME: please add more the authors
        dlg = Gtk.AboutDialog()
        dlg.set_default_response(Gtk.ResponseType.CLOSE)
        
        dlg.set_logo_icon_name('monajat')
        try:
            dlg.set_program_name("Monajat")
        except:
            pass
        dlg.set_name(_("Monajat"))
        #dlg.set_version(version)
        dlg.set_copyright("Copyright © 2009 sabily.org")
        dlg.set_comments(_("Monajat supplications"))
        dlg.set_license("""\
        This program is free software; you can redistribute it and/or modify
        it under the terms of the GNU General Public License as published by
        the Free Software Foundation; either version 2 of the License, or
        (at your option) any later version.

        This program is distributed in the hope that it will be useful,
        but WITHOUT ANY WARRANTY; without even the implied warranty of
        MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.    See the
        GNU General Public License for more details.
""")
        dlg.set_website("https://launchpad.net/monajat")
        dlg.set_website_label("Monajat web site")
        dlg.set_authors(["Fadi al-katout <cutout33@gmail.com>",
                                                                "Muayyad Saleh Alsadi <alsadi@ojuba.org>",
                                                                "Ehab El-Gedawy <ehabsas@gmail.com>",
                                                                "Mahyuddin Susanto <udienz@ubuntu.com>",
                                                                "عبدالرحيم دوبيلار <abdulrahiem@sabi.li>",
                                                                "أحمد المحمودي (Ahmed El-Mahmoudy) <aelmahmoudy@sabily.org>"])
        dlg.run()
        dlg.destroy()
        
    def save_auto_start(self):
        b = self.conf_dlg.auto_start.get_active()
        if b and os.path.exists(self.skip_auto_fn):
            try:
                os.unlink(self.skip_auto_fn)
            except OSError:
                pass
        elif not b:
            open(self.skip_auto_fn,'wt').close()
    
    def update_prayer(self):
        if not self.prayer_items: return
        pt = self.prayer.get_prayers()
        j = 0
        ptn = list(self.ptnames)
        #if you want to disable sunrise time showing from the popup menu use the commands in line 952 and 980
        #ptn[1] = ''
        for p,t in zip(ptn, pt):
            if not p: continue
            i = Gtk.MenuItem
            self.prayer_items[j].set_label("{: <15} {}".format(p, t.format(),))
            j += 1
    
    def init_menu(self):
        self.menu = Gtk.Menu()
        i = Gtk.ImageMenuItem.new_from_stock(Gtk.STOCK_COPY, None)
        i.set_always_show_image(True)
        i.connect('activate', self.copy_cb)
        self.menu.add(i)

        i = Gtk.ImageMenuItem.new_from_stock(Gtk.STOCK_GO_FORWARD, None)
        i.set_always_show_image(True)
        i.connect('activate', self.next_cb)
        self.menu.add(i)

        i = Gtk.ImageMenuItem.new_from_stock(Gtk.STOCK_GO_BACK, None)
        i.set_always_show_image(True)
        i.connect('activate', self.prev_cb)
        self.menu.add(i)

        self.menu.add(Gtk.SeparatorMenuItem.new())

        self.prayer_items = []
        #for disabling sunerise time from the popup menu
        #for j in range(5):
        for j in range(6):
            i = Gtk.MenuItem("-")
            self.prayer_items.append(i)
            self.menu.add(i)
        self.update_prayer()

        self.menu.add(Gtk.SeparatorMenuItem.new())
        
        i = Gtk.MenuItem(_("Configure"))
        i.connect('activate', self.config_cb)
        self.menu.add(i)
        
        self.menu.add(Gtk.SeparatorMenuItem.new())

        i = Gtk.ImageMenuItem.new_from_stock(Gtk.STOCK_ABOUT, None)
        i.set_always_show_image(True)
        i.connect('activate', lambda *args: self.show_about_dialog()) 
        self.menu.add(i)
        
        i = Gtk.ImageMenuItem.new_from_stock(Gtk.STOCK_QUIT, None)
        i.set_always_show_image(True)
        i.connect('activate', Gtk.main_quit)
        self.menu.add(i)

        self.menu.show_all()

    def popup_cb(self, s, button, time):

        self.menu.popup(None,
                        None,
                        self.statusicon.position_menu,
                        self.statusicon,
                        3,
                        Gtk.get_current_event_time())


    def time_set_cb(self, m, t):
        self.conf['minutes'] = t
        self.minutes_counter = 1
        self.save_conf()

    def lang_cb(self, m, l):
        if not m.get_active(): return
        self.m.set_lang(l)
        self.save_conf()

    def notify_cb(self, notify, action, *a):
        if action == "exit":
            Gtk.main_quit()
        elif action == "copy":
            self.copy_cb()
        elif action == "next":
            self.next_cb()
        elif action == "previous":
            self.prev_cb()

def applet_main():
    Gtk.Window.set_default_icon_name('monajat')
    a = applet()
    init_dbus(a.dbus_cb)
    Gtk.main()

if __name__ == "__main__":
    applet_main()
