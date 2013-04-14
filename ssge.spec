Name:		scap-security-guide-editor
Version:	1.0
Release:	1%{?dist}
Summary:	An editor for scap-security-guide project
License:	PostgreSQL
URL:		https://fedorahosted.org/scap-security-guide-editor/
Source0:	%{name}-%{version}.tar.bz2
BuildRoot:	%(mktemp -ud %{_tmppath}/%{name}-%{version}-%{release}-XXXXXX)
BuildArch:  noarch 
Requires:	python-flask git openscap-utils

%description
The scap-security-guide package contains a web-based XCCDF and OVAL editor.

%prep
%setup -q -c


%build


%install
rm -rf %{buildroot}
make install DESTDIR=%{buildroot}


%clean
rm -rf %{buildroot}


%files
%defattr(-,root,root,-)
%doc README
%doc LICENSE
%{_bindir}/ssge
/usr/share/ssge/


%changelog
* Sun Apr 14 2013 Petr Benas <pbenas@redhat.com> - 1.0-1
- initial packaging

