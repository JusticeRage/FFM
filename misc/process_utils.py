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
from collections import deque


def get_children():
    """
    This function returns a list of all FFM's child processes.
    Only works on Linux >= 3.5.
    :return: A list of children spawned by the FFM process and its children.
    """
    children = []
    pids = deque([os.getpid()])
    while pids:
        pid = pids.popleft()
        # This file is only available since the 3.5 Kernel. It may not exist, or the
        # process might have died during the search.
        if not os.path.exists("/proc/%s/task/%s/children" % (pid, pid)):
            return children

        # Add the current child's name
        with open("/proc/%s/cmdline" % pid) as f:
            children.append(f.read().split("\x00")[0])

        # Look for additional children
        with open("/proc/%s/task/%s/children" % (pid, pid), "r") as f:
            pids.extend(int(x) for x in f.read().split())

    return children
