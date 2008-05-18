#
# Conditional build:
%bcond_without	dist_kernel	# without distribution kernel
%bcond_without	kernel		# don't build kernel modules
%bcond_without	userspace	# don't build userspace utilities
%bcond_with	verbose		# verbose build (V=1)

%if %{without kernel}
%undefine	with_dist_kernel
%endif
%if "%{_alt_kernel}" != "%{nil}"
%undefine	with_userspace
%endif
%if %{without userspace}
# nothing to be placed to debuginfo package
%define		_enable_debug_packages	0
%endif

%define		rel	64
%define		pname	submount
Summary:	Automatically mounts and unmounts removable media devices
Summary(pl.UTF-8):	Automatyczne montowanie i odmontowywanie wymiennych nośników danych
Name:		%{pname}%{_alt_kernel}
Version:	0.9
Release:	%{rel}
License:	GPL v2
Group:		Base/Kernel
Source0:	http://dl.sourceforge.net/submount/%{pname}-%{version}.tar.gz
# Source0-md5:	f6abac328dbfb265eff18561065575c6
Patch0:		%{pname}-subfs.patch
Patch1:		%{pname}-namespace.patch
URL:		http://submount.sourceforge.net/
%if %{with kernel}
%{?with_dist_kernel:BuildRequires:	kernel%{_alt_kernel}-module-build >= 3:2.6.7}
BuildRequires:	rpmbuild(macros) >= 1.379
%endif
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%description
Submount is a system for automatically mounting and unmounting
removable media drives like cdroms and floppy disk drives. It works
with the Linux 2.6 kernel series. Once installed, it allows removable
media drives to be accessed as if they were permanently mounted. In
the opposite to supermount doesn't require patching the kernel.

%description -l pl.UTF-8
Submount jest systemem automatycznego montowania i odmontowywania
wymiennych nośników danych, takich jak płyty CD-ROM czy dyskietki.
Działa z jądrami serii 2.6. Raz zainstalowany, umożliwia dostęp do
wymiennych nośników danych tak, jakby były one trwale montowane. W
przeciwieństwie do supermount nie wymaga łatania jądra.

%package -n kernel%{_alt_kernel}-fs-subfs
Summary:	Submount - kernel module
Summary(pl.UTF-8):	Submount - moduł jądra
Release:	%{rel}@%{_kernel_ver_str}
Group:		Base/Kernel
%{?with_dist_kernel:Requires:	kernel%{_alt_kernel}(vermagic) = %{_kernel_ver}}
Requires(post,postun):	/sbin/depmod

%description -n kernel%{_alt_kernel}-fs-subfs
This is a driver for Submount for Linux.

This package contains Linux module.

%description -n kernel%{_alt_kernel}-fs-subfs -l pl.UTF-8
Sterownik dla Linuksa do Submount.

Ten pakiet zawiera moduł jądra Linuksa.

%prep
%setup -q -n %{pname}-%{version}
%patch0 -p1
%patch1 -p1

%build
%if %{with kernel}
%build_kernel_modules -C subfs-%{version} -m subfs
%endif

%if %{with userspace}
cd submountd-%{version}
%configure
%{__make} \
	CFLAGS="%{rpmcflags}"
%endif

%install
rm -rf $RPM_BUILD_ROOT

%if %{with kernel}
%install_kernel_modules -m subfs-%{version}/subfs -d kernel/fs
%endif

%if %{with userspace}
install -d $RPM_BUILD_ROOT{/sbin,%{_mandir}/man8}
install submountd-%{version}/net-submountd $RPM_BUILD_ROOT/sbin
install submountd-%{version}/submountd $RPM_BUILD_ROOT/sbin
install submountd-%{version}/submount.8 $RPM_BUILD_ROOT%{_mandir}/man8
%endif

%clean
rm -rf $RPM_BUILD_ROOT

%post	-n kernel%{_alt_kernel}-fs-subfs
%depmod %{_kernel_ver}

%postun -n kernel%{_alt_kernel}-fs-subfs
%depmod %{_kernel_ver}

%if %{with userspace}
%files
%defattr(644,root,root,755)
%doc README submountd-%{version}/{AUTHORS,ChangeLog}
%attr(755,root,root) /sbin/*
%{_mandir}/man8/*
%endif

%if %{with kernel}
%files -n kernel%{_alt_kernel}-fs-subfs
%defattr(644,root,root,755)
/lib/modules/%{_kernel_ver}/kernel/fs/subfs.ko*
%endif
