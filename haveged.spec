Summary:	A Linux entropy source using the HAVEGE algorithm
Name:		haveged
Version:	1.9.1
Release:	0.1
License:	GPL v3+
Group:		Daemons
Source0:	http://www.issihosts.com/haveged/%{name}-%{version}.tar.gz
# Source0-md5:	015ff58cd10607db0e0de60aeca2f5f8
URL:		http://www.irisa.fr/caps/projects/hipsor/
#Source1:	%{name}.service
BuildRequires:	automake
BuildRequires:	gdb
BuildRequires:	systemd-units
%if 0
Requires(post):	systemd
Requires(preun):	systemd
Requires(postun):	systemd
%endif
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
#autoreconf -fiv
%configure \
	--disable-static
# SMP build is not working
%{__make} -j1

%if %{with tests}
%{__make} check
%endif

%install
rm -rf $RPM_BUILD_ROOT
%{__make} install \
	INSTALL="install -p" \
	DESTDIR=$RPM_BUILD_ROOT

install -d $RPM_BUILD_ROOT%{systemdunitdir}
#cp -p %{SOURCE1} $RPM_BUILD_ROOT%{systemdunitdir}/haveged.service

# We don't ship .la files.
rm $RPM_BUILD_ROOT%{_libdir}/libhavege.la

%clean
rm -rf $RPM_BUILD_ROOT

%post	libs -p /sbin/ldconfig
%postun	libs -p /sbin/ldconfig

%if 0
%post
%systemd_post haveged.service

%preun
%systemd_preun haveged.service

%postun
%systemd_postun_with_restart haveged.service
%endif

%files
%defattr(644,root,root,755)
%doc COPYING README ChangeLog AUTHORS contrib/build/havege_sample.c
%attr(755,root,root) %{_sbindir}/haveged
%{_mandir}/man8/haveged.8*
#%{systemdunitdir}/haveged.service

%files libs
%defattr(644,root,root,755)
%attr(755,root,root) %{_libdir}/libhavege.so.*.*.*
%ghost %{_libdir}/libhavege.so.1

%files devel
%defattr(644,root,root,755)
%{_includedir}/%{name}
%{_libdir}/libhavege.so
%{_mandir}/man3/libhavege.3*
