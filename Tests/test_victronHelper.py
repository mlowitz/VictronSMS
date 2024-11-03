import unittest
from unittest.mock import MagicMock, patch

from VictronProcessors.processor import TankValue
from VictronProcessors.victronHelper import (
    Í,
    get_tank_device_info,
    get_tank_values,
    getValues,
    installationInfo,
    requestHelper,
)


class TestVictronHelper(unittest.TestCase):
    def setUp(self):
        self.headers = {
            "Content-Type": "application/json",
            "x-authorization": "Bearer test_token",
        }
        self.installationID = 12345
        self.tank_info = [
            {"customName": "Tank 1", "instance": 1},
            {"customName": "Tank 2", "instance": 2},
        ]

    @patch("victronHelper.requests.get")
    def test_requestHelper(self, mock_get):
        mock_response = MagicMock()
        mock_response.json.return_value = {"key": "value"}
        mock_get.return_value = mock_response

        url = "https://example.com"
        response = requestHelper(self.headers, url)
        self.assertEqual(response, {"key": "value"})
        mock_get.assert_called_once_with(url, headers=self.headers)

    def test_get_tank_device_info(self):
        json_data = {
            "records": {
                "devices": [
                    {"name": "Tank", "customName": "Tank 1", "instance": 1},
                    {
                        "name": "Battery",
                        "customName": "Battery 1",
                        "instance": 2,
                    },
                    {"name": "Tank", "customName": "Tank 2", "instance": 3},
                ]
            }
        }
        expected_output = [
            {"customName": "Tank 1", "instance": 1},
            {"customName": "Tank 2", "instance": 3},
        ]
        self.assertEqual(get_tank_device_info(json_data), expected_output)

    @patch("victronHelper.requestHelper")
    def test_get_tank_values(self, mock_requestHelper):
        mock_requestHelper.return_value = {
            "records": {
                "data": {
                    "1": {"code": "tl", "formattedValue": "50%"},
                    "2": {"code": "tf", "formattedValue": "Fresh Water"},
                }
            }
        }

        expected_output = [
            TankValue(customName="Tank 1", value="50%"),
            TankValue(customName="Tank 1", type="Fresh Water"),
        ]

        self.assertEqual(
            get_tank_values(self.tank_info, self.headers, self.installationID),
            expected_output,
        )

    @patch("victronHelper.requests.get")
    @patch("victronHelper.get_tank_values")
    @patch("victronHelper.get_tank_device_info")
    def test_getValues(
        self,
        mock_get_tank_device_info,
        mock_get_tank_values,
        mock_requests_get,
    ):
        mock_get_tank_device_info.return_value = self.tank_info
        mock_get_tank_values.return_value = [
            TankValue(customName="Tank 1", value="50%"),
            TankValue(customName="Tank 2", type="Fresh Water"),
        ]

        mock_response = MagicMock()
        mock_response.json.side_effect = [
            {"records": {"data": {"51": {"formattedValue": "80%"}}}},
            {"records": {"devices": []}},
        ]
        mock_requests_get.return_value = mock_response

        info = installationInfo(
            access_token="test_token",
            user_ID=1,
            installationID=self.installationID,
            installation_Name="Test Boat",
            phone_number="1234567890",
            message_time="2023-01-01T00:00:00Z",
        )

        values = getValues(info)
        self.assertEqual(values.boatName, "Test Boat")
        self.assertEqual(values.batterySOC, "80%")
        self.assertEqual(values.tanks, mock_get_tank_values.return_value)


if __name__ == "__main__":
    unittest.main()
