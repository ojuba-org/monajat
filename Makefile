APPNAME := monajat
VERSION := $(shell awk '/Version:/ { print $$2 }' $(APPNAME).spec)
DESTDIR = /
DATADIR = $(DESTDIR)/usr/share
DOCDIR = $(DATADIR)/doc/$(APPNAME)-$(VERSION)
XDGDIR = $(DESTDIR)/etc/xdg
SOURCES = $(wildcard *.desktop.in)
TARGETS = ${SOURCES:.in=}

ECHO := echo
NAKE := make
PYTHON := python3
INSTALL := install
INTLTOOL_MERGE := intltool-merge
RM := $(shell which rm | egrep '/' | sed  's/\s//g')


all: $(TARGETS) db

icons:
	@for i in 96 72 64 48 36 32 24 22 16; do \
		convert -background none monajat-data/$(APPNAME).svg -resize $${i}x$${i} $(APPNAME)-$${i}.png; \
	done
db:
	@$(PYTHON) gen-db.py
		
pos:
	@$(MAKE) -C po all

install: all
	@$(ECHO) "*** Installing..."
	@$(PYTHON) setup.py install -O2 --root $(DESTDIR)
	@$(ECHO) "Copying: $(APPNAME)-autostart.desktop -> $(XDGDIR)/autostart/"
	@$(INSTALL) -d $(XDGDIR)/autostart/
	@$(INSTALL) -m 0644 $(APPNAME)-autostart.desktop $(XDGDIR)/autostart/
	@$(INSTALL) -d $(DATADIR)
	@cp -r screenlets $(DATADIR)
	@$(INSTALL) -d $(DOCDIR)
	@$(INSTALL) -d $(DATADIR)/icons/hicolor/scalable/apps;
	@$(INSTALL) -m 0644 -D monajat-data/$(APPNAME).svg $(DATADIR)/icons/hicolor/scalable/apps/
#	@for i in 96 72 64 48 36 32 24 22 16; do \
#		$(INSTALL) -d $(DATADIR)/icons/hicolor/$${i}x$${i}/apps; \
#		$(INSTALL) -m 0644 -D $(APPNAME)-$${i}.png $(DATADIR)/icons/hicolor/$${i}x$${i}/apps/$(APPNAME).png; \
#	done
	for i in README COPYING TODO NEWS; do\
		$(ECHO) "Copying: $${i} -> $(DOCDIR)";\
		$(INSTALL) -m 0644 -D $${i} $(DOCDIR)/$${i}; \
	done

uninstall:
	@$(ECHO) "*** Uninstalling..."
	@$(ECHO) "- Removing: $(XDGDIR)/autostart/$(APPNAME)-autostart.desktop"
	@$(RM) -f $(XDGDIR)/autostart/$(APPNAME)-autostart.desktop
	@$(ECHO) "- Removing: $(DOCDIR)"
	@$(RM) -rf $(DOCDIR)
	@$(ECHO) "- Removing: $(DESTDIR)/usr/share/locale/*/LC_MESSAGES/$(APPNAME).mo"
	@$(RM) -f $(DESTDIR)/usr/share/locale/*/LC_MESSAGES/$(APPNAME).mo
	@$(ECHO) "- Removing: $(DESTDIR)/usr/bin/$(APPNAME)"
	@$(RM) -f $(DESTDIR)/usr/bin/$(APPNAME)
	@$(ECHO) "- Removing: $(DESTDIR)/usr/lib/python*/site-packages/$(APPNAME)"
	@$(RM) -rf $(DESTDIR)/usr/lib/python*/site-packages/$(APPNAME)
	@$(ECHO) "- Removing: $(DESTDIR)/usr/lib/python*/site-packages/$(APPNAME)*"
	@$(RM) -r $(DESTDIR)/usr/lib/python*/site-packages/$(APPNAME)*
	@$(ECHO) "- Removing: $(DATADIR)/screenlets"
	@$(RM) -rf $(DATADIR)/screenlets
	@$(ECHO) "- Removing: $(DATADIR)/$(APPNAME)"
	@$(RM) -rf $(DATADIR)/$(APPNAME)
	@$(ECHO) "- Removing: $(DATADIR)/icons/hicolor/scalable/apps/$(APPNAME).svg"
	@$(RM) -f $(DATADIR)/icons/hicolor/scalable/apps/$(APPNAME).svg
	@$(ECHO) "- Removing: $(DATADIR)/icons/hicolor/*/apps/$(APPNAME).png"
	@$(RM) -f $(DATADIR)/icons/hicolor/*/apps/$(APPNAME).png;
	@$(ECHO) "- Removing: $(DESTDIR)/usr/bin/$(APPNAME)-*"
	@$(RM) -f $(DESTDIR)/usr/bin/$(APPNAME)-*

		
%.desktop: %.desktop.in pos
	@$(ECHO) "*** Generating Database..."
	@$(INTLTOOL_MERGE) -d po $< $@

clean_restor_pos:
	@make clean
	@$(ECHO) "*** Retoring pos..."
	@git checkout po/* 2>/dev/null || :
    
clean:
	@$(ECHO) "*** Cleaning..."
	@$(MAKE) -C po clean
	@$(ECHO) "- Removing: $(TARGETS)"
	@$(RM) -f $(TARGETS)
	@$(ECHO) "- Removing: locale build"
	@$(RM) -rf locale build
	@$(ECHO) "- Removing: *.pyc"
	@$(RM) -f *.pyc
	@$(ECHO) "- Removing: */*.pyc"
	@$(RM) -f */*.pyc
	@$(ECHO) "- Removing: $(APPNAME)-*.png"
	@$(RM) -f $(APPNAME)-*.png
	@$(ECHO) "- Removing: monajat-data/data.db"
	@$(RM) -f monajat-data/data.db
	
