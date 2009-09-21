#!/usr/bin/env python

# This application is released under the GNU General Public License 
# v3 (or, at your option, any later version). You can find the full 
# text of the license under http://www.gnu.org/licenses/gpl.txt. 
# By using, editing and/or distributing this software you agree to 
# the terms and conditions of this license. 
# Thank you for using free software!

#  MonajatScreenlet (c) Muayyad Saleh Alsadi <alsadi@ojuba.org>
#  based on ClearRssScreenlet (c) Whise <helder.fraga@hotmail.com>

import gettext

import screenlets
from screenlets.options import StringOption , BoolOption , IntOption , FileOption , DirectoryOption , ListOption , AccountOption , TimeOption , FontOption, ColorOption , ImageOption

import cairo
import pango
import sys
import gtk
import gobject
import os
import cgi

is_manager = screenlets.utils.is_manager_running_me()
try:
	from monajat import monajat
except:
	if not is_manager:
		screenlets.show_message(None,"You don't have monajat installed!\nInstall monajat-python.")
		sys.exit()
	else:
		print "You don't have monajat installed!\nInstall monajat-python."
		sys.exit()

class MonajatScreenlet(screenlets.Screenlet):
	"""Monajat Screenlet for Islamic supplications"""
	
	__name__ = 'MonajatScreenlet'
	__version__ = '0.1'
	__author__ = 'Muayyad Saleh Alsadi <alsadi@ojuba.org>'
	__desc__ = 'Screenlet for periodic Islamic supplications'
	
	#Internals
	__timeout = None
	scrol = 180
	text_x = 10
	text_y = 10
	font = 'Sans 11' # TODO: make it sans
	font_name = font.split(' ')[0]
	rgba_color = (1, 1, 1, 0.9)
	update_interval = 5
	a = ''
	__button_pressed = 1
	p_layout = None
	background_color = (0.65, 0.71, 0.34, 0.8)
	__m=monajat.Monajat() # you may pass width like 20 chars
	lang=__m.lang

	def __init__(self, **keyword_args):
		"""Create a Monajat instance"""
		screenlets.Screenlet.__init__(self, width=200, height=200, 
			uses_theme=True, **keyword_args)
		self.__clip1=gtk.Clipboard(selection="CLIPBOARD")
		self.__clip2=gtk.Clipboard(selection="PRIMARY")
		self.theme_name = "default"
		#self.add_menuitem("next", "next")
		self.add_options_group('Monajat', 'Monajat settings:')
		self.add_option(StringOption('Monajat', 'lang', self.lang, 
			'Language', 'set text language', choices=self.__m.langs)) 
		self.add_option(IntOption('Monajat', 'update_interval', 
			self.update_interval, 'Update interval', 
			'The interval for refreshing Monajat text (in minutes)', min=1, max=60))
		self.add_option(FontOption('Monajat','font', 
			self.font_name, 'Text Font', 
			'Text font'))
		self.add_option(ColorOption('Monajat', 'rgba_color', 
			self.rgba_color, 'Default Color', 
			'The default color of the text ...'))
		self.add_option(ColorOption('Monajat','background_color', 
			self.background_color, 'Back color (only with default theme)', 'only works with default theme'))
		self.update_interval = self.update_interval
		gobject.timeout_add(int(100), self.show_text)
		

	def __setattr__(self, name, value):
		screenlets.Screenlet.__setattr__(self, name, value)
		if name in ('lang','text_x', 'text_y', 'font_name', 
				'rgba_color', 'background_color'):
			if self.window:
				self.redraw_canvas()
		if name == "update_interval":
			if value > 0:
				self.__dict__['update_interval'] = value
				if self.__timeout:
					gobject.source_remove(self.__timeout)
				self.__timeout = gobject.timeout_add(int(value * 60000), self.timer_cb)
			else:
				self.__dict__['update_interval'] = 1
				pass
		if name == 'font': self.font_name = str(value).split(' ')[0]

	def net_menu_cb(self, m, url):
		os.system('xdg-open "%s"' % url)

	def create_net_menu(self):
		mm = gtk.Menu()
		links=self.__m.get_current().get('links',u'').split(u'\n')
		for l in links:
			ll=l.split(u'\t',1)
			url=cgi.escape(ll[0])
			if len(ll)>1: t=cgi.escape(ll[1])
			else: t=url
			i= gtk.MenuItem(t)
			i.connect("activate", self.net_menu_cb,url)
			i.show()
			mm.add(i)
		self.net_menu.set_submenu(mm)

	def on_init (self):
		print "Screenlet has been initialized."
		# add default menuitems
		self.add_default_menuitems(screenlets.DefaultMenuItem.XML)
		self.net_menu=self.add_menuitem('internet', 'More from internet')
		self.create_net_menu()
		self.add_submenuitem('lang', 'Language', self.__m.langs)
		self.add_default_menuitems()
		import locale
		try:
		  os.environ['LANG']=self.lang
		  locale.setlocale(locale.LC_ALL, locale.getdefaultlocale(envvars=('LANG',))[0]+'.UTF-8')
		except locale.Error: pass
		if self.lang!=self.__m.lang:
			self.__m.clear()
			self.__m.set_lang(self.lang)
		ld=os.path.join(self.__m.get_prefix(),'..','locale')
		gettext.install('monajat', ld, unicode=0)
		self.refresh_text()

	def menuitem_callback(self, widget, id):
		screenlets.Screenlet.menuitem_callback(self, widget, id)
		if id in self.__m.langs:
			self.__m.set_lang(id)
			self.lang=id
			self.__m.go_forward()
			self.refresh_text()
		if id=="next":
			if len(self.__m.get_current()['text'])> self.scrol:
				self.scrol = self.scrol + 180
			self.redraw_canvas()
		if id=="prev":
			if self.scrol > 180:
				self.scrol = self.scrol - 180
			self.redraw_canvas()
		if id=="option_changed":
			self.option_changed()
		if id=="copy":
			r=self.__m.get_current()['text']
			self.__clip1.set_text(r)
			self.__clip2.set_text(r)
		if id=="refresh":
			self.refresh_text()
		if id=="prev_item":
			self.scrol = 180
			self.__m.go_back()
			self.refresh_text()
		if id=="next_item":
			self.scrol = 180
			self.__m.go_forward()
			self.refresh_text()

	def on_mouse_down(self, event):
		
		if event.type == gtk.gdk.BUTTON_PRESS:
			return self.detect_button(event.x, event.y)
		else:
			return True
		return False

	def on_mouse_up(self, event):
		# do the active button's action
		if self.__button_pressed:
			if self.__button_pressed == 3:
				if len(self.__m.get_current()['text'])> self.scrol:
					self.scrol = self.scrol + 180
					self.redraw_canvas()
			elif self.__button_pressed == 2:
				self.scrol = 180
				self.redraw_canvas()
			elif self.__button_pressed == 1:
				if self.scrol > 180:
					self.scrol = self.scrol - 180
					self.redraw_canvas()
			elif self.__button_pressed == 4:
				self.scrol = 180
				self.__m.go_forward()
				self.redraw_canvas()
			elif self.__button_pressed == 5:
				r=self.__m.get_current()
				self.__clip1.set_text(r['text'])
				self.__clip2.set_text(r['text'])
			elif self.__button_pressed == 6:
				self.scrol = 180
				self.__m.go_back()
				self.redraw_canvas()

			self.__button_pressed = 0
			self.redraw_canvas()
		return False

	def detect_button(self, x, y):
		x /= (self.scale)
		y /= (self.scale)
		button_det = 0
		if y >= 183 and y <= 196.7:
			if x >= 9 and x <= 62:
				button_det = 4+int((x-9)/18)
			elif x >= 135 and x <= 187:
				button_det = 1+int((x-135)/18)
			print button_det

		self.__button_pressed = button_det
		if button_det:
			self.redraw_canvas()
			return True	# we must return boolean for Screenlet.button_press
		else:
			return False

	def on_draw(self, ctx):
		ctx.scale(self.scale, self.scale)

		ctx.set_operator(cairo.OPERATOR_OVER)
		if self.theme:
			ctx.set_source_rgba(*self.background_color)
			if self.theme_name == 'default':self.draw_rounded_rectangle(ctx,0,0,17,200,200)
			self.theme.render(ctx,'background')
		ctx.save()
		try: name = _("Monajat")
		except NameError: return # gettext is not loaded yet
		self.bidi_dir=pango.ALIGN_CENTER
		#self.bidi_dir=pango.ALIGN_LEFT
		#if self.__m.lang in ['ar','fa']:
		#	self.bidi_dir=pango.ALIGN_RIGHT
		#if gtk.widget_get_default_direction()==gtk.TEXT_DIR_LTR:
		#	self.bidi_dir=pango.ALIGN_LEFT
		#else:
		#	self.bidi_dir=pango.ALIGN_RIGHT
		r=self.__m.get_current()
		self.create_net_menu()
		text = r['text']
		om = '<span font_desc="'+self.font_name+'">'
		cm = '</span>'
		if len(text)> self.scrol:
			self.a = '...&gt;&gt;&gt;'
		else:
			self.a = ''
		self.b = '\n'
		if self.scale > 1 or self.scale <= 0.7:
			self.b =''
		text = self.strip_ml_tags(text)
		ctx.set_source_rgba(*self.rgba_color)
		t = "<b>" + name + "</b>" + "\n" + self.b + text[:self.scrol][self.scrol-180:] + self.a
		self.draw_text(ctx, t , self.text_x, self.text_y, self.font_name, 9.5, (self.width - self.text_x) , self.bidi_dir)
		ctx.fill()
		ctx.restore()
		
	def on_draw_shape(self,ctx):
		ctx.rectangle(0,0,self.width,self.height)
		ctx.fill()
		self.on_draw(ctx)

	def strip_ml_tags(self,in_text):
	
		# convert in_text to a mutable object (e.g. list)
		s_list = list(in_text)
		i,j = 0,0
	
		while i < len(s_list):
		# iterate until a left-angle bracket is found
			if s_list[i] == '<':
				while s_list[i] != '>':
				
					s_list.pop(i)
				
			# pops the right-angle bracket, too
				s_list.pop(i)
			else:
				i=i+1
			
		# convert the list back into text
		join_char=''
		return join_char.join(s_list)

	def timer_cb(self):
		"""Show a new supplication"""
		self.__m.go_last()
		self.__m.go_forward()
		return self.refresh_text()

	def refresh_text(self):
		"""Redraw canvas to update the text, used by the timeout function"""
		print("Refreshing text...")
		self.scrol = 180
		self.redraw_canvas()
		print("Done!")
		return True
		
	def show_text(self):
		"""Show text on startup properly, return false to do it only once"""
		print("Loading text...")
		self.redraw_canvas()
		print("Done!")
		return False

# If the program is run directly or passed as an argument to the python
# interpreter then create a Screenlet instance and show it
if __name__ == "__main__":
	import screenlets.session
	screenlets.session.create_session(MonajatScreenlet)

