# Copyright (c) 2000-2005, JPackage Project
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
#
# 1. Redistributions of source code must retain the above copyright
#    notice, this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright
#    notice, this list of conditions and the following disclaimer in the
#    documentation and/or other materials provided with the
#    distribution.
# 3. Neither the name of the JPackage Project nor the names of its
#    contributors may be used to endorse or promote products derived
#    from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
# A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
# OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
# LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
# DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
# THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#

#%define gcj_support %{?_with_gcj_support:1}%{!?_with_gcj_support:%{?_without_gcj_support:0}%{!?_without_gcj_support:%{?_gcj_support:%{_gcj_support}}%{!?_gcj_support:0}}}

%define gcj_support 1
%define jmailver 1.3.2
%define inetlibver 1.1.1

Name:           classpathx-mail
Version:        1.1.1
Release:        %mkrel 5
Epoch:          0
Summary:        GNU JavaMail(tm)

Group:          Development/Java
License:        LGPL-like
URL:            http://www.gnu.org/software/classpathx/
Source0:        http://ftp.gnu.org/gnu/classpathx/mail-%{version}.tar.gz
Source1:        http://ftp.gnu.org/gnu/classpath/inetlib-%{inetlibver}.tar.gz
# see bz157685
Patch1:         %{name}-docbuild.patch
Patch2:         %{name}-add-inetlib.patch
Patch3:         %{name}-remove-inetlib.patch
# see bz157685
Patch4:         classpath-inetlib-docbuild.patch
BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}-root
#Vendor:         JPackage Project
#Distribution:   JPackage

%if ! %{gcj_support}
BuildArch:      noarch
%endif
BuildRequires:  java-rpmbuild >= 0:1.5
BuildRequires:  ant
BuildRequires:  geronimo-jaf-1.0.2-api
BuildRequires:  perl
BuildRequires:  jce
# gnu-crypto is required for pre-1.5 JVMs only
BuildRequires:  gnu-crypto
#BuildRequires:  java-sasl
Requires:       geronimo-jaf-1.0.2-api
Requires:       jce
Requires:       java-sasl
Requires(preun):  update-alternatives
Requires(post):  update-alternatives
Provides:       javamail = 0:%{jmailver}
# For backward compatibility with former monolithic subpackages
Provides:       javamail-monolithic = 0:%{jmailver}
Obsoletes:      classpathx-mail-monolithic <= 0:1.1.1_2jpp_6rh

%if %{gcj_support}
BuildRequires:  java-gcj-compat-devel
%endif

%description
GNU JavaMail(tm) is a free implementation of the JavaMail API.

%package        javadoc
Summary:        Javadoc for %{name}
Group:          Development/Java
Provides:       javamail-javadoc = 0:%{jmailver}
BuildRequires:  java-javadoc, jaf-javadoc

%description    javadoc
%{summary}.


%prep
%setup -q -n mail-%{version}
%patch1 -p0
%patch2 -p0
%patch3 -p0
rm -f libmail.so
gzip -dc %{SOURCE1} | tar -xf -
pushd inetlib-%{inetlibver}
%patch4 -p0
  mkdir -p source/org/jpackage/mail
  mv source/gnu/inet source/org/jpackage/mail
popd
# assume no filename contains spaces
%{__perl} -p -i -e 's/gnu(.)inet/org${1}jpackage${1}mail${1}inet/' `grep gnu.inet -lr *`


%build
# build inetlib
pushd inetlib-%{inetlibver}
  # FIXME: why are these missing?
  export CLASSPATH=$(build-classpath jce sasl 2>/dev/null)
  %{ant} -Dj2se.apidoc=%{_javadocdir}/java inetlib.jar doc
popd
mkdir classes
cp -r inetlib-%{inetlibver}/classes/org classes
# build mail
export CLASSPATH=$(build-classpath activation)
%{ant} \
  -Dj2se.apidoc=%{_javadocdir}/java \
  -Djaf.apidoc=%{_javadocdir}/jaf \
  dist javadoc

# build monolithic
mkdir monolithic
pushd monolithic
for jar in gnumail gnumail-providers ; do jar xf ../$jar.jar; done
rm -f META-INF/MANIFEST.MF
jar cf ../monolithic.jar *
popd
rm -Rf monolithic


%install
rm -rf $RPM_BUILD_ROOT

install -dm 755 $RPM_BUILD_ROOT%{_javadir}/classpathx-mail

# API
install -pm 644 gnumail.jar \
  $RPM_BUILD_ROOT%{_javadir}/classpathx-mail/mail-%{jmailver}-api-%{version}.jar
ln -s mail-%{jmailver}-api-%{version}.jar \
  $RPM_BUILD_ROOT%{_javadir}/classpathx-mail/mail-%{jmailver}-api.jar
ln -s mail-%{jmailver}-api.jar \
  $RPM_BUILD_ROOT%{_javadir}/classpathx-mail/mailapi.jar

# Providers
install -pm 644 gnumail-providers.jar \
  $RPM_BUILD_ROOT%{_javadir}/classpathx-mail/mail-%{jmailver}-providers-%{version}.jar
