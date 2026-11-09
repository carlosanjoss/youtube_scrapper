import unittest

from youtube_client import seconds_until_youtube_quota_reset


class QuotaResetTests(unittest.TestCase):
    def test_pacific_timezone_is_available(self):
        seconds = seconds_until_youtube_quota_reset()
        self.assertGreaterEqual(seconds, 60)
        self.assertLessEqual(seconds, 25 * 60 * 60)


if __name__ == "__main__":
    unittest.main()
