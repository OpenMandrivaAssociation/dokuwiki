%define name    dokuwiki
%define version 20061106
%define up_version	2006-11-06
%define release %mkrel 1

Name:       %{name}
Version:    %{version}
Release:    %{release}
Summary:    A wiki with plain text files backend
License:    GPL 
Group:	    Networking/WWW
Url:        http://wiki.splitbrain.org/wiki:dokuwiki 
Source:     http://www.splitbrain.org/_media/projects/dokuwiki/%{name}-%{up_version}.tar.bz2
Patch:      %{name}-%{version}-fhs.patch
Requires:   mod_php
# webapp macros and scriptlets
Requires(post):		rpm-helper >= 0.16
Requires(postun):	rpm-helper >= 0.16
BuildRequires:	rpm-helper >= 0.16
BuildRequires:	rpm-mandriva-setup >= 1.23
BuildArch:  noarch
BuildRoot:  %{_tmppath}/%{name}-%{version}

%description
DokuWiki is a standards compliant, simple to use Wiki, mainly aimed at creating
documentation of any kind. It is targeted at developer teams, workgroups and
small companies. It has a simple but powerful syntax which makes sure the
datafiles remain readable outside the Wiki and eases the creation of structured
texts. All data is stored in plain text files -- no database is required.

%prep
%setup -q -n %{name}-%{up_version}
%patch0 -p1
find . -name '.htaccess' | xargs rm -f

%build


%install
rm -rf %{buildroot}

install -d -m 755 %{buildroot}%{_var}/www/%{name}
install -m 644 *.php %{buildroot}%{_var}/www/%{name}

install -d -m 755 %{buildroot}%{_datadir}/%{name}
cp -pr bin %{buildroot}%{_datadir}/%{name}
cp -pr inc %{buildroot}%{_datadir}/%{name}

find lib -type f -regex '.*\.\(php\|ini\|js\|txt\|css\)' | \
    tar --create --files-from - --remove-files | \
    (cd %{buildroot}%{_datadir}/%{name} && tar --preserve --extract)
find lib -type f -not -regex '.*\.\(php\|ini\|js\|txt\|css\)' | \
    tar --create --files-from - --remove-files | \
    (cd %{buildroot}%{_var}/www/%{name} && tar --preserve --extract)
mv %{buildroot}%{_datadir}/%{name}/lib/exe %{buildroot}%{_var}/www/%{name}/lib

install -d -m 755 %{buildroot}%{_localstatedir}
cp -pr data %{buildroot}%{_localstatedir}/%{name}

install -d -m 755 %{buildroot}%{_sysconfdir}
cp -pr conf %{buildroot}%{_sysconfdir}/%{name}
rm -f %{buildroot}%{_sysconfdir}/%{name}/*.{dist,example}

# apache configuration
install -d -m 755 %{buildroot}%{_webappconfdir}
cat > %{buildroot}%{_webappconfdir}/%{name}.conf <<EOF
# %{name} Apache configuration
Alias /%{name} %{_var}/www/%{name}

<Directory %{_var}/www/%{name}>
    Allow from all
    DirectoryIndex doku.php
    DirectorySlash On 
</Directory>
EOF

cat > README.urpmi <<EOF
Mandriva RPM specific notes

setup
-----
The setup used here differs from default one, to achieve better FHS compliance.
- the files accessibles from the web are in %{_var}/www/%{name}
- the variable files are in %{_localstatedir}/%{name}
- the non-variable files are in %{_datadir}/%{name}
- the configuration files are in %{_sysconfdir}/%{name}
EOF
	
%clean
rm -rf %{buildroot}

%pre
if [ $1 = "2" ]; then
    # fix for old setup
    if [ -d %{_localstatedir}/%{name}/data ]; then
        mv %{_localstatedir}/%{name}/data/* %{_localstatedir}/%{name}
        rmdir %{_localstatedir}/%{name}/data
    fi
fi

%post
%_post_webapp

%postun
%_postun_webapp

%files
%defattr(-,root,root)
%doc COPYING README VERSION README.urpmi conf/*.{dist,example}
%config(noreplace) %{_webappconfdir}/%{name}.conf
%config(noreplace) %{_sysconfdir}/%{name}
%{_var}/www/%{name}
%{_datadir}/%{name}
%attr(-,apache,apache) %{_localstatedir}/%{name}


