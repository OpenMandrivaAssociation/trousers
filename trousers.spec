%define major 1
%define libname %mklibname tspi %{major}
%define develname %mklibname -d %{name}

%define _disable_lto 1
%define _disable_rebuild_configure 1
%define _disable_ld_no_undefined 1

Name:		trousers
Summary:	TCG's Software Stack v1.2
Version:	0.3.13
Release:	4
License:	BSD
Group:		System/Libraries
Url:		http://trousers.sourceforge.net
Source0:	http://downloads.sourceforge.net/%{name}/%{name}-%{version}.tar.gz
Source1:	tcsd.service
Patch1:		trousers-0.3.13-mga-noinline.patch
Patch2:		trousers-openssl1.1.patch
BuildRequires:	openssl-devel

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
%setup -q
%apply_patches
# fix man page paths
sed -i -e 's|/var/tpm|/var/lib/tpm|g' -e 's|/usr/local/var|/var|g' man/man5/tcsd.conf.5.in man/man8/tcsd.8.in

%build
%configure --with-gui=openssl
%make

%install
%makeinstall_std
rm -f %{buildroot}/%{_libdir}/libtspi.la
mkdir -p %{buildroot}%{_unitdir}
install -m 0644 %{SOURCE1} %{buildroot}%{_unitdir}/

%pre
%_pre_useradd tss /dev/null /bin/false

%post
%_post_service tcsd

%preun
%_preun_service tcsd

%postun
%_postun_userdel tss

%files
%doc README LICENSE ChangeLog
%{_sbindir}/tcsd
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
