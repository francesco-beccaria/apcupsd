Name:         apcupsd
Version:      3.12.1
Release:      1%{?dist}
Summary:      APC UPS Power Control Daemon for Linux

Group:        System Environment/Daemons
License:      GPL
URL:          http://www.apcupsd.com
Source0:      http://download.sourceforge.net/apcupsd/%{name}-%{version}.tar.gz
Source1:      apcupsd.logrotate
Source2:      apcupsd-httpd.conf
Patch0:       apcupsd-3.10.18-init.patch
BuildRoot:    %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)

BuildRequires: glibc-devel >= 2.3, gd-devel > 2.0, dos2unix
BuildRequires: net-snmp-devel, gettext-devel, ncurses-devel, tcp_wrappers
Requires:      /bin/mail
Requires(post):  /sbin/chkconfig
Requires(preun): /sbin/chkconfig

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


%prep
%setup -q
%patch -p1 -b .init
dos2unix examples/*status examples/*.c


%build
%configure \
        --sysconfdir="%{_sysconfdir}/apcupsd" \
        --with-cgi-bin="%{_localstatedir}/www/apcupsd" \
        --enable-cgi \
        --enable-pthreads \
        --enable-net \
        --enable-master-slave \
        --enable-apcsmart \
        --enable-dumb \
        --enable-net-snmp \
        --enable-snmp \
        --enable-usb \
        --enable-powerflute \
        --enable-nls \
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
%{_sysconfdir}/apcupsd/changeme
%{_sysconfdir}/apcupsd/commfailure
%{_sysconfdir}/apcupsd/commok
%{_sysconfdir}/apcupsd/offbattery
%{_sysconfdir}/apcupsd/onbattery
%{_sysconfdir}/apcupsd/masterconnect
%{_sysconfdir}/apcupsd/mastertimeout
%config(noreplace) %{_sysconfdir}/logrotate.d/apcupsd
%attr(0755,root,root) %{_sbindir}/*
%{_mandir}/*/*

%files cgi
%defattr(-,root,root,-)
%config(noreplace) %{_sysconfdir}/apcupsd/apcupsd.css
%config(noreplace) %{_sysconfdir}/httpd/conf.d/apcupsd.conf
%{_localstatedir}/www/apcupsd/


%post
# add our links
if [ "$1" -ge 1 ] ; then
/sbin/chkconfig --add apcupsd
fi


%preun
if [ $1 = 0 ] ; then
        # remove startup links
        /sbin/chkconfig --del apcupsd
fi


%changelog
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
- Removed %{_smp_mflags} from make, broke builds
- Patch init file to not start automatically and add reload
- Mark css file config
- Require /sbin/chkconfig

* Mon Oct 17 2005 - Orion Poplawski <orion@cora.nwra.com> - 3.10.18-2
- Add %defattr to -cgi package

* Wed Aug 17 2005 - Orion Poplawski <orion@cora.nwra.com> - 3.10.18-1
- Initial Fedora Version
