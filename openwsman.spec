%{!?python_sitelib: %global python_sitelib %(%{__python} -c "from distutils.sysconfig import get_python_lib; print get_python_lib()")}
%{!?python_sitearch: %global python_sitearch %(%{__python} -c "from distutils.sysconfig import get_python_lib; print get_python_lib(1)")}
%{!?ruby_sitelib: %global ruby_sitelib %(ruby -rrbconfig -e 'puts Config::CONFIG["sitelibdir"] ')}
%{!?ruby_sitearch: %global ruby_sitearch %(ruby -rrbconfig -e 'puts Config::CONFIG["sitearchdir"] ')}

Name:           openwsman
Version:        2.2.3
Release:        6%{?dist}
License:        BSD
Url:            http://www.openwsman.org/
Source:         http://downloads.sourceforge.net/project/openwsman/%{name}/%{version}/%{name}-%{version}.tar.bz2
Source1:        openwsmand.8.gz
Patch0:         %{name}-initscript.patch
# Patch1: accepted by upstream
Patch1:         openwsman-2.2.3-cert-verify-fix.patch
# Patch2: accepted by upstream
Patch2:         openwsman-2.2.3-release_cmpi_data_remove.patch
Patch3:         openwsman-2.2.3-initscript.patch
BuildRoot:      %(mktemp -ud %{_tmppath}/%{name}-%{version}-%{release}-XXXXXXX)
Group:          Applications/System
Summary:        Open-source Implementation of WS-Management
BuildRequires:  swig
BuildRequires:  libcurl-devel libxml2-devel pam-devel sblim-sfcc-devel
BuildRequires:  python python-devel ruby ruby-devel perl
BuildRequires:  perl-devel pkgconfig openssl-devel
BuildRequires:  libtool
Requires:       net-tools

%description
Openwsman is a project intended to provide an open-source
implementation of the Web Services Management specification
(WS-Management) and to expose system management information on the
Linux operating system using the WS-Management protocol. WS-Management
is based on a suite of web services specifications and usage
requirements that exposes a set of operations focused on and covers
all system management aspects.


%package -n libwsman1
License:        BSD
Group:          System Environment/Libraries
Summary:        Open-source Implementation of WS-Management
Provides:       %{name} = %{version}
Obsoletes:      %{name} < %{version}

%description -n libwsman1
Openwsman library for packages dependent on openwsman.


%package -n libwsman-devel
License:        BSD
Group:          Development/Libraries
Summary:        Open-source Implementation of WS-Management
Provides:       %{name}-devel = %{version}
Obsoletes:      %{name}-devel < %{version}
Requires:       libwsman1 = %{version}-%{release}
Requires:       %{name}-server = %{version}-%{release}
Requires:       %{name}-client = %{version}-%{release}
Requires:       sblim-sfcc-devel libxml2-devel pam-devel
Requires:       libcurl-devel

%description -n libwsman-devel
Development files for openwsman.


%package client
License:        BSD
Group:          System Environment/Libraries
Summary:        Openwsman Client libraries
Requires:       libwsman1 = %{version}-%{release}

%description client
Openwsman Client libraries.


%package server
License:        BSD
Group:          System Environment/Daemons
Requires:       net-tools
Requires:       libwsman1 = %{version}-%{release}
Requires(post):       chkconfig
Requires(preun):      chkconfig
Requires(postun):     initscripts
Summary:        Openwsman Server and service libraries

%description server
Openwsman Server and service libraries.


%package python
License:        BSD
Group:          Development/Libraries
Summary:        Python bindings for openwsman client API
Requires:       python
Requires:       libwsman1 = %{version}-%{release}

%description python
This package provides Python bindings to access the openwsman client
API.


%package ruby
License:        BSD
Group:          Development/Libraries
Requires:       ruby
Requires:       ruby(abi) = 1.8
Requires:       libwsman1 = %{version}-%{release}
Summary:        Ruby bindings for openwsman client API

%description ruby
This package provides Ruby bindings to access the openwsman client API.


%package perl
License:        BSD
Group:          Development/Libraries
Requires:       perl(:MODULE_COMPAT_%(eval "`%{__perl} -V:version`"; echo $version))
Requires:       libwsman1 = %{version}-%{release}
Summary:        Perl bindings for openwsman client API

