Name:           kbd
Version:        1.15.3
Release:        1
Summary:        Tools for configuring the console (keyboard, virtual terminals, etc.)

Group:          System/Base
License:        GPLv2+
URL:            http://ftp.altlinux.org/pub/people/legion/kbd
Source0:        http://ftp.altlinux.org/pub/people/legion/kbd/kbd-%{version}.tar.gz
Source1:        kbd-latsun-fonts.tar.bz2
Source2:        ro_maps.tar.bz2
Source3:        kbd-latarcyrheb-16-fixed.tar.bz2
Patch1:         kbd-1.15-keycodes-man.patch
Patch3:         kbd-1.15-unicode_start.patch
Patch4:         kbd-1.15-resizecon-x86_64.patch
Patch6:         kbd-shutup-loadkeys.patch
Patch7:         kbd-1.15-disable-alt-tty-switch.patch
Patch8:         kbd-1.15.3-fix-es-translation.patch

BuildRequires:  bison, flex, gettext

%description
The %{name} package contains tools for managing a Linux
system's console's behavior, including the keyboard, the screen
fonts, the virtual terminals and font files.


%package doc
Summary: Documentation for kbd
Group: Documentation
Requires: kbd = %{version}-%{release}

%description doc
Documentation for kbd package


%prep
%setup -q -a 1 -a 2 -a 3
%patch1 -p1 -b .keycodes-man
%patch3 -p1 -b .unicode_start
%patch4 -p1 -b .resizecon_x86_64
%patch6 -p1 -b .shutup_loadkeys
%patch7 -p1 
%patch8 -p1

# 7-bit maps are obsolete; so are non-euro maps
pushd data/keymaps/i386
mv qwerty/fi.map qwerty/fi-old.map
cp qwerty/fi-latin9.map qwerty/fi.map
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
%configure --prefix=%{_prefix} --datadir=/lib/kbd --mandir=%{_mandir} --localedir=%{_datadir}/locale --enable-nls
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

# Some microoptimization
sed -i -e 's,\<kbd_mode\>,/bin/kbd_mode,g;s,\<setfont\>,/bin/setfont,g' \
        $RPM_BUILD_ROOT/bin/unicode_start

# Link open to openvt
ln -s openvt $RPM_BUILD_ROOT%{_bindir}/open

%find_lang %{name}

%files -f %{name}.lang
%defattr(-,root,root,-)
%doc AUTHORS README COPYING
/bin/*
%{_bindir}/*
%{_mandir}/*/*
/lib/kbd

%files doc
%doc AUTHORS README COPYING doc/kbd.FAQ*.html doc/font-formats/*.html doc/utf/utf* doc/dvorak/* ChangeLog

