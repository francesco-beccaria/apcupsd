Name:         apcupsd
Version:      3.14.2
Release:      2%{?dist}
Summary:      APC UPS Power Control Daemon for Linux

Group:        System Environment/Daemons
License:      GPL
URL:          http://www.apcupsd.com
Source0:      http://downloads.sourceforge.net/apcupsd/%{name}-%{version}.tar.gz
Source1:      apcupsd.logrotate
Source2:      apcupsd-httpd.conf
Patch0:       apcupsd-3.14.1-init.patch
Patch1:       apcupsd-3.14.2-shutdown.patch
BuildRoot:    %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)

BuildRequires: glibc-devel >= 2.3, gd-devel > 2.0
BuildRequires: net-snmp-devel, gettext-devel, ncurses-devel, tcp_wrappers-devel
BuildRequires: gtk2-devel, gnome-vfs2-devel, desktop-file-utils
Requires:      /bin/mail
Requires(post):  /sbin/chkconfig
Requires(preun): /sbin/chkconfig
Requires(preun): /sbin/service
Requires(postun): /sbin/service

%description
Apcupsd can be used for controlling most APC UPSes. During a
power failure, apcupsd will inform the users about the power
failure and that a shutdown may occur.  If power is not restored,
a system shutdown will follow when the battery is exausted, a
timeout (seconds) expires, or the battery runtime expires based
on internal APC calculations determined by power consumption
rates.  If the power is restored before one of the above shutdown
conditions is met, apcupsd will inform users about this fact.
Some features depend on what UPS model you have (simple or smart).


%package cgi
Summary:      Web interface for apcupsd
Group:        Applications/Internet
Requires:     %{name} = %{version}-%{release}
Requires:     httpd

%description cgi
A CGI interface to the APC UPS monitoring daemon.


%package gui
Summary:      GUI interface for apcupsd
Group:        Applications/System
Requires:     %{name} = %{version}-%{release}

%description gui
A GUI interface to the APC UPS monitoring daemon.


%prep
%setup -q
%patch0 -p1 -b .init
%patch1 -p1 -b .shutdown

# Don't strip binaries
sed -i -e 's/^\(.*INSTALL_PROGRAM.*\) -s /\1 /' src{,/cgi}/Makefile.in


%build
%configure \
        --sysconfdir="%{_sysconfdir}/apcupsd" \
        --with-cgi-bin="%{_localstatedir}/www/apcupsd" \
        --enable-cgi \
        --enable-pthreads \
        --enable-net \
        --enable-apcsmart \
        --enable-dumb \
        --enable-net-snmp \
        --enable-snmp \
        --enable-usb \
        --enable-powerflute \
        --enable-nls \
        --enable-gapcmon \
        --enable-pcnet \
        --with-libwrap=%{_libdir} \
        --with-serial-dev= \
        --with-upstype=usb \
        --with-upscable=usb \
        APCUPSD_MAIL=/bin/mail
make


%install
rm -rf $RPM_BUILD_ROOT

mkdir -p $RPM_BUILD_ROOT%{_initrddir}
mkdir -p $RPM_BUILD_ROOT%{_localstatedir}/www/apcupsd

make DESTDIR=$RPM_BUILD_ROOT install

rm $RPM_BUILD_ROOT%{_initrddir}/halt
rm $RPM_BUILD_ROOT%{_initrddir}/halt.old

install -m744 platforms/apccontrol \
              $RPM_BUILD_ROOT%{_sysconfdir}/apcupsd/apccontrol
	      
install -m755 platforms/redhat/apcupsd $RPM_BUILD_ROOT%{_initrddir}

install -d %{buildroot}%{_sysconfdir}/logrotate.d
install -m0644 %{SOURCE1} %{buildroot}%{_sysconfdir}/logrotate.d/%{name}
install -d %{buildroot}%{_sysconfdir}/httpd/conf.d
install -m0644 %{SOURCE2} %{buildroot}%{_sysconfdir}/httpd/conf.d/%{name}.conf

desktop-file-install --vendor="fedora" \
        --dir=${RPM_BUILD_ROOT}%{_datadir}/applications \
        --delete-original \
        ${RPM_BUILD_ROOT}%{_datadir}/applications/gapcmon.desktop

# Cleanup for later %doc processing
chmod -x examples/*.conf examples/*.c
rm examples/*.in


%clean
rm -rf $RPM_BUILD_ROOT


%files
%defattr(-,root,root,-)
%doc COPYING ChangeLog examples ReleaseNotes
%dir %{_sysconfdir}/apcupsd
%{_initrddir}/apcupsd
%config(noreplace) %{_sysconfdir}/apcupsd/apcupsd.conf
%config(noreplace) %{_sysconfdir}/apcupsd/hosts.conf
%config(noreplace) %{_sysconfdir}/apcupsd/multimon.conf
%attr(0755,root,root) %{_sysconfdir}/apcupsd/apccontrol
%config(noreplace) %{_sysconfdir}/apcupsd/changeme
%config(noreplace) %{_sysconfdir}/apcupsd/commfailure
%config(noreplace) %{_sysconfdir}/apcupsd/commok
%config(noreplace) %{_sysconfdir}/apcupsd/offbattery
%config(noreplace) %{_sysconfdir}/apcupsd/onbattery
%config(noreplace) %{_sysconfdir}/logrotate.d/apcupsd
%attr(0755,root,root) %{_sbindir}/*
%{_mandir}/*/*