ln -s mail-%{jmailver}-providers-%{version}.jar \
  $RPM_BUILD_ROOT%{_javadir}/classpathx-mail/mail-%{jmailver}-providers.jar
ln -s mail-%{jmailver}-providers.jar \
  $RPM_BUILD_ROOT%{_javadir}/classpathx-mail/providers.jar
for prov in imap nntp pop3 smtp ; do
  ln -s mail-%{jmailver}-providers.jar \
    $RPM_BUILD_ROOT%{_javadir}/classpathx-mail/$prov-%{jmailver}.jar
  ln -s providers.jar $RPM_BUILD_ROOT%{_javadir}/classpathx-mail/$prov.jar
done

install -pm 644 monolithic.jar \
  $RPM_BUILD_ROOT%{_javadir}/classpathx-mail-%{jmailver}-monolithic-%{version}.jar
ln -s classpathx-mail-%{jmailver}-monolithic-%{version}.jar $RPM_BUILD_ROOT%{_javadir}/classpathx-mail-%{jmailver}-monolithic.jar
touch $RPM_BUILD_ROOT%{_javadir}/javamail.jar # for %ghost

install -dm 755 $RPM_BUILD_ROOT%{_javadocdir}/%{name}-%{jmailver}
cp -pR docs/* $RPM_BUILD_ROOT%{_javadocdir}/%{name}-%{jmailver}
ln -s %{name}-%{jmailver} $RPM_BUILD_ROOT%{_javadocdir}/%{name} # ghost symlink


%if %{gcj_support}
%{_bindir}/aot-compile-rpm
%endif

%clean
rm -rf $RPM_BUILD_ROOT


%triggerpostun -- classpathx-mail-monolithic <= 0:1.1.1-1jpp
# Remove file from old monolithic subpackage
rm -f %{_javadir}/javamail.jar
# Recreate the link as update-alternatives could not do it
ln -s %{_sysconfdir}/alternatives/javamail %{_javadir}/javamail.jar

%post
%{_sbindir}/update-alternatives --install %{_javadir}/javamail.jar javamail %{_javadir}/classpathx-mail-%{jmailver}-monolithic.jar 10300

%if %{gcj_support}
if [ -x %{_bindir}/rebuild-gcj-db ]
then
  %{_bindir}/rebuild-gcj-db
fi
%endif

%if %{gcj_support}
%postun
if [ -x %{_bindir}/rebuild-gcj-db ]
then
  %{_bindir}/rebuild-gcj-db
fi
%endif

%preun
if [ "$1" = "0" ]; then
    %{_sbindir}/update-alternatives --remove javamail %{_javadir}/classpathx-mail-%{jmailver}-monolithic.jar
fi

%post javadoc
rm -f %{_javadocdir}/%{name}
ln -s %{name}-%{jmailver} %{_javadocdir}/%{name}

%postun javadoc
if [ "$1" = "0" ]; then
    rm -f %{_javadocdir}/%{name}
fi


%files
%defattr(644,root,root,755)
%doc AUTHORS ChangeLog COPYING
%dir %{_javadir}/classpathx-mail
%{_javadir}/classpathx-mail/mail-%{jmailver}-api-%{version}.jar
%{_javadir}/classpathx-mail/mail-%{jmailver}-api.jar
%{_javadir}/classpathx-mail/mailapi.jar
%{_javadir}/classpathx-mail/mail-%{jmailver}-providers-%{version}.jar
%{_javadir}/classpathx-mail/mail-%{jmailver}-providers.jar
%{_javadir}/classpathx-mail/providers.jar
%{_javadir}/classpathx-mail/imap-%{jmailver}.jar
%{_javadir}/classpathx-mail/imap.jar
%{_javadir}/classpathx-mail/nntp-%{jmailver}.jar
%{_javadir}/classpathx-mail/nntp.jar
%{_javadir}/classpathx-mail/pop3-%{jmailver}.jar
%{_javadir}/classpathx-mail/pop3.jar
%{_javadir}/classpathx-mail/smtp-%{jmailver}.jar
%{_javadir}/classpathx-mail/smtp.jar
# Monolithic jar
%{_javadir}/classpathx-mail-%{jmailver}-monolithic-%{version}.jar
%{_javadir}/classpathx-mail-%{jmailver}-monolithic.jar
%ghost %{_javadir}/javamail.jar

%if %{gcj_support}
%attr(-,root,root) %{_libdir}/gcj/%{name}/classpathx-mail-%{jmailver}-monolithic-%{version}.jar.*
# These ones are included in the monolithic one above
#%attr(-,root,root) %{_libdir}/gcj/%{name}/mail-%{jmailver}-api-%{version}.jar.*
#%attr(-,root,root) %{_libdir}/gcj/%{name}/mail-%{jmailver}-providers-%{version}.jar.*
%endif

%files javadoc
%defattr(644,root,root,755)
%doc %{_javadocdir}/%{name}-%{jmailver}
%doc %dir %{_javadocdir}/%{name}


