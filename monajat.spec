%global owner ojuba-org

Name: monajat
Summary: Monajat Islamic Supplications
Summary: منظومة أذكار إسلامية
URL: http://ojuba.org
Version: 3.0
Release: 1%{?dist}
Source: https://github.com/%{owner}/%{name}/archive/%{version}/%{name}-%{version}.tar.gz
License: WAQFv2 and GPLv2
BuildArch: noarch
Requires: python
Requires: libitl
Requires: pygobject3 >= 3.0.2
BuildRequires: ImageMagick
BuildRequires: intltool
BuildRequires: gettext
BuildRequires: python-setuptools
BuildRequires: python2-devel

%description
Monajat Islamic Supplications.

%description -l ar
منظومة أذكار إسلامية.

%package database
Summary: Monajat Database
Summary(ar): قاعدة بيانات مناجاة
BuildArch: noarch

%description database
This is the database used by Monajat.

%description database -l ar
قاعد البيانات المُستعملة بواسطة برنامج مُناجاة.

%package -n python-monajat
Summary: Monajat python module
Summary(ar): وحدة بيثون لمُناجاة
BuildArch: noarch
Requires: python
Requires: %{name}-database
Requires: libitl

%description -n python-monajat
This is the python Monajat library needed by all monajat front ends.

%description -n python-monajat -l ar
مكتبة بيثون لبرنامج مُناجاة و هي مطلوبة لكل واجهات البرنامج.

%package applet
Summary: Monajat Tray Applet
Summary(ar): بريمج مُناجاة لصينية النّظام
BuildArch: noarch
Requires: python-monajat
# TODO: is it better to say gnome-python2-extras ?
Requires: pygtk2
Requires: notify-python
Requires: desktop-notification-daemon

%description applet
This package contains Monajat Desktop Tray Applet.

%description applet -l ar
بريمج مُناجاة لصينية النّظام.

%package mod
Summary: Monajat for console
Summary(ar): مُناجاة للطّرفية
BuildArch: noarch
Requires: python-monajat

%description mod
Monajat in terminal.

%description mod -l ar
مُناجاة في الطّرفية.

%package screenlets
Summary: Monajat for Screenlets
Summary(ar): مُناجاة لسكرينلت
BuildArch: noarch
Requires: screenlets
Requires: python-monajat

%description screenlets
Monajat in Screenlets.

%description screenlets -l ar
مُناجاة كسكرينلت.

%prep
%autosetup -n %{name}-%{version}

%build
make %{?_smp_mflags}

%install
%make_install

%files database
%{_datadir}/%{name}/data.db

%files -n python-monajat
%license COPYING
%doc README TODO NEWS
%{_defaultdocdir}/%{name}-%{version}/*
%{python2_sitelib}/%{name}/*.py*
%{python2_sitelib}/*.egg-info
%{_datadir}/locale/*/*/*.mo

%files applet
%{_bindir}/%{name}-applet
%{_datadir}/%{name}/cities.db
%{_datadir}/%{name}/athan.ogg
%{_datadir}/%{name}/%{name}.svg
%{_datadir}/icons/hicolor/scalable/apps/%{name}.svg
/etc/xdg/autostart/*

%files mod
%{_bindir}/%{name}-mod

%files screenlets
%{_datadir}/screenlets/*

%changelog
* Wed Feb 8 2017 Mosaab Alzoubi <moceap#hotmail.com> - 3.0-1
- Update to 3.0
- New way to Github

* Mon Jul 27 2015 Mosaab Alzoubi <moceap#hotmail.com> - 2.6.6-1
- Update to 2.6.6
- Use %%make_install and %%license
- Add Arabic Summaries and Descriptions
- General Revision

* Wed Jul 30 2014 Ehab El-Gedawy <ehabsas@gmail.com> - 2.6.5-3
- New options in the settings for the prayer times
- Update en_GB.po
- Update ar.po
- Add more options in the settings for prayer times.
- Add previous releases in NEWS file
- relpace glib with GObject, to prevent (Segmentation fault)
- fix notification actions
- fix Gst player 

* Sun Feb 16 2014 Mosaab Alzoubi <moceap@hotmail.com> - 2.6.5-2
- General Revision.

* Sat Jul 23 2011 Muayyad Saleh Alsadi <alsadi@ojuba.org> - 2.6.4-1
- use notify object per notification
- fix unicode
- fix installation files
- cities search fix
- speed up search cities
- port SoundPlayer to Gst
- Port to gtk3

* Sat Jul 23 2011 Muayyad Saleh Alsadi <alsadi@ojuba.org> - 2.6.0-1
- play Athan audio file

* Thu Jul 14 2011 Muayyad Saleh Alsadi <alsadi@ojuba.org> - 2.5.0-1
- prayer time support

* Thu Jun 17 2010 Muayyad Saleh Alsadi <alsadi@ojuba.org> - 2.3.2-1
- Override build & clean commands in a cleaner manne
- Install monajat-applet & monajat-mod as scripts
- fix url escape

* Wed Oct 21 2009  Muayyad Saleh AlSadi <alsadi@ojuba.org> - 2.3.1-1
- load/save user preferences

* Tue Sep 22 2009  Muayyad Saleh AlSadi <alsadi@ojuba.org> - 2.3.0-2
- split database package (to be used by plasma-widget-athkar without pulling all monajat)
- add screenlets package

* Thu Aug 13 2009  Muayyad Saleh AlSadi <alsadi@ojuba.org> - 2.2.1-1
- many options to menu

* Sat Aug 8 2009  Muayyad Saleh AlSadi <alsadi@ojuba.org> - 2.1.1-1
- show on every 5 minutes

* Thu Aug 6 2009  Muayyad Saleh AlSadi <alsadi@ojuba.org> - 0.1.0-1
- initial packing