%description perl
This package provides Perl bindings to access the openwsman client API.


%prep
%setup -q 
%patch0 -p1 -b .initscript
%patch1 -p1 -b .cert-verify-fix
%patch2 -p1 -b .release_cmpi_data_remove
%patch3 -p1 -b .initscript2


%build
/bin/sh autoconfiscate.sh
# Removing executable permissions on .c and .h files to fix rpmlint warnings. 
chmod -x src/cpp/WsmanClient.h
chmod -x src/lib/wsman-filter.c
chmod -x include/wsman-filter.h
%configure \
    --disable-more-warnings \
    --disable-static \
    --enable-python \
    --enable-ruby \
    --enable-perl \
    --enable-ipv6
sed -i -e '/not ending/ s/.*/true/' libtool
export RPM_OPT_FLAGS="$RPM_OPT_FLAGS -DFEDORA"
make CFLAGS="$RPM_OPT_FLAGS" %{?_smp_flags}


%install
rm -rf %{buildroot}
make DESTDIR=%{buildroot} install
rm -f %{buildroot}/%{_libdir}/*.la
rm -f %{buildroot}/%{_libdir}/openwsman/plugins/*.la
rm -f %{buildroot}/%{_libdir}/openwsman/authenticators/*.la
mkdir -p %{buildroot}/%{_sysconfdir}/init.d
install -m 644 etc/openwsman.conf %{buildroot}/%{_sysconfdir}/openwsman
install -m 644 etc/ssleay.cnf %{buildroot}/%{_sysconfdir}/openwsman
install -m 644 etc/openwsman_client.conf %{buildroot}/%{_sysconfdir}/openwsman
install -m 755 etc/init/openwsmand.sh %{buildroot}/%{_sysconfdir}/init.d/openwsmand
ln -sf %{_sysconfdir}/init.d/openwsmand %{buildroot}/%{_sbindir}/rcopenwsmand
# install manpage
mkdir -p %{buildroot}/%{_mandir}/man8/
cp %SOURCE1 %{buildroot}/%{_mandir}/man8/
# move ruby files to correct places
%global rarch %(echo %{ruby_sitearch} | cut -d"/" -f7)
mkdir -p %{buildroot}/%{ruby_sitelib}
mkdir -p %{buildroot}/%{ruby_sitearch}
mv %{buildroot}/usr/lib/ruby/1.8/openwsman %{buildroot}/%{ruby_sitelib}/openwsman
mv %{buildroot}/%{_libdir}/ruby/%{rarch}/1.8/%{rarch}/openwsman.so %{buildroot}/%{ruby_sitearch}


%clean
rm -rf %{buildroot}

%files -n libwsman1
%defattr(-,root,root,-)
%doc AUTHORS COPYING ChangeLog README TODO
%{_libdir}/libwsman.so.*
%{_libdir}/libwsman_client.so.*
%{_libdir}/libwsman_curl_client_transport.so.*

%files -n libwsman-devel
%defattr(-,root,root,-)
%{_includedir}/*
%{_libdir}/pkgconfig/*
%{_libdir}/*.so
%doc AUTHORS COPYING ChangeLog README

%files python
%defattr(-,root,root,-)
%{python_sitearch}/*.so
%{python_sitelib}/*.py
%{python_sitelib}/*.pyc
%{python_sitelib}/*.pyo
%doc AUTHORS COPYING ChangeLog README

%files ruby
%defattr(-,root,root,-)
%{ruby_sitearch}/openwsman.so
%dir %{ruby_sitelib}/openwsman
%{ruby_sitelib}/openwsman/openwsman.rb
%{ruby_sitelib}/openwsman/xmlnode.rb
%doc AUTHORS COPYING ChangeLog README

%files perl
%defattr(-,root,root,-)
%{perl_vendorarch}/openwsman.so
%{perl_vendorlib}/openwsman.pm
%doc AUTHORS COPYING ChangeLog README

%files server
# Don't remove *.so files from the server package.
# the server fails to start without these files.
%defattr(-,root,root,-)
%dir %{_sysconfdir}/openwsman
%config(noreplace) %{_sysconfdir}/openwsman/openwsman.conf
%config(noreplace) %{_sysconfdir}/openwsman/ssleay.cnf
%attr(0755,root,root) %{_sysconfdir}/openwsman/owsmangencert.sh
%config(noreplace) %{_sysconfdir}/pam.d/openwsman
%attr(0755,root,root) %{_sysconfdir}/init.d/openwsmand
%dir %{_libdir}/openwsman
%dir %{_libdir}/openwsman/authenticators
%{_libdir}/openwsman/authenticators/*.so
%{_libdir}/openwsman/authenticators/*.so.*
%dir %{_libdir}/openwsman/plugins
%{_libdir}/openwsman/plugins/*.so
%{_libdir}/openwsman/plugins/*.so.*
%{_sbindir}/openwsmand
%{_sbindir}/rcopenwsmand
%{_libdir}/libwsman_server.so.*
%{_mandir}/man8/*
%doc AUTHORS COPYING ChangeLog README

%files client
%defattr(-,root,root,-)
%config(noreplace) %{_sysconfdir}/openwsman/openwsman_client.conf
%{_libdir}/libwsman_clientpp.so.*
%doc AUTHORS COPYING ChangeLog README

%post -n libwsman1 -p /sbin/ldconfig

%postun -n libwsman1 -p /sbin/ldconfig

%post server
/sbin/ldconfig
chkconfig --add  openwsmand

%preun server
if [ $1 = 0 ] ; then
    /sbin/service %{name}d stop >/dev/null 2>&1
    /sbin/chkconfig --del openwsmand
fi

%postun server
rm -f /var/log/wsmand.log
if [ "$1" -ge "1" ] ; then
    /sbin/service openwsmand condrestart >/dev/null 2>&1 || :
fi
/sbin/ldconfig

%post client -p /sbin/ldconfig

%postun client -p /sbin/ldconfig

%changelog
* Mon Jul 12 2010 Vitezslav Crhonek <vcrhonek@redhat.com> - 2.2.3-6
- Fix initscript

* Tue Jun 15 2010 Vitezslav Crhonek <vcrhonek@redhat.com> - 2.2.3-5
- Add help2man generated manpage for openwsmand
- Fix Requires fields

* Wed May 26 2010 Vitezslav Crhonek <vcrhonek@redhat.com> - 2.2.3-4
- Fix openwsman crash with sblim-sfcb-1.3.7
- Add configuration file to openwsman-client

* Tue May 18 2010 Vitezslav Crhonek <vcrhonek@redhat.com> - 2.2.3-3
- Split openwsman package

* Mon Mar 15 2010 Vitezslav Crhonek <vcrhonek@redhat.com> - 2.2.3-2
- Fix client fails to connect even if valid CA certificate is present
  Resolves: #572560

* Thu Mar 11 2010 Vitezslav Crhonek <vcrhonek@redhat.com> - 2.2.3-1
- Update to openwsman-2.2.3

* Mon Nov 23 2009 Dennis Gregorovic <dgregor@redhat.com> - 2.2.0-1.1
- Rebuilt for RHEL 6

* Thu Oct  1 2009 Praveen K Paladugu <praveen_paladugu@dell.com> - 2.2.0-1
- Updated the sources to 2.2.0. Couple of major changes are as follows:
- Major changes:
-       Adapt IANA ports of 5985 (http) and 5986 (https)
-       Change the Ruby bindings module name to 'Openwsman'
-       Change the Ruby plugin module name to 'Openwsman'
-       IPv6 support (A_Venkatachalam@Dell.com)
-       preliminary support for wbem intrinsic operations
-           'EnumerateClassNames' and 'GetClass' (kkaempf@suse.de)
-            (needs fixed sblim-sfcc, see www.openwsman.org for details)

* Fri Aug 21 2009 Tomas Mraz <tmraz@redhat.com> - 2.1.0-4
- rebuilt with new openssl

* Sat Jul 25 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2.1.0-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_12_Mass_Rebuild

* Thu Feb 26 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2.1.0-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_11_Mass_Rebuild

* Mon Sep 22 2008 Matt Domsch <Matt_Domsch@dell.com> - 2.1.0-1
- update to 2.1.0, resolves security issues

* Tue Aug 19 2008  <srinivas_ramanatha@dell.com> - 2.0.0-1%{?dist}
- Modified the spec file to adhere to fedora packaging guidelines.
