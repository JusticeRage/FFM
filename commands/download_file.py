"""
    FFM by @JusticeRage

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
import hashlib
import re
import tqdm

from model.command.command import Command
from model.driver.input_api import *
from commands.command_manager import register_plugin


class Download(Command):
    def __init__(self, *args, **kwargs):
        if len(args) < 2:
            raise RuntimeError("Received %d argument(s), expected 3." % len(args))
        elif len(args) == 2:
            self.destination = os.path.basename(args[1])
        else:
            self.destination = args[2]

        if os.path.exists(self.destination):
            raise RuntimeError("%s already exists! Aborting." % self.destination)

        if not file_exists(args[1]):
            raise RuntimeError("%s not found!" % args[1])
        self.target_file = args[1]

    @staticmethod
    def regexp():
        return r"^\!download"

    @staticmethod
    def usage():
        write_str("Usage: !upload [local file] [remote destination]\r\n", LogLevel.WARNING)

    @staticmethod
    def name():
        return "!download"

    @staticmethod
    def description():
        return "Downloads a file from the remote machine."

    def execute(self):
        file_size = int(shell_exec('stat -c "%%s" %s' % self.target_file, False))
        bytes_read = 0
        md5 = hashlib.md5()
        with open(self.destination, 'wb') as f:
            with tqdm.tqdm(total=file_size, unit="o", unit_scale=True) as progress_bar:
                while bytes_read < file_size:
                    chunk_size = min(2048, file_size - bytes_read)
                    data = shell_exec("xxd -p -l%d -s%d %s" % (chunk_size, bytes_read, self.target_file), False)
                    data = re.sub(r"\r|\n|\r\n", "", data)  # Strip newlines from xxd output.
                    data = bytearray.fromhex(data)
                    progress_bar.update(chunk_size)
                    bytes_read += chunk_size
                    md5.update(data)
                    f.write(data)
        md5sum = md5.hexdigest()
        remote_md5sum = shell_exec("md5sum %s |cut -d' ' -f1" % self.target_file)
        write_str("Local MD5:  %s\r\nRemote MD5: %s\r\n" % (md5sum, remote_md5sum), LogLevel.WARNING)


register_plugin(Download)