%files cgi
%defattr(-,root,root,-)
%config(noreplace) %{_sysconfdir}/apcupsd/apcupsd.css
%config(noreplace) %{_sysconfdir}/httpd/conf.d/apcupsd.conf
%{_localstatedir}/www/apcupsd/

%files gui
%defattr(-,root,root,-)
%{_bindir}/gapcmon
%{_datadir}/applications/fedora-gapcmon.desktop
%{_datadir}/pixmaps/apcupsd.png
%{_datadir}/pixmaps/charging.png
%{_datadir}/pixmaps/gapc_prefs.png
%{_datadir}/pixmaps/onbatt.png
%{_datadir}/pixmaps/online.png
%{_datadir}/pixmaps/unplugged.png


%post
/sbin/chkconfig --add apcupsd

%preun
if [ $1 = 0 ]; then
   /sbin/service apcupsd stop >/dev/null 2>&1
   /sbin/chkconfig --del apcupsd
fi

%postun
if [ $1 -ge 1 ]; then
   /sbin/service apcupsd condrestart >/dev/null 2>&1 || :
fi


%changelog
* Wed Jan 30 2008 Tomas Smetana <tsmetana@redhat.com> - 3.14.2-2
- fix #348701 - apcupsd control script does not invoke shutdown properly

* Wed Oct 10 2007 - Orion Poplawski <orion@cora.nwra.com> - 3.14.2-1
- Update to 3.14.2, remove upstreamed patches

* Wed Aug  1 2007 - Orion Poplawski <orion@cora.nwra.com> - 3.14.1-3
- Add patch to close open file descriptors (bug #247162)
- Stop/restart service as needed on removal/upgrade

* Mon Jun 02 2007 - Orion Poplawski <orion@cora.nwra.com> - 3.14.1-2
- Add patch for linux USB UPS detection (bug #245864)

* Tue May 29 2007 - Orion Poplawski <orion@cora.nwra.com> - 3.14.1-1
- Update to 3.14.1

* Mon Apr 23 2007 - Orion Poplawski <orion@cora.nwra.com> - 3.14.0-2
- Fix init script for LSB compliance (bug #237532)

* Mon Feb 12 2007 - Orion Poplawski <orion@cora.nwra.com> - 3.14.0-1
- Update to 3.14.0

* Fri Jan  5 2007 - Orion Poplawski <orion@cora.nwra.com> - 3.13.9-2
- Mark everything in /etc/apcupsd noreplace
- Change BR to tcp_wrappers-devel

* Thu Nov 30 2006 - Orion Poplawski <orion@cora.nwra.com> - 3.13.9-1
- Update to 3.13.9, add gui package

* Mon Oct  9 2006 - Orion Poplawski <orion@cora.nwra.com> - 3.12.4-3
- Fix /etc/httpd/conf.d/apcupsd.conf so DirectoryIndex works (bug #209952).
  Patch from Clive Messer (clive@vacuumtube.org.uk)

* Tue Aug 29 2006 - Orion Poplawski <orion@cora.nwra.com> - 3.12.4-2
- Rebuild for FC6

* Mon Aug 21 2006 - Orion Poplawski <orion@cora.nwra.com> - 3.12.4-1
- Update to 3.12.4

* Tue Jan 10 2006 - Orion Poplawski <orion@cora.nwra.com> - 3.12.2-1
- Update to 3.12.2
- Don't strip binaries

* Tue Jan 10 2006 - Orion Poplawski <orion@cora.nwra.com> - 3.12.1-1
- Update to 3.12.1

* Wed Jan  4 2006 - Orion Poplawski <orion@cora.nwra.com> - 3.12.0-1
- Update to 3.12.0

* Tue Jan  3 2006 - Orion Poplawski <orion@cora.nwra.com> - 3.10.18-7
- Rebuild

* Wed Dec 21 2005 - Orion Poplawski <orion@cora.nwra.com> - 3.10.18-6
- Rebuild

* Wed Nov 16 2005 - Orion Poplawski <orion@cora.nwra.com> - 3.10.18-5
- Bump for new openssl

* Fri Nov  4 2005 - Orion Poplawski <orion@cora.nwra.com> - 3.10.18-4
- Add logrotate script for /var/log/apcupsd.events
- Add apache configuration script and change cgi directory to
  /var/www/apcupsd
- Compile in snmp, net-snmp, powerflute, nls, add tcp_wrappers support

* Mon Oct 17 2005 - Orion Poplawski <orion@cora.nwra.com> - 3.10.18-3
- Removed %%{_smp_mflags} from make, broke builds
- Patch init file to not start automatically and add reload
- Mark css file config
- Require /sbin/chkconfig

* Mon Oct 17 2005 - Orion Poplawski <orion@cora.nwra.com> - 3.10.18-2
- Add %%defattr to -cgi package

* Wed Aug 17 2005 - Orion Poplawski <orion@cora.nwra.com> - 3.10.18-1
- Initial Fedora Version
