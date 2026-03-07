import json
import unittest

from geointel.exceptions import ResponseParsingError
from geointel.response_parser import ResponseParser


class ResponseParserTests(unittest.TestCase):
    def test_parse_response_normalizes_non_numeric_coordinates(self) -> None:
        raw_response = json.dumps(
            {
                "interpretation": "Test",
                "locations": [
                    {
                        "country": "France",
                        "city": "Paris",
                        "confidence": "High",
                        "coordinates": {
                            "latitude": "48.8566",
                            "longitude": None,
                        },
                    }
                ],
            }
        )

        result = ResponseParser.parse_response(raw_response)

        self.assertEqual(48.8566, result["locations"][0]["coordinates"]["latitude"])
        self.assertEqual(0.0, result["locations"][0]["coordinates"]["longitude"])

    def test_invalid_json_is_not_reported_as_truncated(self) -> None:
        with self.assertRaises(ResponseParsingError) as error:
            ResponseParser.parse_response("{invalid json}")

        self.assertIn("Failed to parse API response as JSON", str(error.exception))
        self.assertNotIn("truncated", str(error.exception).lower())


if __name__ == "__main__":
    unittest.main()
