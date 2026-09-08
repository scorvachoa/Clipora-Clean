import os
import unittest
from src.services.ffmpeg_service import build_output_path, _parse_out_time


class TestFFmpegService(unittest.TestCase):
    def test_build_output_path_default(self):
        result = build_output_path("/videos/test.mp4")
        self.assertEqual(result, os.path.join("/videos", "test_clean.mp4"))

    def test_build_output_path_with_dir(self):
        result = build_output_path("/videos/test.mp4", "/output")
        self.assertEqual(result, os.path.join("/output", "test_clean.mp4"))

    def test_build_output_path_preserves_container(self):
        result = build_output_path("/videos/test.mkv")
        self.assertEqual(result, os.path.join("/videos", "test_clean.mkv"))

    def test_build_output_path_no_ext(self):
        result = build_output_path("/videos/test")
        self.assertEqual(result, os.path.join("/videos", "test_clean.mp4"))

    def test_parse_out_time_valid(self):
        result = _parse_out_time("01:30:45.500000")
        self.assertAlmostEqual(result, 5445.5, places=2)

    def test_parse_out_time_zero(self):
        result = _parse_out_time("00:00:00.000000")
        self.assertEqual(result, 0.0)

    def test_parse_out_time_invalid_format(self):
        result = _parse_out_time("invalid")
        self.assertIsNone(result)

    def test_parse_out_time_wrong_parts(self):
        result = _parse_out_time("01:30")
        self.assertIsNone(result)


if __name__ == "__main__":
    unittest.main()
