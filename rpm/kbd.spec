Name:           kbd
Version:        2.0.4
Release:        1
Summary:        Tools for configuring the console (keyboard, virtual terminals, etc.)

Group:          System/Base
License:        GPLv2+
URL:            http://kbd-project.org/
Source0:        https://git.kernel.org/pub/scm/linux/kernel/git/legion/kbd.git/snapshot/kbd-%{version}.tar.gz
Source1:        kbd-latarcyrheb-16-fixed.tar.bz2
Patch1:         kbd-1.15-keycodes-man.patch
Patch3:         kbd-1.15-unicode_start.patch
Patch7:         kbd-1.15-disable-alt-tty-switch.patch

BuildRequires:  bison, flex, gettext, pam-devel

%description
The %{name} package contains tools for managing a Linux
system's console's behavior, including the keyboard, the screen
fonts, the virtual terminals and font files.


%package doc
Summary: Documentation for %{name}
Group: Documentation
Requires: kbd = %{version}-%{release}

%description doc
Documentation and man pages for %{name}.


%prep
%setup -q -n %{name}-%{version}/%{name} -a 1
%patch1 -p1 -b .keycodes-man
%patch3 -p1 -b .unicode_start
%patch7 -p1

# 7-bit maps are obsolete; so are non-euro maps
pushd data/keymaps/i386
cp qwerty/pt-latin9.map qwerty/pt.map
cp qwerty/sv-latin1.map qwerty/se-latin1.map

mv azerty/fr.map azerty/fr-old.map
cp azerty/fr-latin9.map azerty/fr.map

cp azerty/fr-latin9.map azerty/fr-latin0.map # legacy alias

# Rename conflicting keymaps
mv dvorak/no.map dvorak/no-dvorak.map
mv fgGIod/trf.map fgGIod/trf-fgGIod.map
mv olpc/es.map olpc/es-olpc.map
mv olpc/pt.map olpc/pt-olpc.map
mv qwerty/cz.map qwerty/cz-qwerty.map
popd

# remove obsolete "gr" translation
pushd po
rm -f gr.po gr.gmo
popd

# Convert to utf-8
iconv -f iso-8859-1 -t utf-8 < "ChangeLog" > "ChangeLog_"
mv "ChangeLog_" "ChangeLog"

%build
./autogen.sh
%configure --prefix=%{_prefix} --datadir=/usr/lib/kbd --mandir=%{_mandir} --localedir=%{_datadir}/locale --enable-nls
make %{?_smp_mflags}

%install
rm -rf $RPM_BUILD_ROOT
make install DESTDIR=$RPM_BUILD_ROOT

# ro_win.map.gz is useless
rm -f $RPM_BUILD_ROOT/lib/kbd/keymaps/i386/qwerty/ro_win.map.gz

# Create additional name for Serbian latin keyboard
ln -s sr-cy.map.gz $RPM_BUILD_ROOT/usr/lib/kbd/keymaps/i386/qwerty/sr-latin.map.gz

# Create additional name for Chinese keyboard
ln -s us.map.gz $RPM_BUILD_ROOT/usr/lib/kbd/keymaps/i386/qwerty/cn.map.gz

# The rhpl keyboard layout table is indexed by kbd layout names, so we need a
# Korean keyboard
ln -s us.map.gz $RPM_BUILD_ROOT/usr/lib/kbd/keymaps/i386/qwerty/ko.map.gz

# Some microoptimization
sed -i -e 's,\<kbd_mode\>,/usr/bin/kbd_mode,g;s,\<setfont\>,/usr/bin/setfont,g' \
        $RPM_BUILD_ROOT/usr/bin/unicode_start

# Link open to openvt
ln -s openvt $RPM_BUILD_ROOT%{_bindir}/open
ln -s openvt.1.gz $RPM_BUILD_ROOT%{_mandir}/man1/open.1.gz

mkdir -p $RPM_BUILD_ROOT%{_docdir}/%{name}-%{version}
install -m0644 -t $RPM_BUILD_ROOT%{_docdir}/%{name}-%{version} \
	AUTHORS README ChangeLog docs/doc/kbd.FAQ*.html docs/doc/font-formats/*.html \
	docs/doc/utf/utf* docs/doc/dvorak/*

%find_lang %{name}

%files -f %{name}.lang
%defattr(-,root,root,-)
%license COPYING
%{_bindir}/*
%dir %{_libdir}/kbd
%{_libdir}/kbd/consolefonts
%{_libdir}/kbd/consoletrans
%{_libdir}/kbd/keymaps
%{_libdir}/kbd/unimaps

%files doc
%defattr(-, root, root, -)
%doc %{_docdir}/%{name}-%{version}
%{_mandir}/*/*
