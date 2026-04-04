import types
import unittest
from unittest import mock

import ffm


class DriverStub:
    def __init__(self):
        self.clear_count = 0
        self.draw_count = 0

    def clear_line(self):
        self.clear_count += 1

    def draw_current_line(self):
        self.draw_count += 1


class TestFFM(unittest.TestCase):
    def test_update_window_size_redraws_active_session_driver(self):
        driver = DriverStub()
        session = types.SimpleNamespace(master=123, input_driver=driver)
        old_context = ffm.context
        ffm.context = types.SimpleNamespace(
            window_size=[24, 80], active_session=session, sessions=[session]
        )

        def fake_ioctl(fd, request, winsz, mutate=False):
            if request == ffm.termios.TIOCGWINSZ:
                winsz[0] = 40
                winsz[1] = 120
            return 0

        try:
            with mock.patch.object(ffm.fcntl, "ioctl", side_effect=fake_ioctl):
                ffm.update_window_size()
        finally:
            ffm.context = old_context

        self.assertEqual(driver.clear_count, 1)
        self.assertEqual(driver.draw_count, 1)
