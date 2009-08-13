Name: monajat
Summary: Monajat Islamic Supplications
URL: http://git.ojuba.org/cgit/monajat/about/
Version: 2.2.1
Release: 1%{?dist}
Source0: http://git.ojuba.org/cgit/monajat/snapshot/%{name}-%{version}.tar.bz2
License: GPLv2
Group: System Environment/Base
BuildArch: noarch
BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)
BuildRequires: gettext
BuildRequires: python, python-setuptools

%{!?python_sitelib: %define python_sitelib %(%{__python} -c "from distutils.sysconfig import get_python_lib; print get_python_lib(1)")}

%description
Monajat Islamic Supplications

%package python
Group: System Environment/Base
Summary: Monajat Islamic Supplications
BuildArch: noarch
Requires: python, setuptool
%description python
Monajat Islamic Supplications

This is the python monajat library needed by all monajat front ends

%package applet
Summary: Monajat Islamic Supplications for Desktop Tray Applet
Group: System Environment/Base
BuildArch: noarch
# TODO: is it better to say gnome-python2-extras ?
Requires: python, setuptool, pygtk2, notify-python
Requires: monajat-python
%description applet
Monajat Islamic Supplications

This package contains the Desktop Tray Applet

%package mod
Summary: Monajat Islamic Supplications for console
Group: System Environment/Base
BuildArch: noarch
# TODO: is it better to say gnome-python2-extras ?
Requires: python, setuptool
Requires: monajat-python
%description mod
Monajat Islamic Supplications

This package contains a console application that can be used in issue message
or in the profile


%prep
%setup -q
%build
./update-pot.sh
./gen-mo.sh

%install
rm -rf $RPM_BUILD_ROOT

%{__python} setup.py install \
        --root=$RPM_BUILD_ROOT \
        --optimize=2
rm $RPM_BUILD_ROOT/%{python_sitelib}/%{name}/sql*.py*
mkdir -p $RPM_BUILD_ROOT/%{_datadir}/icons/hicolor/scalable/apps/
ln -s ../../../../%{name}/%{name}.svg $RPM_BUILD_ROOT/%{_datadir}/icons/hicolor/scalable/apps/%{name}.svg

%clean
rm -rf $RPM_BUILD_ROOT

%files python
%doc README COPYING TODO
%{python_sitelib}/%{name}/__init__.py*
%{python_sitelib}/%{name}/%{name}.py*
%{python_sitelib}/*.egg-info
%{_datadir}/locale/*/*/*.mo
%{_datadir}/%{name}/data.db

%files applet
%{python_sitelib}/%{name}/applet.py*
%{python_sitelib}/%{name}/utils.py*
%{_bindir}/%{name}-applet
%{_datadir}/%{name}/%{name}.svg
%{_datadir}/icons/hicolor/scalable/apps/%{name}.svg
/etc/xdg/autostart/*

%files mod
%{_bindir}/%{name}-mod

%changelog
* Thu Aug 13 2009  Muayyad Saleh AlSadi <alsadi@ojuba.org> - 2.2.1-1
- many options to menu

* Sat Aug 8 2009  Muayyad Saleh AlSadi <alsadi@ojuba.org> - 2.1.1-1
- show on every 5 minutes

* Thu Aug 6 2009  Muayyad Saleh AlSadi <alsadi@ojuba.org> - 0.1.0-1
- initial packing

