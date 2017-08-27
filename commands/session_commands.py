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

import model.context as context
from model.session import Session

def cycle_session():
    for i in range(0, len(context.sessions)):
        if context.active_session is context.sessions[i]:
            if i != len(context.sessions) - 1:
                context.active_session = context.sessions[i+1]
            else:
                context.active_session = context.sessions[0]
            print("SESSION SWITCH!\r")
            os.write(context.active_session.master, "\n")
            return

# -----------------------------------------------------------------------------

def create_session():
    context.sessions.append(Session())
    print("SESSION CREATION!\r")
