Name:           kbd
Version:        2.6.3
Release:        1
Summary:        Tools for configuring the console (keyboard, virtual terminals, etc.)
License:        GPLv2+
URL:            http://kbd-project.org/
Source0:        %{name}-%{version}.tar.gz
Source1:        kbd-latarcyrheb-16-fixed.tar.bz2
# Patch0: puts additional information into man pages
Patch0:         kbd-1.15-keycodes-man.patch
# Patch2: adds default unicode font to unicode_start script
Patch2:         kbd-1.15-unicode_start.patch
# Patch3: fixes decimal separator in Swiss German keyboard layout, bz 882529
Patch3:         kbd-1.15.5-sg-decimal-separator.patch
# Patch4: adds xkb and legacy keymaps subdirs to loadkyes search path, bz 1028207
Patch4:         kbd-1.15.5-loadkeys-search-path.patch
# Patch5: don't hardcode font used in unicode_start, take it from vconsole.conf,
#   bz 1101007
Patch5:         kbd-2.0.2-unicode-start-font.patch
# Patch6: fixes issues found by static analysis
Patch6:         kbd-2.4.0-covscan-fixes.patch
Patch7:         kbd-1.15-disable-alt-tty-switch.patch

BuildRequires:  bison, flex, gettext, pam-devel

%description
The %{name} package contains tools for managing a Linux
system's console's behavior, including the keyboard, the screen
fonts, the virtual terminals and font files.


%package doc
Summary: Documentation for %{name}
Requires: kbd = %{version}-%{release}

%description doc
Documentation and man pages for %{name}.


%prep
%autosetup -p1 -n %{name}-%{version}/%{name} -a 1

# 7-bit maps are obsolete; so are non-euro maps
pushd data/keymaps/i386
cp qwerty/pt-latin9.map qwerty/pt.map
cp qwerty/sv-latin1.map qwerty/se-latin1.map

mv azerty/fr.map azerty/fr-old.map
cp azerty/fr-latin9.map azerty/fr.map

cp azerty/fr-latin9.map azerty/fr-latin0.map # legacy alias

# Rename conflicting keymaps
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
%configure --prefix=%{_prefix} --datadir=/lib/kbd --mandir=%{_mandir} --localedir=%{_datadir}/locale --enable-nls --disable-vlock
make %{?_smp_mflags}

%install
rm -rf $RPM_BUILD_ROOT
make install DESTDIR=$RPM_BUILD_ROOT

# ro_win.map.gz is useless
rm -f $RPM_BUILD_ROOT/lib/kbd/keymaps/i386/qwerty/ro_win.map.gz

# Create additional name for Serbian latin keyboard
ln -s sr-cy.map.gz $RPM_BUILD_ROOT/lib/kbd/keymaps/i386/qwerty/sr-latin.map.gz

# Create additional name for Chinese keyboard
ln -s us.map.gz $RPM_BUILD_ROOT/lib/kbd/keymaps/i386/qwerty/cn.map.gz

# The rhpl keyboard layout table is indexed by kbd layout names, so we need a
# Korean keyboard
ln -s us.map.gz $RPM_BUILD_ROOT/lib/kbd/keymaps/i386/qwerty/ko.map.gz

# Move binaries which we use before /usr is mounted from %{_bindir} to /bin.
mkdir -p $RPM_BUILD_ROOT/bin
for binary in setfont dumpkeys kbd_mode unicode_start unicode_stop loadkeys ; do
  mv $RPM_BUILD_ROOT%{_bindir}/$binary $RPM_BUILD_ROOT/bin/
done

# https://bugzilla.redhat.com/show_bug.cgi?id=2015972
# xkb Arabic layout is 'ara', not 'fa', langtable tells us to use 'ara'
ln -s fa.map.gz $RPM_BUILD_ROOT/lib/kbd/keymaps/i386/qwerty/ara.map.gz

# Some microoptimization
sed -i -e 's,\<kbd_mode\>,%{_bindir}/kbd_mode,g;s,\<setfont\>,%{_bindir}/setfont,g' \
        $RPM_BUILD_ROOT/bin/unicode_start

mkdir -p $RPM_BUILD_ROOT%{_docdir}/%{name}-%{version}
install -m0644 -t $RPM_BUILD_ROOT%{_docdir}/%{name}-%{version} \
        AUTHORS README ChangeLog docs/doc/kbd.FAQ*.html docs/doc/font-formats/*.html \
        docs/doc/utf/utf* docs/doc/dvorak/*

%find_lang %{name}

%files -f %{name}.lang
%defattr(-,root,root,-)
%license COPYING
/bin/*
%{_bindir}/*
%dir /lib/kbd
/lib/kbd/consolefonts
/lib/kbd/consoletrans
/lib/kbd/keymaps
/lib/kbd/unimaps

%files doc
%defattr(-, root, root, -)
%doc %{_docdir}/%{name}-%{version}
%{_mandir}/*/*
