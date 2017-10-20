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

def print_columns(strings, fd, width=80):
    """
    This function prints a series of input strings as columns.
    :param strings: The strings to print.
    :param fd: A file descriptor pointing to where the data should be
    written.
    :param width: The size of the window.
    """
    # Simple case: everything fits on a line:
    if len("  ".join(strings)) <= width:
        os.write(fd, "  ".join(strings).encode("UTF-8"))
        os.write(fd, b"\r\n")
        return

    # Determine how many columns should be used.
    number_of_columns = 1
    max_sizes = []
    new_max_size = []
    while True:
        # Divide and round up the result
        number_of_lines = len(strings) // (number_of_columns + 1) + (len(strings) % (number_of_columns + 1) > 0)
        for i in range(number_of_columns + 1):
            column_strings = strings[i * number_of_lines:(i + 1) * number_of_lines]
            # Returns the size of the biggest string in the list.
            if len(column_strings) != 0:  # Some configurations may leave the last column empty.
                new_max_size.append(len(max(column_strings, key=len)))
        # Size of each line: size of the biggest element of each column plus 2 spaces between each column.
        if sum(new_max_size) + 2 * (len(new_max_size) - 1) >= width:
            break
        number_of_columns += 1
        max_sizes = new_max_size  # Keep a copy of the size of each column
        new_max_size = []

    # TODO: if 1 column
    if number_of_columns == 1:
        for s in strings:
            os.write(fd, (s + "\r\n").encode("UTF-8"))
        return

    # Print each line:
    number_of_lines = len(strings) // number_of_columns + (len(strings) % number_of_columns > 0)  # Divide and round up
    for i in range(number_of_lines):
        line_strings = [strings[j] for j in range(i, len(strings), number_of_lines)]
        for i in range(len(line_strings)):
            line_strings[i] = line_strings[i].ljust(max_sizes[i])  # Pad each string.
        os.write(fd, "  ".join(line_strings).encode("UTF-8"))
        os.write(fd, b"\r\n")
