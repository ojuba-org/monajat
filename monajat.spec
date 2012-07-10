Name: monajat
Summary: Monajat Islamic Supplications
URL: http://git.ojuba.org/cgit/monajat/about/
Version: 2.6.5
Release: 1%{?dist}
Source0: http://git.ojuba.org/cgit/monajat/snapshot/%{name}-%{version}.tar.bz2
License: GPLv2
Group: System Environment/Base
BuildArch: noarch
BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)
Requires: python, libitl
Requires:   pygobject3 >= 3.0.2
BuildRequires: gettext
BuildRequires: python, python-setuptools

# /usr/share/gnome-shell/extensions/Monajat@ojuba.org

%{!?python_sitelib: %define python_sitelib %(%{__python} -c "from distutils.sysconfig import get_python_lib; print get_python_lib(1)")}

%description
Monajat Islamic Supplications

%package database
Group: System Environment/Base
Summary: Monajat Islamic Supplications database
BuildArch: noarch
%description database
Monajat Islamic Supplications

This is the database used by monajat.


%package python
Group: System Environment/Base
Summary: Monajat Islamic Supplications
BuildArch: noarch
Requires: python, %{name}-database, libitl
%description python
Monajat Islamic Supplications

This is the python monajat library needed by all monajat front ends

%package applet
Summary: Monajat Islamic Supplications for Desktop Tray Applet
Group: System Environment/Base
BuildArch: noarch
Requires: %{name}-python
# TODO: is it better to say gnome-python2-extras ?
Requires: pygtk2, notify-python, desktop-notification-daemon
%description applet
Monajat Islamic Supplications

This package contains the Desktop Tray Applet

%package mod
Summary: Monajat Islamic Supplications for console
Group: System Environment/Base
BuildArch: noarch
Requires: %{name}-python
%description mod
Monajat Islamic Supplications

This package contains a console application that can be used in issue message
or in the profile

%package screenlets
Summary: Monajat Islamic Supplications for Screenlets
Group: System Environment/Base
BuildArch: noarch
Requires: screenlets
Requires: %{name}-python
%description screenlets
Monajat Islamic Supplications

This package contains screenlets version

%prep
%setup -q

%build
make %{?_smp_mflags}

%install
rm -rf $RPM_BUILD_ROOT
%makeinstall DESTDIR=$RPM_BUILD_ROOT


%clean
rm -rf $RPM_BUILD_ROOT

%files database
%{_datadir}/%{name}/data.db

%files python
#%doc README COPYING TODO NEWS
%{_defaultdocdir}/%{name}-%{version}/*
%{python_sitelib}/%{name}/*.py*
%{python_sitelib}/*.egg-info
%{_datadir}/locale/*/*/*.mo

%files applet
%{python_sitelib}/%{name}/applet.py*
%{python_sitelib}/%{name}/utils.py*
%{_bindir}/%{name}-applet
%{_datadir}/%{name}/cities.db
%{_datadir}/%{name}/athan.ogg
%{_datadir}/%{name}/%{name}.svg

%{_datadir}/icons/hicolor/scalable/apps/%{name}.svg
%{_datadir}/icons/hicolor/*/apps/%{name}.png
/etc/xdg/autostart/*

%files mod
%{_bindir}/%{name}-mod

%files screenlets
%{_datadir}/screenlets/*

%changelog
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

