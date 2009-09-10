%define eclipse_base %{_libdir}/eclipse
%define gcj_support 0
%define rlsdate 200809292108

Summary: AnyEdit plugin for eclipse
Name: eclipse-anyedit
Version: 2.1.1
Release: %mkrel 2
License: BSD
Group: Development/Other
URL: http://andrei.gmxhome.de/anyedit/index.html
Buildroot: %(mktemp -ud %{_tmppath}/%{name}-%{version}-%{release})

Source0: http://andrei.gmxhome.de/eclipse/plugins/de.loskutov.anyedit.AnyEditTools_%{version}.%{rlsdate}.jar
Source1: assemble.xml
Source2: package.xml
Source3: LICENSE

# work around unicode/compiler issue
Patch0: eclipse-anyedit-%{version}-unicode.patch

Requires: eclipse-platform >= 3.3
BuildRequires: jpackage-utils >= 0:1.5
BuildRequires: eclipse-pde
%if %{gcj_support}
BuildRequires:          java-gcj-compat-devel >= 1.0.33
Requires(post):         java-gcj-compat >= 1.0.33
Requires(postun):       java-gcj-compat >= 1.0.33
%else
BuildRequires:          java-devel >= 1.4.2
BuildArch:              noarch
%endif

%description
The AnyEdit plugin adds several new actions to the context menu of text-based
Eclipse editors.

%prep
%setup -q -c
%patch0 -p1

# remove pre-compiled classes
rm -rf de

# install license
install -m 644 %{SOURCE3} LICENSE

%build
# See comments in the script to understand this.
%if 0%{?rhel} == 5
/bin/sh -x %{_libdir}/eclipse/buildscripts/copy-platform SDK %{eclipse_base}
%else
/bin/sh -x %{eclipse_base}/buildscripts/copy-platform SDK %{eclipse_base}
%endif

SDK=$(cd SDK > /dev/null && pwd)

# Eclipse may write preferences and logs here
mkdir home
homedir=$(cd home > /dev/null && pwd)

# create the required assemble and package targets
mkdir $(pwd)/build/
# this symlink creates the assemble target which assembles the plugin
ln -s %{SOURCE1} $(pwd)/build/assemble.de.loskutov.anyedit.AnyEditTools.all.xml
# this symlink creates the package target which packages the plugin
ln -s %{SOURCE2} $(pwd)/build/package.de.loskutov.anyedit.AnyEditTools.all.xml

# find correct location
package_build=$(find %{eclipse_base} -name 'package-build' -print | grep pde | grep templates)
build_xml=$(find %{eclipse_base} -name 'build.xml' -print | grep pde | grep scripts)

# build the plugin
eclipse \
     -nosplash                                         \
     -application org.eclipse.ant.core.antRunner       \
     -Dtype=plugin                                     \
     -Did=de.loskutov.anyedit.AnyEditTools             \
     -DbaseLocation=$SDK                               \
     -DsourceDirectory=$(pwd)                          \
     -DbuildDirectory=$(pwd)/build                     \
     -Dbuilder=$package_build \
     -f $build_xml \
     -vmargs -Duser.home=$homedir

%install
rm -rf %{buildroot}

# create plugins directory
install -d -m 755 %{buildroot}/%{eclipse_base}/dropins/anyedit/plugins

# install plugin
install -m 644 de.loskutov.anyedit.AnyEditTools_%{version}.%{rlsdate}.jar \
  %{buildroot}/%{eclipse_base}/dropins/anyedit/plugins

%if %{gcj_support}
  %{_bindir}/aot-compile-rpm
%endif

%clean
rm -rf %{buildroot}

%if %{gcj_support}
%post
if [ -x %{_bindir}/rebuild-gcj-db ]
then
  %{_bindir}/rebuild-gcj-db
fi
%postun
if [ -x %{_bindir}/rebuild-gcj-db ]
then
  %{_bindir}/rebuild-gcj-db
fi
%endif

%files
%defattr(-,root,root,-)
%{eclipse_base}/dropins/anyedit/plugins/de.loskutov.anyedit.AnyEditTools_%{version}.%{rlsdate}.jar
%doc LICENSE
%if %{gcj_support}
%attr(-,root,root) %{_libdir}/gcj/%{name}
%endif
