%bcond_without	systemd	# build without systemd
Summary:	A Linux entropy source using the HAVEGE algorithm
Name:		haveged
Version:	1.9.15
Release:	3
License:	GPL v3+
Group:		Daemons
Source0:	https://github.com/jirka-h/haveged/archive/v%{version}.tar.gz
# Source0-md5:	9298cbdfb37ab84bdb710f042373a354
Source1:	%{name}.init
URL:		http://www.irisa.fr/caps/projects/hipsor/
BuildRequires:	autoconf >= 2.59
BuildRequires:	automake
BuildRequires:	libtool
BuildRequires:	rpmbuild(macros) >= 1.644
%{?with_systemd:BuildRequires:	systemd-devel}
Requires(post,preun,postun):	systemd-units >= 38
Requires:	systemd-units >= 38
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%description
A Linux entropy source using the HAVEGE algorithm

Haveged is a user space entropy daemon which is not dependent upon the
standard mechanisms for harvesting randomness for the system entropy
pool. This is important in systems with high entropy needs or limited
user interaction (e.g. headless servers).

Haveged uses HAVEGE (HArdware Volatile Entropy Gathering and
Expansion) to maintain a 1M pool of random bytes used to fill
/dev/random whenever the supply of random bits in /dev/random falls
below the low water mark of the device. The principle inputs to
haveged are the sizes of the processor instruction and data caches
used to setup the HAVEGE collector. The haveged default is a 4kb data
cache and a 16kb instruction cache. On machines with a cpuid
instruction, haveged will attempt to select appropriate values from
internal tables.

%package libs
Summary:	Shared libraries for HAVEGE algorithm
Group:		Libraries

%description libs
Shared libraries for HAVEGE algorithm.

%package devel
Summary:	Headers and shared development libraries for HAVEGE algorithm
Group:		Development/Libraries
Requires:	%{name}-devel = %{version}-%{release}

%description devel
Headers and shared object symbolic links for the HAVEGE algorithm

%prep
%setup -q

%build
%{__libtoolize}
%{__aclocal}
%{__autoconf}
%{__autoheader}
%{__automake}
%configure \
	--disable-static
# SMP build is not working
%{__make} -j1

%install
rm -rf $RPM_BUILD_ROOT
%{__make} install \
	DESTDIR=$RPM_BUILD_ROOT

install -d $RPM_BUILD_ROOT%{systemdunitdir}
sed -e 's:@SBIN_DIR@:%{_sbindir}:g' contrib/Fedora/haveged.service > $RPM_BUILD_ROOT%{systemdunitdir}/haveged.service

install -d $RPM_BUILD_ROOT/etc/rc.d/init.d
install -p %{SOURCE1} $RPM_BUILD_ROOT/etc/rc.d/init.d/haveged

# We don't ship .la files.
rm $RPM_BUILD_ROOT%{_libdir}/libhavege.la

%clean
rm -rf $RPM_BUILD_ROOT

%post	libs -p /sbin/ldconfig
%postun	libs -p /sbin/ldconfig

%post
/sbin/chkconfig --add haveged
%service haveged restart
%systemd_post haveged.service

%preun
if [ "$1" = "0" ]; then
	%service haveged stop
	/sbin/chkconfig --del haveged
fi
%systemd_preun haveged.service

%postun
%systemd_reload

%files
%defattr(644,root,root,755)
%doc AUTHORS ChangeLog NEWS README contrib/build/havege_sample.c
%attr(754,root,root) /etc/rc.d/init.d/haveged
%attr(755,root,root) %{_sbindir}/haveged
%{_mandir}/man8/haveged.8*
%{systemdunitdir}/haveged.service

%files libs
%defattr(644,root,root,755)
%attr(755,root,root) %{_libdir}/libhavege.so.*.*.*
%ghost %{_libdir}/libhavege.so.2

%files devel
%defattr(644,root,root,755)
%{_includedir}/%{name}
%{_libdir}/libhavege.so
%{_mandir}/man3/libhavege.3*
