#
# Conditional build:
%bcond_without	dist_kernel	# without distribution kernel
%bcond_without	kernel		# don't build kernel modules
%bcond_without	smp		# don't build SMP module
%bcond_without	userspace	# don't build userspace utilities
%bcond_with	verbose		# verbose build (V=1)
#
Summary:	Automatically mounts and unmounts removable media devices
Summary(pl):	Automatyczne montowanie i odmontowywanie wymiennych no¶ników danych
Name:		submount
Version:	0.9
%define		_rel	1
Release:	%{_rel}
License:	GPL v2
Group:		Base/Kernel
Source0:	http://dl.sourceforge.net/submount/%{name}-%{version}.tar.gz
# Source0-md5:	f6abac328dbfb265eff18561065575c6
URL:		http://submount.sourceforge.net/
%{?with_dist_kernel:BuildRequires:	kernel-module-build >= 2.6.7}
BuildRequires:	rpmbuild(macros) >= 1.217
Requires:	submount(kernel)
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%description
Submount is a system for automatically mounting and unmounting
removable media drives like cdroms and floppy disk drives. It works
with the Linux 2.6 kernel series. Once installed, it allows removable
media drives to be accessed as if they were permanently mounted.
In the opposite to supermount doesn't require patching the kernel.

%description -l pl
Submount jest systemem automatycznego montowania i odmontowywania
wymiennych no¶ników danych, takich jak p³yty CD-ROM czy dyskietki.
Dzia³a z j±drami serii 2.6. Raz zainstalowany, umo¿liwia dostêp do
wymiennych no¶ników danych tak, jakby by³y one trwale montowane. W
przeciwieñstwie do supermount nie wymaga ³atania j±dra.

%package -n kernel-misc-submount
Summary:	Submount - kernel module
Summary(pl):	Submount - modu³ j±dra
Release:	%{_rel}@%{_kernel_ver_str}
Group:		Base/Kernel
%{?with_dist_kernel:%requires_releq_kernel_up}
Requires(post,postun):	/sbin/depmod
Provides:	submount(kernel)

%description -n kernel-misc-submount
Submount - kernel module.

%description -n kernel-misc-submount -l pl
Submount - modu³ j±dra.

%package -n kernel-smp-misc-submount
Summary:	Submount - SMP kernel module
Summary(pl):	Submount - modu³ j±dra SMP
Release:	%{_rel}@%{_kernel_ver_str}
Group:		Base/Kernel
%{?with_dist_kernel:%requires_releq_kernel_smp}
Requires(post,postun):	/sbin/depmod
Provides:	submount(kernel)

%description -n kernel-smp-misc-submount
Submount - SMP kernel module.

%description -n kernel-smp-misc-submount -l pl
Submount - modu³ j±dra SMP.

%prep
%setup -q

%build
%if %{with kernel}
cd subfs-%{version}
for cfg in %{?with_dist_kernel:%{?with_smp:smp} up}%{!?with_dist_kernel:nondist}; do
	if [ ! -r "%{_kernelsrcdir}/config-$cfg" ]; then
		exit 1
	fi
	rm -rf include
	install -d include/{linux,config}
	ln -sf %{_kernelsrcdir}/config-$cfg .config
	ln -sf %{_kernelsrcdir}/include/linux/autoconf-$cfg.h include/linux/autoconf.h
	ln -sf %{_kernelsrcdir}/include/asm-%{_target_base_arch} include/asm
	ln -sf %{_kernelsrcdir}/Module.symvers-$cfg Module.symvers
%if %{without dist_kernel}
	ln -sf %{_kernelsrcdir}/scripts
%endif
	touch include/config/MARKER
	%{__make} -C %{_kernelsrcdir} clean \
		RCS_FIND_IGNORE="-name '*.ko' -o" \
		M=$PWD O=$PWD \
		%{?with_verbose:V=1}
	%{__make} -C %{_kernelsrcdir} modules \
		M=$PWD O=$PWD \
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

%post	-n kernel-misc-submount
%depmod %{_kernel_ver}

%postun -n kernel-misc-submount
%depmod %{_kernel_ver}

%post	-n kernel-smp-misc-submount
%depmod %{_kernel_ver}smp

%postun -n kernel-smp-misc-submount
%depmod %{_kernel_ver}smp

%if %{with userspace}
%files
%defattr(644,root,root,755)
%attr(755,root,root) /sbin/*
%{_mandir}/man8/*
%endif

%if %{with kernel}
%files -n kernel-misc-submount
%defattr(644,root,root,755)
/lib/modules/%{_kernel_ver}/kernel/fs/subfs.ko*

%if %{with smp} && %{with dist_kernel}
%files -n kernel-smp-misc-submount
%defattr(644,root,root,755)
/lib/modules/%{_kernel_ver}smp/kernel/fs/subfs.ko*
%endif
%endif
