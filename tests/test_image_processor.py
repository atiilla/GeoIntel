import unittest

from geointel.image_processor import ImageProcessor


class ImageProcessorTests(unittest.TestCase):
    def test_parse_data_url_extracts_supported_mime_type(self) -> None:
        mime_type, payload = ImageProcessor.parse_data_url(
            "data:image/png;base64,ZmFrZS1pbWFnZQ=="
        )

        self.assertEqual("image/png", mime_type)
        self.assertEqual("ZmFrZS1pbWFnZQ==", payload)

    def test_get_mime_type_prefers_valid_override(self) -> None:
        mime_type = ImageProcessor.get_mime_type(
            "/tmp/uploaded.jpg",
            mime_type_override="image/webp",
        )

        self.assertEqual("image/webp", mime_type)

    def test_get_mime_type_ignores_invalid_override(self) -> None:
        mime_type = ImageProcessor.get_mime_type(
            "/tmp/uploaded.png",
            mime_type_override="text/plain",
        )

        self.assertEqual("image/png", mime_type)


if __name__ == "__main__":
    unittest.main()
