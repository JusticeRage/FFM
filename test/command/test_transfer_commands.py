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

import os
import io
import tarfile
import tempfile
import unittest
from unittest import mock

import commands.download_file as download_file
import commands.download_directory as download_directory
import commands.upload_file as upload_file
from model.driver.input_api import shell_quote
from test.fixture.dummy_context import DummyContextTest


class _FakeProgressBar:
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False

    def update(self, amount):
        return None


class TestDownloadCommandQuoting(DummyContextTest):
    def _run_download_case(self, xxd_available):
        remote_path = "/tmp/remote path's.bin"
        with tempfile.TemporaryDirectory() as tmpdir:
            destination = os.path.join(tmpdir, "downloaded.bin")

            commands = []

            def fake_shell_exec(command, *args, **kwargs):
                commands.append(command)
                if command.startswith('stat -c "%s" '):
                    return "4100"
                if xxd_available and command.startswith("xxd -p -l4096 -s0 "):
                    return "61" * 4096
                if xxd_available and command.startswith("xxd -p -l4 -s4096 "):
                    return "62" * 4
                if not xxd_available and command.startswith("od -vt x1 -N4096 -j0 "):
                    return "61" * 4096
                if not xxd_available and command.startswith("od -vt x1 -N4 -j4096 "):
                    return "62" * 4
                if command.startswith("md5sum "):
                    return "remote-md5"
                raise AssertionError("Unexpected shell command: %s" % command)

            with mock.patch.object(
                download_file, "file_exists", return_value=True
            ), mock.patch.object(
                download_file.tqdm, "tqdm", return_value=_FakeProgressBar()
            ), mock.patch.object(
                download_file,
                "check_command_existence",
                side_effect=lambda cmd: cmd == "xxd" and xxd_available or cmd == "od",
            ), mock.patch.object(
                download_file, "shell_exec", side_effect=fake_shell_exec
            ):
                cmd = download_file.Download("!download", remote_path, destination)
                cmd.execute()

        quoted_path = shell_quote(remote_path)
        if xxd_available:
            expected = [
                'stat -c "%%s" %s' % quoted_path,
                "xxd -p -l4096 -s0 %s" % quoted_path,
                "xxd -p -l4 -s4096 %s" % quoted_path,
                "md5sum %s |cut -d' ' -f1" % quoted_path,
            ]
        else:
            expected = [
                'stat -c "%%s" %s' % quoted_path,
                "od -vt x1 -N4096 -j0 %s | awk '{$1=\"\"; print $0}'" % quoted_path,
                "od -vt x1 -N4 -j4096 %s | awk '{$1=\"\"; print $0}'" % quoted_path,
                "md5sum %s |cut -d' ' -f1" % quoted_path,
            ]
        self.assertEqual(commands, expected)

    def test_quotes_remote_path_in_stat_chunk_reads_and_checksum_with_xxd(self):
        self._run_download_case(True)

    def test_quotes_remote_path_in_stat_chunk_reads_and_checksum_with_od(self):
        self._run_download_case(False)


class TestUploadCommandQuoting(DummyContextTest):
    def test_quotes_remote_destination_in_append_and_checksum(self):
        remote_destination = "/var/tmp/upload path's.bin"
        with tempfile.NamedTemporaryFile("wb", delete=False) as handle:
            handle.write(b"x" * 3000)
            local_file = handle.name

        commands = []

        def fake_gzip_compress(contents):
            return b"compressed-%d" % len(contents)

        def fake_b64encode(data):
            if data == b"compressed-2048":
                return b"chunk-one"
            if data == b"compressed-952":
                return b"chunk-two"
            raise AssertionError("Unexpected compressed payload: %r" % (data,))

        def fake_shell_exec(command, *args, **kwargs):
            commands.append(command)
            if command.startswith('echo "'):
                return ""
            if command.startswith("md5sum "):
                return "remote-md5"
            raise AssertionError("Unexpected shell command: %s" % command)

        try:
            with mock.patch.object(
                upload_file, "is_directory", return_value=False
            ), mock.patch.object(
                upload_file, "file_exists", return_value=False
            ), mock.patch.object(
                upload_file.gzip, "compress", side_effect=fake_gzip_compress
            ), mock.patch.object(
                upload_file.base64, "b64encode", side_effect=fake_b64encode
            ), mock.patch.object(
                upload_file, "shell_exec", side_effect=fake_shell_exec
            ), mock.patch.object(
                upload_file.tqdm, "tqdm", return_value=_FakeProgressBar()
            ):
                cmd = upload_file.Upload("!upload", local_file, remote_destination)
                cmd.execute()
        finally:
            os.remove(local_file)

        quoted_destination = shell_quote(remote_destination)
        self.assertEqual(
            commands,
            [
                'echo "chunk-one" |base64 -d |gunzip >> %s' % quoted_destination,
                'echo "chunk-two" |base64 -d |gunzip >> %s' % quoted_destination,
                "md5sum %s |cut -d' ' -f1" % quoted_destination,
            ],
        )


