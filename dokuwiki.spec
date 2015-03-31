%define dir_version  2014-09-29d
%define _localstatedir %{_var}
%define __noautoreq /usr/bin/php

Name:       dokuwiki
Version:    20140929
Release:    7
Summary:    A wiki with plain text files backend
License:    GPLv2
Group:      Networking/WWW
URL:        https://www.dokuwiki.org/dokuwiki
Source0:    http://download.dokuwiki.org/src/dokuwiki/%{name}-%{dir_version}.tgz
Requires:   apache-mod_php
Requires:   php-xml
BuildArch:  noarch

%description
DokuWiki is a standards compliant, simple to use Wiki, mainly aimed at creating
documentation of any kind. It is targeted at developer teams, workgroups and
small companies. It has a simple but powerful syntax which makes sure the
datafiles remain readable outside the Wiki and eases the creation of structured
texts. All data is stored in plain text files -- no database is required.

%prep
%setup -q -n %{name}-%{dir_version}
find . -name '.htaccess' | xargs rm -f

%build

%install
install -d -m 755 %{buildroot}%{_datadir}/%{name}

install -d -m 755 %{buildroot}%{_datadir}/%{name}/bin
install -m 755 bin/* %{buildroot}%{_datadir}/%{name}/bin

cp -pr inc %{buildroot}%{_datadir}/%{name}
cp -pr lib %{buildroot}%{_datadir}/%{name}

install -m 644 *.php %{buildroot}%{_datadir}/%{name}

pushd %{buildroot}%{_datadir}/%{name}
ln -sf ../../../var/lib/dokuwiki data
ln -sf ../../../etc/dokuwiki conf
popd

install -d -m 755 %{buildroot}%{_localstatedir}/lib
cp -pr data %{buildroot}%{_localstatedir}/lib/%{name}

install -d -m 755 %{buildroot}%{_sysconfdir}
cp -pr conf %{buildroot}%{_sysconfdir}/%{name}
rm -f %{buildroot}%{_sysconfdir}/%{name}/*.{dist,example}

# apache configuration
install -d -m 755 %{buildroot}%{_webappconfdir}
cat > %{buildroot}%{_webappconfdir}/%{name}.conf <<EOF
# %{name} Apache configuration
Alias /%{name} %{_datadir}/%{name}

<Directory %{_datadir}/%{name}>
    Require all granted
    DirectoryIndex doku.php
</Directory>

<Directory %{_datadir}/%{name}/bin>
    Require all denied
</Directory>

<Directory %{_datadir}/%{name}/inc>
    Require all denied
</Directory>

<Directory %{_datadir}/%{name}/conf>
    Require all denied
</Directory>

<Directory %{_datadir}/%{name}/data>
    Require all denied
</Directory>
EOF

cat > README.urpmi <<EOF
The setup used here differs from default one, to achieve better FHS compliance, and
follow upstream security recommandations detailed at
http://wiki.splitbrain.org/wiki:security:
- the non-variable files are in %{_datadir}/%{name}
- the variable files are in %{_localstatedir}/lib/%{name}
- the configuration files are in %{_sysconfdir}/%{name}
EOF
	
%pretrans
# fix for old lib setup
if [ -d %{_localstatedir}/www/%{name}/lib -a ! -L %{_localstatedir}/www/%{name}/lib ]; then
    cd %{_localstatedir}/www/%{name}
    find lib -type f | \
        tar --create --files-from - --remove-files | \
        (cd %{_datadir}/%{name} && tar --preserve --extract)
    rm -rf lib
    ln -sf ../../..%{_datadir}/%{name}/lib lib
fi


%pre
if [ $1 = "2" ]; then
    # fix for old setup
    if [ -d %{_localstatedir}/lib/%{name}/data ]; then
        mv %{_localstatedir}/lib/%{name}/data/* %{_localstatedir}/lib/%{name}
        rmdir %{_localstatedir}/lib/%{name}/data
    fi
fi

%files
%doc README VERSION README.urpmi conf/*.{dist,example}
%config(noreplace) %{_webappconfdir}/%{name}.conf
%attr(-,apache,apache) %config(noreplace) %{_sysconfdir}/%{name}
%{_datadir}/%{name}
%attr(-,apache,apache) %{_localstatedir}/lib/%{name}


