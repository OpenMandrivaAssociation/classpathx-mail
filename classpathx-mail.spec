%global jmailver 1.3.1
%global inetlibver 1.1.2

Name:           classpathx-mail
Version:        1.1.2
Release:        11
Summary:        GNU JavaMail(tm)

Group:          System/Libraries
# Classpath library exception
License:        GPLv2+ with exceptions
URL:            http://www.gnu.org/software/classpathx/
Source0:        http://ftp.gnu.org/gnu/classpathx/mail-%{version}.tar.gz
Source1:        http://ftp.gnu.org/gnu/classpath/inetlib-%{inetlibver}.tar.gz
Patch0:         %{name}-add-inetlib.patch
# see bz157685
Patch3:         %{name}-remove-inetlib.patch

BuildArch:      noarch
BuildRequires:  jpackage-utils >= 0:1.5
BuildRequires:	java-1.6.0-openjdk-devel
BuildRequires:  ant
BuildRequires:  perl
BuildRequires:  java-javadoc
Requires(preun): chkconfig
Requires(post):  chkconfig
Provides:       javamail = 0:%{jmailver}

%description
GNU JavaMail(tm) is a free implementation of the JavaMail API.

%package        javadoc
Summary:        Javadoc for %{name}
Group:          Development/Java
Provides:       javamail-javadoc = 0:%{jmailver}
Requires:       jpackage-utils

%description    javadoc
%{summary}.


%prep
%setup -q -n mail-%{version} -a 1
%patch0
%patch3 -p0
rm -f libmail.so
#gzip -dc %{SOURCE1} | tar -xf -
pushd inetlib-%{inetlibver}/source/gnu/inet
sed -i -e "s|public final Logger logger|public final static Logger logger|g" imap/IMAPConnection.java nntp/NNTPConnection.java pop3/POP3Connection.java smtp/SMTPConnection.java
popd

%build
export JAVA_HOME=%_prefix/lib/jvm/java-1.6.0
export JAVAC=$JAVA_HOME/bin/javac
# build inetlib
pushd inetlib-%{inetlibver}
  %configure 
  %make
popd
mkdir classes
cp -r inetlib-%{inetlibver}/classes/gnu classes
# build mail
ant \
  -Dj2se.apidoc=%{_javadocdir}/java \
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
rm -rf %{buildroot}

install -dm 755 %{buildroot}%{_javadir}/classpathx-mail

# API
install -pm 644 gnumail.jar \
  %{buildroot}%{_javadir}/classpathx-mail/mail-%{jmailver}-api.jar
ln -s mail-%{jmailver}-api.jar \
  %{buildroot}%{_javadir}/classpathx-mail/mailapi.jar

# Providers
install -pm 644 gnumail-providers.jar \
  %{buildroot}%{_javadir}/classpathx-mail/mail-%{jmailver}-providers.jar
ln -s mail-%{jmailver}-providers.jar \
  %{buildroot}%{_javadir}/classpathx-mail/providers.jar
for prov in imap nntp pop3 smtp ; do
  ln -s mail-%{jmailver}-providers.jar \
    %{buildroot}%{_javadir}/classpathx-mail/$prov.jar
done

install -pm 644 monolithic.jar \
  %{buildroot}%{_javadir}/classpathx-mail-%{jmailver}-monolithic.jar
touch %{buildroot}%{_javadir}/javamail.jar # for %%ghost

install -dm 755 %{buildroot}%{_javadocdir}/%{name}-%{jmailver}
cp -pR docs/* %{buildroot}%{_javadocdir}/%{name}-%{jmailver}
ln -s %{name}-%{jmailver} %{buildroot}%{_javadocdir}/%{name} # ghost symlink

%triggerpostun -- classpathx-mail-monolithic <= 0:1.1.1-1jpp
# Remove file from old monolithic subpackage
rm -f %{_javadir}/javamail.jar
# Recreate the link as update-alternatives could not do it
ln -s %{_sysconfdir}/alternatives/javamail %{_javadir}/javamail.jar

%post
%{_sbindir}/update-alternatives --install %{_javadir}/javamail.jar javamail %{_javadir}/classpathx-mail-1.3.1-monolithic.jar 010301

%preun
if [ "$1" = "0" ]; then
    %{_sbindir}/update-alternatives --remove javamail %{_javadir}/classpathx-mail-1.3.1-monolithic.jar
fi

%files
%defattr(-,root,root,-)
%doc AUTHORS ChangeLog COPYING README README.*
%dir %{_javadir}/classpathx-mail
%{_javadir}/classpathx-mail/mail-%{jmailver}-api.jar
%{_javadir}/classpathx-mail/mailapi.jar
%{_javadir}/classpathx-mail/mail-%{jmailver}-providers.jar
%{_javadir}/classpathx-mail/providers.jar
%{_javadir}/classpathx-mail/imap.jar
%{_javadir}/classpathx-mail/nntp.jar
%{_javadir}/classpathx-mail/pop3.jar
%{_javadir}/classpathx-mail/smtp.jar
# Monolithic jar
%{_javadir}/classpathx-mail-%{jmailver}-monolithic.jar
%ghost %{_javadir}/javamail.jar

%files javadoc
%defattr(-,root,root,-)
%{_javadocdir}/%{name}-%{jmailver}
%{_javadocdir}/%{name}

