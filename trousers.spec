%define major 1
%define libname %mklibname %{name} %{major}
%define develname %mklibname %{name} -d

Summary:	Implementation of the TCG's Software Stack v1.1 Specification
Name:		trousers
Version:	0.3.0
Release:	%mkrel 1
License:	CPL
Group:		System/Servers
URL:		http://www.sf.net/projects/trousers
Source0:	http://downloads.sourceforge.net/trousers/%{name}-%{version}.tar.gz
Patch0:		trousers-no_werror.diff
Patch1:		trousers-mdv_conf.diff
BuildRequires:	libtool
BuildRequires:	autoconf2.5
BuildRequires:	gtk2-devel
BuildRequires:	openssl-devel
BuildRequires:	gmp-devel
Requires:	openssl
Requires(post): rpm-helper
Requires(preun): rpm-helper
Requires(pre): rpm-helper
Requires(postun): rpm-helper
BuildRoot:	%{_tmppath}/%{name}-%{version}-%{release}-root

%description
TrouSerS is an implementation of the Trusted Computing Group's Software Stack
(TSS) specification. You can use TrouSerS to write applications that make use
of your TPM hardware. TPM hardware can create, store and use RSA keys
securely (without ever being exposed in memory), verify a platform's software
state using cryptographic hashes and more.

%package -n	%{libname}
Summary:	Implementation of the TCG's Software Stack v1.1 Specification
Group:          System/Libraries

%description -n	%{libname}
TrouSerS is an implementation of the Trusted Computing Group's Software Stack
(TSS) specification. You can use TrouSerS to write applications that make use
of your TPM hardware. TPM hardware can create, store and use RSA keys
securely (without ever being exposed in memory), verify a platform's software
state using cryptographic hashes and more.

%package -n	%{develname}
Summary:	Static library and header files for the %{name} library
Group:		Development/C
Requires:	%{libname} = %{version}
Provides:	%{name}-devel = %{version}

%description -n	%{develname}
TrouSerS is an implementation of the Trusted Computing Group's Software Stack
(TSS) specification. You can use TrouSerS to write applications that make use
of your TPM hardware. TPM hardware can create, store and use RSA keys
securely (without ever being exposed in memory), verify a platform's software
state using cryptographic hashes and more.

This package contains the static %{name} library and its header files.

%prep

%setup -q
%patch0 -p0
%patch1 -p1

# weird bug
mkdir -p py/dist
touch py/dist/Makefile.in

%build
%serverbuild
libtoolize --copy --force; aclocal; automake --add-missing -copy --foreign; autoconf

%configure2_5x \
    --localstatedir=/var \
    --with-openssl=%{_prefix} \
    --with-gmp \
    --with-gui=gtk

%make

%install
rm -rf %{buildroot}

%makeinstall_std

# install some extra stuff
libtool --mode=install %{_bindir}/install -c -m 755 tools/ps_convert %{buildroot}%{_sbindir}
libtool --mode=install %{_bindir}/install -c -m 755 tools/ps_inspect %{buildroot}%{_sbindir}

install -d %{buildroot}%{_initrddir}
install -m0755 dist/fedora/fedora.initrd.tcsd %{buildroot}%{_initrddir}/tcsd

%pre
%_pre_useradd tss %{_localstatedir}/lib/tss /bin/sh

%post
%_post_service tcsd

%preun
%_preun_service tcsd

%postun
%_postun_userdel tss

%if %mdkversion < 200900
%post -n %{libname} -p /sbin/ldconfig
%endif

%if %mdkversion < 200900
%postun -n %{libname} -p /sbin/ldconfig
%endif

%clean
rm -rf %{buildroot}

%files
%defattr(-,root,root)
%attr(0755,root,root) %{_initrddir}/tcsd
%attr(0600,tss,tss) %config(noreplace) %{_sysconfdir}/tcsd.conf
%attr(0755,tss,tss) %{_sbindir}/tcsd
%attr(0755,root,root) %{_sbindir}/ps_convert
%attr(0755,root,root) %{_sbindir}/ps_inspect
%attr(0700,tss,tss) %dir %{_localstatedir}/lib/tpm
%{_mandir}/man5/*
%{_mandir}/man8/*

%files -n %{libname}
%defattr(-,root,root)
%doc AUTHORS ChangeLog LICENSE NICETOHAVES README README.selinux TODO doc/*
%{_libdir}/*.so.*

%files -n %{develname}
%defattr(-,root,root)
%{_libdir}/*.so
%{_libdir}/*.a
%{_libdir}/*.la
%dir %{_includedir}/tss
%dir %{_includedir}/trousers
%{_includedir}/tss/*.h
%{_includedir}/trousers/*.h
%{_mandir}/man3/Tspi_*
