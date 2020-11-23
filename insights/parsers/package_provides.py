"""
PackageProvides - commands ``/bin/echo {command_package}``
==========================================================

This command reads the output of the pre-command:

``for jp in `/bin/ps auxww | grep <cmd> | grep -v grep| awk '{print $11}' | sort -u`; do echo $jp `readlink -e $jp | xargs rpm -qf`; done``

This command looks for all versions of cmd running and tries to find the
RPM packages which provide them.  The running command and its package name
are stored as properties ``command`` and ``package`` of the object.

The reason why using above pre_command is that we need to record the links
between running_java_command and package which provides the java command. In
``ps aux`` output, we can only get what java command starts a java
application, instead of java package. Through this way, when there is jdk
bug, we can detect whether a running java application will be affected.

"""

from insights import parser, CommandParser
from insights.parsers import SkipException
from insights.specs import Specs
from insights.core.filters import add_filter


# The Parsers in this module depends on the `ps auxww` spec which needs 'filter'.
SUPPORTED_COMMANDS = [
    'httpd',
    'java',
]
add_filter(Specs.ps_auxww, SUPPORTED_COMMANDS)


class PackageProvidesCMD(CommandParser):
    """
    Base class to parse the output of the following command:

        for jp in `/bin/ps auxww | grep <cmd> | grep -v grep | awk '{print $11}' | sort -u`; do echo "$jp `readlink -e $jp | xargs rpm -qf`"; done

    Attributes:
        command (str): The java command that starts application.
        package (str): Java package that provides above java command.

    Raises:
        SkipException: If there is no java application running. Or, if running
            java command is not provided by package installed through yum or
            rpm.
    """

    def parse_content(self, content):
        if len(content) == 0:
            raise SkipException()

        l = content[0].split()

        if len(l) != 2:
            raise SkipException()

        self.command = l[0]
        self.package = l[1]


@parser(Specs.package_provides_java)
class PackageProvidesJava(PackageProvidesCMD):
    """
    Parse the output of command::

        for jp in `/bin/ps auxww | grep java | grep -v grep | awk '{print $11}' | sort -u`; do echo "$jp `readlink -e $jp | xargs rpm -qf`"; done

    Typical output of this command::

        /usr/lib/jvm/jre/bin/java java-1.8.0-openjdk-headless-1.8.0.141-3.b16.el6_9.x86_64

    Examples:
        >>> java_package.command
        '/usr/lib/jvm/jre/bin/java'
        >>> java_package.package
        'java-1.8.0-openjdk-headless-1.8.0.141-3.b16.el6_9.x86_64'
    """
    pass


@parser(Specs.package_provides_httpd)
class PackageProvidesHttpd(PackageProvidesCMD):
    """
    Parse the output of command::

        for jp in `/bin/ps auxww | grep java | grep -v grep | awk '{print $11}' | sort -u`; do echo "$jp `readlink -e $jp | xargs rpm -qf`"; done

    Typical output of this command::

        /opt/rh/httpd24/root/usr/sbin/httpd httpd24-httpd-2.4.34-7.el7.x86_64

    Examples:
        >>> httpd_package.command
        '/opt/rh/httpd24/root/usr/sbin/httpd'
        >>> httpd_package.package
        'httpd24-httpd-2.4.34-7.el7.x86_64'
    """
    pass
