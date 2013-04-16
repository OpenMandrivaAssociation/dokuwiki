%define up_version  2011-05-25a
%define dir_version  2011-05-25a

%define _localstatedir %{_var}

Name:       dokuwiki
Version:    20110525a
Release:    3
Summary:    A wiki with plain text files backend
License:    GPLv2
Group:      Networking/WWW
Url:        http://wiki.splitbrain.org/wiki:dokuwiki 
Source:     http://www.splitbrain.org/_media/projects/dokuwiki/%{name}-%{up_version}.tgz
Requires:   mod_php
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



%files
%defattr(-,root,root)
%doc COPYING README VERSION README.urpmi conf/*.{dist,example}
%config(noreplace) %{_webappconfdir}/%{name}.conf
%attr(-,apache,apache) %config(noreplace) %{_sysconfdir}/%{name}
%{_var}/www/%{name}
%{_datadir}/%{name}
%attr(-,apache,apache) %{_localstatedir}/lib/%{name}


%changelog
* Thu Oct 06 2011 Andrey Bondrov <abondrov@mandriva.org> 20110525a-1mdv2012.0
+ Revision: 703319
- New version: 20110525a

* Sun Dec 05 2010 Oden Eriksson <oeriksson@mandriva.com> 20091225-3mdv2011.0
+ Revision: 610265
- rebuild

* Mon Mar 01 2010 Guillaume Rousse <guillomovitch@mandriva.org> 20091225-2mdv2010.1
+ Revision: 513174
- rely on filetrigger for reloading apache configuration begining with 2010.1, rpm-helper macros otherwise

* Thu Jan 21 2010 Frederik Himpe <fhimpe@mandriva.org> 20091225-1mdv2010.1
+ Revision: 494701
- Update to new version 2009-12-25c

* Fri Oct 09 2009 Jerome Martin <jmartin@mandriva.org> 20090214-2mdv2010.0
+ Revision: 456375
- Updated to release 2009-02-14b for security fix for a local file inclusion issue 1700 (CVE-2009-1960)
  Fixed installation bug #49532

* Tue Feb 17 2009 Jerome Martin <jmartin@mandriva.org> 20090214-1mdv2009.1
+ Revision: 341205
- version 2008-02-14

* Tue Sep 16 2008 Guillaume Rousse <guillomovitch@mandriva.org> 20080505-2mdv2009.0
+ Revision: 285147
- add php-xml dependency

* Mon Jun 30 2008 Guillaume Rousse <guillomovitch@mandriva.org> 20080505-1mdv2009.0
+ Revision: 230355
-use a nicer workaround for rpm bug (thanks Pixel)
-correct data files double inclusion
- new version
- workaround rpm bug when computing files list difference on upgrade (#41713)

  + Pixel <pixel@mandriva.com>
    - adapt to %%_localstatedir now being /var instead of /var/lib (#22312)

* Fri Feb 22 2008 Guillaume Rousse <guillomovitch@mandriva.org> 20070626b-2mdv2008.1
+ Revision: 173937
- fix FHS patch
- revert previous css location change, they are used indirectly by php code

* Fri Feb 22 2008 Guillaume Rousse <guillomovitch@mandriva.org> 20070626b-1mdv2008.1
+ Revision: 173924
- new version
- rediff FHS patch
- fix css location

  + Olivier Blin <blino@mandriva.org>
    - restore BuildRoot

* Mon Dec 17 2007 Thierry Vignaud <tv@mandriva.org> 20061106-1mdv2008.1
+ Revision: 124146
- kill re-definition of %%buildroot on Pixel's request


* Wed Dec 13 2006 Guillaume Rousse <guillomovitch@mandriva.org> 20061106-1mdv2007.0
+ Revision: 96213
- handle upgrade from previous setup
- new version
  use a patch to enforce FHS compliance instead of symlinks
  put all included files outside of web directory
  put data under /var/lib/dokuwiki directly, no need for an additional empty directory
  put sample configuration files under documentation
  provide README.urpmi about mdv specific setup
  cleanup spec file

  + jmartin <jmartin>
    - import dokuwiki-20060309-3mdv2007.0

* Fri Jun 30 2006 Jerome Martin <jmartin@mandriva.org> 20060309-3mdv2007.0
- Fix web directory to /var/www/dokuwiki

* Fri May 12 2006 Jerome Martin <jmartin@mandriva.org> 20060309-2mdk
- Fixed WebappsPolicy

* Thu Mar 23 2006 Jerome Martin <jmartin@mandriva.org> 20060309-1mdk
- Version 2006-03-09

* Mon Feb 06 2006 Jerome Martin <jmartin@mandriva.org> 20050922-1mdk
- New version

* Sun Jul 24 2005 Michael Scherer <misc@mandriva.org> 20050713-1mdk
- from roudoudou <roudoud0u@free.fr>
  - Initial Mandriva rpm package