class TestDirectoryDownloadCommand(DummyContextTest):
    def _build_archive(self, members, mode="w:gz"):
        archive = io.BytesIO()
        with tarfile.open(fileobj=archive, mode=mode) as tar:
            for name, data in members.items():
                info = tarfile.TarInfo(name=name)
                payload = data.encode("utf-8")
                info.size = len(payload)
                tar.addfile(info, io.BytesIO(payload))
        return archive.getvalue()

    def test_streams_remote_tar_and_extracts_locally(self):
        remote_path = "/tmp/remote dir's"
        archive_bytes = self._build_archive(
            {
                "remote dir's/file.txt": "hello",
                "remote dir's/subdir/nested.txt": "world",
            }
        )

        commands = []

        def fake_shell_exec_stream(command, handler, timeout=300):
            commands.append(command)
            encoded = download_directory.base64.b64encode(archive_bytes)
            midpoint = len(encoded) // 2
            handler(encoded[:midpoint] + b"\n")
            handler(encoded[midpoint:] + b"\n")
            return 0

        with tempfile.TemporaryDirectory() as tmpdir:
            destination = os.path.join(tmpdir, "extract-here")

            with mock.patch.object(
                download_directory, "is_directory", return_value=True
            ), mock.patch.object(
                download_directory,
                "check_command_existence",
                side_effect=lambda cmd: cmd in {"tar", "base64", "gzip"},
            ), mock.patch.object(
                download_directory,
                "shell_exec_stream",
                side_effect=fake_shell_exec_stream,
            ):
                cmd = download_directory.DownloadDirectory(
                    "!download-dir", remote_path, destination
                )
                cmd.execute()

            quoted_parent = shell_quote("/tmp")
            quoted_name = shell_quote("remote dir's")
            self.assertEqual(
                commands,
                [
                    "tar -cf - -C %s %s | gzip -c | base64"
                    % (quoted_parent, quoted_name)
                ],
            )
            with open(
                os.path.join(destination, "remote dir's", "file.txt"), "r"
            ) as handle:
                self.assertEqual(handle.read(), "hello")
            with open(
                os.path.join(destination, "remote dir's", "subdir", "nested.txt"), "r"
            ) as handle:
                self.assertEqual(handle.read(), "world")

    def test_falls_back_to_plain_tar_when_gzip_is_unavailable(self):
        remote_path = "/tmp/remote dir's"
        archive_bytes = self._build_archive(
            {
                "remote dir's/file.txt": "hello",
            },
            mode="w:",
        )

        commands = []

        def fake_shell_exec_stream(command, handler, timeout=300):
            commands.append(command)
            handler(download_directory.base64.b64encode(archive_bytes) + b"\n")
            return 0

        with tempfile.TemporaryDirectory() as tmpdir:
            destination = os.path.join(tmpdir, "extract-here")

            with mock.patch.object(
                download_directory, "is_directory", return_value=True
            ), mock.patch.object(
                download_directory,
                "check_command_existence",
                side_effect=lambda cmd: cmd in {"tar", "base64"},
            ), mock.patch.object(
                download_directory,
                "shell_exec_stream",
                side_effect=fake_shell_exec_stream,
            ):
                cmd = download_directory.DownloadDirectory(
                    "!download-dir", remote_path, destination
                )
                cmd.execute()

            quoted_parent = shell_quote("/tmp")
            quoted_name = shell_quote("remote dir's")
            self.assertEqual(
                commands,
                ["tar -cf - -C %s %s | base64" % (quoted_parent, quoted_name)],
            )
            with open(
                os.path.join(destination, "remote dir's", "file.txt"), "r"
            ) as handle:
                self.assertEqual(handle.read(), "hello")

    def test_rejects_archive_path_traversal(self):
        remote_path = "/tmp/remote-dir"
        archive_bytes = self._build_archive({"../../escape.txt": "boom"})

        def fake_shell_exec_stream(command, handler, timeout=300):
            handler(download_directory.base64.b64encode(archive_bytes) + b"\n")
            return 0

        with tempfile.TemporaryDirectory() as tmpdir:
            destination = os.path.join(tmpdir, "extract-here")
            outside = os.path.join(tmpdir, "escape.txt")

            with mock.patch.object(
                download_directory, "is_directory", return_value=True
            ), mock.patch.object(
                download_directory,
                "check_command_existence",
                side_effect=lambda cmd: cmd in {"tar", "base64", "gzip"},
            ), mock.patch.object(
                download_directory,
                "shell_exec_stream",
                side_effect=fake_shell_exec_stream,
            ):
                cmd = download_directory.DownloadDirectory(
                    "!download-dir", remote_path, destination
                )
                with self.assertRaises(RuntimeError):
                    cmd.execute()

            self.assertFalse(os.path.exists(outside))
