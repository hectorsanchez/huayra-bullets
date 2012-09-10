#!/usr/bin/python
# -*- coding: utf-8 -*-

from gi.repository import Gio
import gtk
import gtk.gdk
import webkit 
import os
import sys
import subprocess
import urllib2

# Base Key en GSettings 
BASE_KEY = "apps.conectar-bullets"


class BulletsBrowser(webkit.WebView):
	"""
	Widget for browsing the bullets.
	"""
	def __init__(self, gsettings, start_page):
		webkit.WebView.__init__(self)
		self.gsettings = gsettings
		self.get_property("settings").set_property("enable-default-context-menu", False)
		self.connect('navigation-policy-decision-requested', self._on_navigate_decision)
		self.load_uri(start_page)
    
	def _on_navigate_decision(self, view, frame, req, action, decision):
		parts =  req.get_uri().split("://", 1)
		if len(parts) == 2:
			if parts[0] == 'exec':
				#Lanzar comandos externos
				command = urllib2.unquote(parts[1])
				subprocess.Popen(command, shell=True)
				return True
			if parts[0] == 'ui':
				#Funciones del BulletsBrowser que pueden ser llamadas desde las paginas.
				params = parts[1].split("?", 1)
				if params[0] == 'finalize':
					for p in params:
						if p == 'autostart':
							gsettings.set_boolean("auto-start", True)
						elif p == 'no_autostart':
							gsettings.set_boolean("auto-start", False)
					gtk.main_quit()
				return True
		return False

def build_app_window(gsettings, start_page):
	"""
	Build application window.
	"""
	sw = gtk.ScrolledWindow()
	bullet_browser = BulletsBrowser(gsettings, start_page) 
	sw.add(bullet_browser) 
	win = gtk.Window(gtk.WINDOW_TOPLEVEL)
	win.add(sw) 
	win.set_resizable(False)
	bullet_browser.set_size_request(600, 400)
	win.set_default_size(600, 400)
	win.set_title("Primeros pasos")
	win.set_position(gtk.WIN_POS_CENTER)
	win.set_deletable(False)
	win.connect("destroy", gtk.main_quit)
	return win


if __name__ == '__main__':
	gsettings = Gio.Settings.new(BASE_KEY)
	if not gsettings.get_boolean('auto-start'):
		# Si se deshabilito el autostart, no mostrar los bullets
		sys.exit(0)
	
	win = build_app_window(gsettings, "file://" + os.path.dirname(os.path.abspath(__file__)) + "/1.html")
	win.show_all() 
	gtk.main()
