"""
    ffm.py by @JusticeRage and @ice-wzl

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""
import time
from commands.command_manager import register_plugin
from model.plugin.command import Command
from model.driver.input_api import *

# -----------------------------------------------------------------------------

class GetOS(Command):
    def __init__(self, *args, **kwargs):
        pass

    @staticmethod
    def regexp():
        return r"^\s*\!os($| )"

    @staticmethod
    def name():
        return "!os"

    @staticmethod
    def description():
        return "Prints the distribution of the current machine."
    
    @staticmethod
    def tag():
        return "Enumeration"

    @staticmethod
    def usage():
        return "Usage: !os"

    def execute(self):
        shell_exec("cat /etc/*release*", print_output=True)

# -----------------------------------------------------------------------------

class PtySpawn(Command):
    def __init__(self, *args, **kwargs):
        pass

    @staticmethod
    def regexp():
        return r"^\s*!pty($| )"

    @staticmethod
    def name():
        return "!pty"

    @staticmethod
    def description():
        return "Spawns a PTY in the current shell."
    
    @staticmethod
    def tag():
        return "Stealth"

    @staticmethod
    def usage():
        return "Usage: !pty"

    def execute(self):
        if context.active_session.input_driver.last_line:
            raise RuntimeError("A TTY already seems to be present.")

        pass_command("script /dev/null")
        # Sleep a little bit to allow the pty to be created.
        time.sleep(0.2)
        pass_command("unset HISTFILE HISTFILESIZE HISTSIZE PROMPT_COMMAND")
        pass_command("stty -echo")
        pass_command("export TERM=xterm")
        pass_command("unset SSH_CONNECTION")

# -----------------------------------------------------------------------------

class Debug(Command):
    def __init__(self, *args, **kwargs):
        pass

    @staticmethod
    def regexp():
        return r"^\s*!dbg($| )"

    @staticmethod
    def name():
        return "!dbg"

    @staticmethod
    def description():
        return "Prints debug information."
    
    @staticmethod
    def tag():
        return "Help"

    @staticmethod
    def usage():
        return "Usage: !dbg"

    def execute(self):
        write_str("Current command prompt: %s\r\n" %
                  context.active_session.input_driver.last_line.encode("UTF-8"), LogLevel.WARNING)

# -----------------------------------------------------------------------------

class Suid(Command):
    def __init__(self, *args, **kwargs):
        pass

    @staticmethod
    def regexp():
        return r"^\s*\!suid($| )"

    @staticmethod
    def name():
        return "!suid"

    @staticmethod
    def description():
        return "Finds SUID, SGID binaries on the current machine."
    
    @staticmethod
    def tag():
        return "Enumeration"

    @staticmethod
    def usage():
        return "Usage: !suid"

    def execute(self):
        write_str("SUID + SGID Binaries: \r\n", LogLevel.WARNING)
        shell_exec("find / -perm -4000 -type f ! -path '/dev/*' -exec ls -la {} \; 2>/dev/null; find / -perm -4000 -type f ! -path '/dev/*' -exec ls -la {} \; 2>/dev/null", print_output=True)

class Info(Command):
    def __init__(self, *args, **kwargs):
        pass

    @staticmethod
    def regexp():
        return r"^\s*\!info($| )"

    @staticmethod
    def name():
        return "!info"

    @staticmethod
    def description():
        return "Returns CPU(s), Architecture, Memory, and Kernel Verison for the current machine."
    
    @staticmethod
    def tag():
        return "Enumeration"

    @staticmethod
    def usage():
        return "Usage: !info"

    def execute(self):
        write_str("System Info: \r\n", LogLevel.WARNING)
        shell_exec('uptime -p | grep "up" | tr -s " " &&  lscpu | grep "^CPU(s)" | tr -s " " && lscpu | grep "^Architecture" | tr -s " " && echo "Kernel Version: $(uname -r)" && lsmem | grep "^Total online memory:" | tr -s " "', print_output=True)

# -----------------------------------------------------------------------------
class SshKeys(Command):
    def __init__(self, *args, **kwargs):
        pass

    @staticmethod
    def regexp():
        return r"^\s*\!sshkeys($| )"

    @staticmethod
    def name():
        return "!sshkeys"

    @staticmethod
    def description():
        return "Hunts for Private and Public SSH keys on the current machine."
    
    @staticmethod
    def tag():
        return "Enumeration"

    @staticmethod
    def usage():
        return "Usage: !sshkeys"

    def execute(self):
        write_str("Potential SSH Keys: \r\n", LogLevel.WARNING)
        shell_exec('find / -type f -name "*.pub" 2>/dev/null; find / -type f -name "authorized_keys" 2>/dev/null; find / -type f -name "*_rsa" 2>/dev/null; find / -type f -name "*_ecsa" 2>/dev/null; find / -type f -name "*_ed25519" 2>/dev/null; find / -type f -name "*_dsa" 2>/dev/null', print_output=True)
        
# -----------------------------------------------------------------------------

class DBHunter(Command):
    def __init__(self, *args, **kwargs):
        pass

    @staticmethod
    def regexp():
        return r"^\s*\!db-hunter($| )"

    @staticmethod
    def name():
        return "!db-hunter"

    @staticmethod
    def description():
        return "Hunts for .sqlite, .sqlite3, and .db files"
    
    @staticmethod
    def tag():
        return "Enumeration"

    @staticmethod
    def usage():
        return "Usage: !db-hunter"

    def execute(self):
        write_str("DB Hunter: \r\n", LogLevel.WARNING)
        shell_exec("find / -name '*.db' -o -name '*.sqlite' -o -name '*.sqlite3' 2>/dev/null | grep -v /var/cache/man", print_output=True)

# -----------------------------------------------------------------------------

class BackupHunter(Command):
    def __init__(self, *args, **kwargs):
        pass

    @staticmethod
    def regexp():
        return r"^\s*\!backup-hunter($| )"

    @staticmethod
    def name():
        return "!backup-hunter"

    @staticmethod
    def description():
        return "Hunts for backup files"
    
    @staticmethod
    def tag():
        return "Enumeration"

    @staticmethod
    def usage():
        return "Usage: !backup-hunter"

    def execute(self):
        write_str("Backup Hunter: \r\n", LogLevel.WARNING)
        shell_exec('find /var /etc /bin /sbin /home /usr/local/bin /usr/local/sbin /usr/bin /usr/games /usr/sbin /root /tmp -type f \( -name "*backup*" -o -name "*\.bak" -o -name "*\.bck" -o -name "*\.bk" \) 2>/dev/null', print_output=True)

# -----------------------------------------------------------------------------
class Mtime(Command):
    def __init__(self, *args, **kwargs):
        self.time = None
        if len(args) == 2:
            self.time = args[1]
        else:
            raise RuntimeError("Received %d argument(s), expected 2." % len(args))
        
    @staticmethod
    def regexp():
        return r"^\s*\!mtime($| )"

    @staticmethod
    def name():
        return "!mtime"

    @staticmethod
    def description():
        return "Returns files modified in the last X minutes"
    
    @staticmethod
    def tag():
        return "Enumeration"

    @staticmethod
    def usage():
        return "Usage: !mtime 5"

    def execute(self):
        shell_exec('find / -type f -mmin -{} ! -path "/proc/*" ! -path "/sys/*" ! -path "/run/*" ! -path "/dev/*" ! -path "/var/lib/*" 2>/dev/null'.format(self.time), print_output=True)
        write_str("Module Complete.\r\n", LogLevel.WARNING)

#sudo -V | grep "Sudo ver" | grep "1\.[01234567]\.[0-9]\+\|1\.8\.1[0-9]\*\|1\.8\.2[01234567]"
class SudoV(Command):
    def __init__(self, *args, **kwargs):
        pass

    @staticmethod
    def regexp():
        return r"^\s*\!sudo-version($| )"

    @staticmethod
    def name():
        return "!sudo-version"

    @staticmethod
    def description():
        return "Checks for a vulnerable sudo version"
    
    @staticmethod
    def tag():
        return "Enumeration"

    @staticmethod
    def usage():
        return "Usage: !sudo-version"
#this function needs more testing and some reworking, but it is a MVP
    def execute(self):
        #bash command will hit off sudo version and return output
        test_sudo = shell_exec('sudo -V | grep "Sudo ver" | grep "1\.[01234567]\.[0-9]\+\|1\.8\.1[0-9]\*\|1\.8\.2[01234567]"', print_output=False)
        if len(test_sudo) == 0:
            write_str("Sudo Version is likely NOT Vulnerable\r\n", LogLevel.WARNING)
        elif "not found" in test_sudo:
            write_str("Sudo not found, are you in a container?\r\n", LogLevel.WARNING)
        else:
            write_str("Sudo Version might be Vulnerable, examine further\r\n", LogLevel.ERROR)

register_plugin(GetOS)
register_plugin(PtySpawn)
register_plugin(Debug)
register_plugin(Suid)
register_plugin(Info)
register_plugin(SshKeys)
register_plugin(DBHunter)
register_plugin(Mtime)
register_plugin(BackupHunter)
register_plugin(SudoV)