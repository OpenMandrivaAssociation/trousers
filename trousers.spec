%define major 1
%define libname %mklibname tspi %{major}
%define develname %mklibname -d %{name}

%define _disable_lto 1
%define _disable_rebuild_configure 1
%define _disable_ld_no_undefined 1

Name:		trousers
Summary:	TCG's Software Stack v1.2
Version:	0.3.15
Release:	1
License:	BSD
Group:		System/Libraries
Url:		http://trousers.sourceforge.net
Source0:	http://downloads.sourceforge.net/%{name}/%{name}-%{version}.tar.gz
Source1:	%{name}.sysusers
Source2:	https://src.fedoraproject.org/rpms/trousers/raw/rawhide/f/tcsd.service
Patch1:		https://src.fedoraproject.org/rpms/trousers/raw/rawhide/f/trousers-0.3.14-noinline.patch
# submitted upstream
Patch2:		https://src.fedoraproject.org/rpms/trousers/raw/rawhide/f/trousers-0.3.14-unlock-in-err-path.patch
Patch3:		https://src.fedoraproject.org/rpms/trousers/raw/rawhide/f/trousers-0.3.14-fix-indent-obj_policy.patch
Patch4:		https://src.fedoraproject.org/rpms/trousers/raw/rawhide/f/trousers-0.3.14-fix-indent-tspi_key.patch
BuildRequires:	pkgconfig(openssl)
Requires(pre):	systemd
%systemd_requires

%description
TrouSerS is an implementation of the Trusted Computing Group's Software Stack
(TSS) specification. You can use TrouSerS to write applications that make use
of your TPM hardware. TPM hardware can create, store and use RSA keys
securely (without ever being exposed in memory), verify a platform's software
state using cryptographic hashes and more.

%package -n %{libname}
Summary:	TrouSerS Shared libraries
Group:		System/Libraries

%description -n %{libname}
Shared libraries for TrouSerS.

%package -n %{develname}
Summary:	TrouSerS header files and documentation
Group:		Development/C
Requires:	%{libname} = %{version}-%{release}
Provides:	%{name}-devel = %{version}-%{release}

%description -n %{develname}
Header files and man pages for use in creating Trusted Computing enabled
applications.

%prep
%autosetup -p1
# fix man page paths
sed -i -e 's|/var/tpm|/var/lib/tpm|g' -e 's|/usr/local/var|/var|g' man/man5/tcsd.conf.5.in man/man8/tcsd.8.in

%build
chmod +x ./bootstrap.sh
./bootstrap.sh

%configure --with-gui=openssl
%make_build

%install
%make_install
rm -f %{buildroot}/%{_libdir}/libtspi.la
install -Dpm 644 %{SOURCE1} %{buildroot}%{_sysusersdir}/%{name}.conf
mkdir -p %{buildroot}%{_unitdir}
install -m 0644 %{SOURCE2} %{buildroot}%{_unitdir}/

%pre
%sysusers_create_package %{name}.conf %{SOURCE1}

%post
%systemd_post tcsd.service

%preun
%systemd_preun tcsd.service

%postun
%systemd_postun_with_restart tcsd.service 

%files
%doc README LICENSE ChangeLog
%{_sbindir}/tcsd
%{_sysusersdir}/%{name}.conf
%config(noreplace) %attr(0600, tss, tss) %{_sysconfdir}/tcsd.conf
%{_mandir}/man5/*
%{_mandir}/man8/*
%{_unitdir}/tcsd.service
%attr(0700, tss, tss) %{_localstatedir}/lib/tpm/

%files -n %{libname}
%{_libdir}/libtspi.so.%{major}
%{_libdir}/libtspi.so.%{major}.*

%files -n %{develname}
%doc doc/LTC-TSS_LLD_08_r2.pdf doc/TSS_programming_SNAFUs.txt
%{_libdir}/libtspi.so
%{_libdir}/libtddl.a
%{_includedir}/*
%{_mandir}/man3/Tspi_*
