%define name    dokuwiki
%define version 20110525a
%define up_version  2011-05-25a
%define dir_version  2011-05-25a
%define release %mkrel 1

%define _localstatedir %{_var}

Name:       %{name}
Version:    %{version}
Release:    %{release}
Summary:    A wiki with plain text files backend
License:    GPLv2
Group:      Networking/WWW
Url:        http://wiki.splitbrain.org/wiki:dokuwiki 
Source:     http://www.splitbrain.org/_media/projects/dokuwiki/%{name}-%{up_version}.tgz
Requires:   mod_php
Requires:   php-xml
%if %mdkversion < 201010
Requires(post):   rpm-helper
Requires(postun):   rpm-helper
%endif
BuildArch:  noarch
BuildRoot:  %{_tmppath}/%{name}-%{version}

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
rm -rf %{buildroot}

install -d -m 755 %{buildroot}%{_var}/www/%{name}
install -m 644 *.php %{buildroot}%{_var}/www/%{name}
(cd %{buildroot}%{_var}/www/%{name} && ln -sf ../../..%{_datadir}/%{name}/lib .)

cat > %{buildroot}%{_var}/www/%{name}/prepend.php <<'EOF'
<?php
define('DOKU_CONF','%{_sysconfdir}/%{name}/');
define('DOKU_LOCAL','%{_sysconfdir}/%{name}/');
define('DOKU_INC','%{_datadir}/%{name}/');
define('DOKU_DATA','%{_localstatedir}/lib/%{name}/');
EOF

install -d -m 755 %{buildroot}%{_datadir}/%{name}
cp -pr bin %{buildroot}%{_datadir}/%{name}
chmod +x %{buildroot}%{_datadir}/%{name}/bin/*
cp -pr inc %{buildroot}%{_datadir}/%{name}
cp -pr lib %{buildroot}%{_datadir}/%{name}

install -d -m 755 %{buildroot}%{_localstatedir}/lib
cp -pr data %{buildroot}%{_localstatedir}/lib/%{name}

install -d -m 755 %{buildroot}%{_sysconfdir}
cp -pr conf %{buildroot}%{_sysconfdir}/%{name}
rm -f %{buildroot}%{_sysconfdir}/%{name}/*.{dist,example}
perl -pi -e 's|./data|%{_localstatedir}/lib/%{name}|' %{buildroot}%{_sysconfdir}/%{name}/dokuwiki.php


# apache configuration
install -d -m 755 %{buildroot}%{_webappconfdir}
cat > %{buildroot}%{_webappconfdir}/%{name}.conf <<EOF
# %{name} Apache configuration
Alias /%{name} %{_var}/www/%{name}

<Directory %{_var}/www/%{name}>
    Order allow,deny
    Allow from all
    Options FollowSymLinks
    DirectoryIndex doku.php
    php_value auto_prepend_file %{_var}/www/%{name}/prepend.php
</Directory>
EOF

cat > README.urpmi <<EOF
Mandriva RPM specific notes

setup
-----
The setup used here differs from default one, to achieve better FHS compliance, and
follow upstream security recommandations detailed at
http://wiki.splitbrain.org/wiki:security:
- the files accessibles from the web are in %{_var}/www/%{name}
- the variable files are in %{_localstatedir}/lib/%{name}
- the non-variable files are in %{_datadir}/%{name}
- the configuration files are in %{_sysconfdir}/%{name}
EOF
	
%clean
rm -rf %{buildroot}

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

%post
%if %mdkversion < 201010
%_post_webapp
%endif

%postun
%if %mdkversion < 201010
%_postun_webapp
%endif

%files
%defattr(-,root,root)
%doc COPYING README VERSION README.urpmi conf/*.{dist,example}
%config(noreplace) %{_webappconfdir}/%{name}.conf
%attr(-,apache,apache) %config(noreplace) %{_sysconfdir}/%{name}
%{_var}/www/%{name}
%{_datadir}/%{name}
%attr(-,apache,apache) %{_localstatedir}/lib/%{name}
