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

import base64
import os
import re
import tarfile
import tempfile

from commands.command_manager import register_plugin
from model.driver.input_api import *
from model.plugin.command import Command


class _Base64ArchiveWriter:
    def __init__(self, fd):
        self.fd = fd
        self.buffer = b""

    def write(self, chunk):
        self.buffer += re.sub(rb"\s+", b"", chunk)
        decode_length = len(self.buffer) // 4 * 4
        if decode_length == 0:
            return
        self.fd.write(base64.b64decode(self.buffer[:decode_length]))
        self.buffer = self.buffer[decode_length:]

    def finalize(self):
        if self.buffer:
            self.fd.write(base64.b64decode(self.buffer))
            self.buffer = b""


class DownloadDirectory(Command):
    def __init__(self, *args, **kwargs):
        if len(args) < 2 or len(args) > 3:
            raise RuntimeError("Received %d argument(s), expected 2 or 3." % len(args))

        self.target_directory = args[1].rstrip("/")
        if not self.target_directory:
            raise RuntimeError("Remote directory path cannot be empty.")
        if not is_directory(self.target_directory):
            raise RuntimeError("%s is not a directory!" % args[1])

        self.destination = os.path.expanduser(args[2]) if len(args) == 3 else "."
        if os.path.exists(self.destination) and not os.path.isdir(self.destination):
            raise RuntimeError("%s is not a directory!" % self.destination)

        if not check_command_existence("tar"):
            raise RuntimeError("tar is not available on the remote machine! Aborting.")
        if not check_command_existence("base64"):
            raise RuntimeError(
                "base64 is not available on the remote machine! Aborting."
            )
        self.use_gzip = check_command_existence("gzip")

    @staticmethod
    def regexp():
        return r"^\s*\!download-dir($| )"

    @staticmethod
    def usage():
        write_str(
            "Usage: !download-dir [remote directory] [local destination]\r\n",
            LogLevel.WARNING,
        )

    @staticmethod
    def name():
        return "!download-dir"

    @staticmethod
    def description():
        return "Downloads a directory from the remote machine without touching its filesystem."

    @staticmethod
    def tag():
        return "Transfer"

    def _get_remote_archive_command(self):
        parent = os.path.dirname(self.target_directory) or "/"
        basename = os.path.basename(self.target_directory)
        command = "tar -cf - -C %s %s" % (
            shell_quote(parent),
            shell_quote(basename),
        )
        if self.use_gzip:
            command += " | gzip -c"
        return command + " | base64"

    def _validate_member_name(self, member_name):
        normalized = os.path.normpath(member_name)
        if (
            os.path.isabs(member_name)
            or normalized == ".."
            or normalized.startswith(".." + os.sep)
        ):
            raise RuntimeError(
                "Refusing to extract unsafe archive member %s." % member_name
            )
        target = os.path.realpath(os.path.join(self.destination, normalized))
        if os.path.commonpath(
            [os.path.realpath(self.destination), target]
        ) != os.path.realpath(self.destination):
            raise RuntimeError(
                "Refusing to extract unsafe archive member %s." % member_name
            )

    def _ensure_parent_chain_is_not_symlink(self, member_name):
        normalized = os.path.normpath(member_name)
        parent = os.path.dirname(normalized)
        current = os.path.realpath(self.destination)
        for part in [part for part in parent.split(os.sep) if part not in ("", ".")]:
            current = os.path.join(current, part)
            if os.path.islink(current):
                raise RuntimeError(
                    "Refusing to extract through symlinked path %s." % member_name
                )

    def _extract_archive(self, archive_path):
        os.makedirs(self.destination, exist_ok=True)
        archive_mode = "r:gz" if self.use_gzip else "r:"
        with tarfile.open(archive_path, archive_mode) as archive:
            members = archive.getmembers()
            for member in members:
                self._validate_member_name(member.name)
            for member in members:
                self._ensure_parent_chain_is_not_symlink(member.name)
                extract_kwargs = {
                    "path": self.destination,
                    "set_attrs": True,
                    "filter": "data",
                }
                archive.extract(member, **extract_kwargs)

    def execute(self):
        archive_suffix = ".tar.gz" if self.use_gzip else ".tar"
        with tempfile.NamedTemporaryFile(suffix=archive_suffix, delete=False) as handle:
            archive_path = handle.name
            writer = _Base64ArchiveWriter(handle)

            try:
                exit_code = shell_exec_stream(
                    self._get_remote_archive_command(), writer.write, timeout=3600
                )
                writer.finalize()
                handle.flush()
                if exit_code != 0:
                    raise RuntimeError(
                        "Remote archive command failed with exit code %d." % exit_code
                    )
            finally:
                handle.flush()

        try:
            self._extract_archive(archive_path)
        finally:
            if os.path.exists(archive_path):
                os.remove(archive_path)


register_plugin(DownloadDirectory)
