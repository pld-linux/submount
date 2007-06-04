#
# Conditional build:
%bcond_without	dist_kernel	# without distribution kernel
%bcond_without	kernel		# don't build kernel modules
%bcond_without	up		# don't build UP module
%bcond_without	smp		# don't build SMP module
%bcond_without	userspace	# don't build userspace utilities
%bcond_with	verbose		# verbose build (V=1)
%bcond_with	grsec_kernel	# build for kernel-grsecurity
#
%if %{with kernel} && %{with dist_kernel} && %{with grsec_kernel}
%define	alt_kernel	grsecurity
%endif
#
%ifarch sparc
%undefine	with_smp
%endif
#
%define		_rel	52
Summary:	Automatically mounts and unmounts removable media devices
Summary(pl):	Automatyczne montowanie i odmontowywanie wymiennych no¶ników danych
Name:		submount
Version:	0.9
Release:	%{_rel}
License:	GPL v2
Group:		Base/Kernel
Source0:	http://dl.sourceforge.net/submount/%{name}-%{version}.tar.gz
# Source0-md5:	f6abac328dbfb265eff18561065575c6
Patch0:		%{name}-subfs.patch
URL:		http://submount.sourceforge.net/
%if %{with kernel}
%{?with_dist_kernel:BuildRequires:	kernel%{_alt_kernel}-module-build >= 3:2.6.7}
BuildRequires:	rpmbuild(macros) >= 1.308
%endif
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%description
Submount is a system for automatically mounting and unmounting
removable media drives like cdroms and floppy disk drives. It works
with the Linux 2.6 kernel series. Once installed, it allows removable
media drives to be accessed as if they were permanently mounted. In
the opposite to supermount doesn't require patching the kernel.

%description -l pl
Submount jest systemem automatycznego montowania i odmontowywania
wymiennych no¶ników danych, takich jak p³yty CD-ROM czy dyskietki.
Dzia³a z j±drami serii 2.6. Raz zainstalowany, umo¿liwia dostêp do
wymiennych no¶ników danych tak, jakby by³y one trwale montowane. W
przeciwieñstwie do supermount nie wymaga ³atania j±dra.

%package -n kernel%{_alt_kernel}-fs-subfs
Summary:	Submount - kernel module
Summary(pl):	Submount - modu³ j±dra
Release:	%{_rel}@%{_kernel_ver_str}
Group:		Base/Kernel
Requires(post,postun):	/sbin/depmod
%if %{with dist_kernel}
%requires_releq_kernel_up
Requires(postun):	%releq_kernel_up
%endif

%description -n kernel%{_alt_kernel}-fs-subfs
This is a driver for Submount for Linux.

This package contains Linux module.

%description -n kernel%{_alt_kernel}-fs-subfs -l pl
Sterownik dla Linuksa do Submount.

Ten pakiet zawiera modu³ j±dra Linuksa.

%package -n kernel%{_alt_kernel}-smp-fs-subfs
Summary:	Submount - SMP kernel module
Summary(pl):	Submount - modu³ j±dra SMP
Release:	%{_rel}@%{_kernel_ver_str}
Group:		Base/Kernel
Requires(post,postun):	/sbin/depmod
%if %{with dist_kernel}
%requires_releq_kernel_smp
Requires(postun):	%releq_kernel_smp
%endif

%description -n kernel%{_alt_kernel}-smp-fs-subfs
This is a driver for Submount for Linux.

This package contains Linux SMP module.

%description -n kernel%{_alt_kernel}-smp-fs-subfs -l pl
Sterownik dla Linuksa do Submount.

Ten pakiet zawiera modu³ j±dra Linuksa SMP.

%prep
%setup -q
%patch0 -p1

%build
%if %{with kernel}
cd subfs-%{version}
for cfg in %{?with_dist_kernel:%{?with_smp:smp} up}%{!?with_dist_kernel:nondist}; do
	if [ ! -r "%{_kernelsrcdir}/config-$cfg" ]; then
		exit 1
	fi
        install -d o/include/linux
        ln -sf %{_kernelsrcdir}/config-$cfg o/.config
        ln -sf %{_kernelsrcdir}/Module.symvers-$cfg o/Module.symvers
        ln -sf %{_kernelsrcdir}/include/linux/autoconf-$cfg.h o/include/linux/autoconf.h
        %{__make} -j1 -C %{_kernelsrcdir} O=$PWD/o prepare scripts
	%{__make} -C %{_kernelsrcdir} clean \
		RCS_FIND_IGNORE="-name '*.ko' -o" \
		M=$PWD O=$PWD/o \
		%{?with_verbose:V=1}
	%{__make} -C %{_kernelsrcdir} modules \
%if "%{_target_base_arch}" != "%{_arch}"
		ARCH=%{_target_base_arch} \
		CROSS_COMPILE=%{_target_base_cpu}-pld-linux- \
%endif
		HOSTCC="%{__cc}" \
		M=$PWD O=$PWD/o \
		%{?with_verbose:V=1}
	mv subfs.ko subfs-$cfg.ko
done
cd -
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
install -d $RPM_BUILD_ROOT/lib/modules/%{_kernel_ver}{,smp}/kernel/fs
cd subfs-%{version}
install subfs-%{?with_dist_kernel:up}%{!?with_dist_kernel:nondist}.ko \
	$RPM_BUILD_ROOT/lib/modules/%{_kernel_ver}/kernel/fs/subfs.ko
%if %{with smp} && %{with dist_kernel}
install subfs-smp.ko \
	$RPM_BUILD_ROOT/lib/modules/%{_kernel_ver}smp/kernel/fs/subfs.ko
%endif
cd -
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

%post	-n kernel%{_alt_kernel}-smp-fs-subfs
%depmod %{_kernel_ver}smp

%postun -n kernel%{_alt_kernel}-smp-fs-subfs
%depmod %{_kernel_ver}smp

%if %{with userspace}
%files
%defattr(644,root,root,755)
%doc README submountd-%{version}/{AUTHORS,ChangeLog}
%attr(755,root,root) /sbin/*
%{_mandir}/man8/*
%endif

%if %{with kernel}
%if %{with up} || %{without dist_kernel}
%files -n kernel%{_alt_kernel}-fs-subfs
%defattr(644,root,root,755)
/lib/modules/%{_kernel_ver}/kernel/fs/subfs.ko*
%endif

%if %{with smp} && %{with dist_kernel}
%files -n kernel%{_alt_kernel}-smp-fs-subfs
%defattr(644,root,root,755)
/lib/modules/%{_kernel_ver}smp/kernel/fs/subfs.ko*
%endif
%endif
