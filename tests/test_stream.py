import unittest
from src.models.stream import Stream


class TestStream(unittest.TestCase):
    def test_stream_creation(self):
        stream = Stream(
            index=0,
            stream_type="video",
            codec="h264",
            language="spa",
            description="Video principal",
        )
        self.assertEqual(stream.index, 0)
        self.assertEqual(stream.stream_type, "video")
        self.assertEqual(stream.codec, "h264")
        self.assertEqual(stream.language, "spa")

    def test_match_key(self):
        stream = Stream(
            index=0,
            stream_type="Video",
            codec="H264",
            language="SPA",
            description="",
        )
        self.assertEqual(stream.match_key, ("video", "spa", "h264"))

    def test_type_label(self):
        video = Stream(index=0, stream_type="video", codec="h264", language="und", description="")
        audio = Stream(index=1, stream_type="audio", codec="aac", language="spa", description="")
        subtitle = Stream(index=2, stream_type="subtitle", codec="srt", language="spa", description="")

        self.assertEqual(video.type_label, "Video")
        self.assertEqual(audio.type_label, "Audio")
        self.assertEqual(subtitle.type_label, "Subtitulo")

    def test_to_dict(self):
        stream = Stream(
            index=0,
            stream_type="video",
            codec="h264",
            language="spa",
            description="Test",
            checked=True,
        )
        d = stream.to_dict()
        self.assertEqual(d["index"], 0)
        self.assertEqual(d["stream_type"], "video")
        self.assertTrue(d["checked"])

    def test_from_probe(self):
        data = {
            "index": 0,
            "codec_type": "video",
            "codec_name": "h264",
            "tags": {"language": "spa", "description": "Test"},
        }
        stream = Stream.from_probe(data)
        self.assertEqual(stream.index, 0)
        self.assertEqual(stream.stream_type, "video")
        self.assertEqual(stream.language, "spa")

    def test_from_probe_defaults(self):
        data = {"index": 1}
        stream = Stream.from_probe(data)
        self.assertEqual(stream.codec, "unknown")
        self.assertEqual(stream.language, "und")


if __name__ == "__main__":
    unittest.main()
