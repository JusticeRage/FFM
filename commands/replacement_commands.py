"""
    ffm.py by @JusticeRage

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
import sys
import time

import model.context as context

def alias_test():
    #context.pty_pre_read_hook = pre_hook
    os.write(sys.stdout.fileno(), "\r\n")
    os.write(context.active_session.master, "\x15ls -l\n")
    # Restore echo after the PTY's output has been read.
    #context.pty_post_read_hook = context.active_session.enable_echo

def pre_hook():
    context.active_session.disable_echo()
    time.sleep(1)
    os.write(context.active_session.master, "\x15ls -l\n")