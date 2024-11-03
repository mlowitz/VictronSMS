from http import HTTPStatus
from unittest.mock import Mock, patch

import pytest
from fastapi import HTTPException
from Utilities.HttpHelpers import AuthType, GetHelper, PostHelper


def test_get_helper_bearer_success():
    with patch("requests.get") as mock_get:
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"key": "value"}
        mock_get.return_value = mock_response

        result = GetHelper(AuthType.Bearer, "test_token", "http://test.url")
        assert result == {"key": "value"}
        mock_get.assert_called_once_with(
            "http://test.url",
            headers={
                "Content-Type": "application/json",
                "x-authorization": "Bearer test_token",
            },
        )


def test_get_helper_authorization_success():
    with patch("requests.get") as mock_get:
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"key": "value"}
        mock_get.return_value = mock_response

        result = GetHelper(
            AuthType.Authorization, "test_token", "http://test.url"
        )
        assert result == {"key": "value"}
        mock_get.assert_called_once_with(
            "http://test.url",
            headers={
                "Content-Type": "application/json",
                "x-authorization": "Token test_token",
            },
        )


def test_get_helper_bad_token_type():
    with pytest.raises(HTTPException) as exc_info:
        GetHelper("InvalidType", "test_token", "http://test.url")
    assert exc_info.value.status_code == HTTPStatus.BAD_REQUEST
    assert exc_info.value.detail == "Bad Token Type"


def test_get_helper_http_error():
    with patch("requests.get") as mock_get:
        mock_response = Mock()
        mock_response.status_code = 404
        mock_response.json.return_value = {"error": "not found"}
        mock_get.return_value = mock_response

        with pytest.raises(HTTPException) as exc_info:
            GetHelper(AuthType.Bearer, "test_token", "http://test.url")
        assert exc_info.value.status_code == 404
        assert exc_info.value.detail == {"error": "not found"}


def test_post_helper_bearer_success():
    with patch("requests.post") as mock_post:
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"key": "value"}
        mock_post.return_value = mock_response

        result = PostHelper(
            AuthType.Bearer,
            "test_token",
            "http://test.url",
            data={"data": "value"},
        )
        assert result == {"key": "value"}
        mock_post.assert_called_once_with(
            "http://test.url",
            headers={
                "Content-Type": "application/json",
                "x-authorization": "Bearer test_token",
            },
            json={"data": "value"},
        )


def test_post_helper_authorization_success():
    with patch("requests.post") as mock_post:
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"key": "value"}
        mock_post.return_value = mock_response

        result = PostHelper(
            AuthType.Authorization,
            "test_token",
            "http://test.url",
            data={"data": "value"},
        )
        assert result == {"key": "value"}
        mock_post.assert_called_once_with(
            "http://test.url",
            headers={
                "Content-Type": "application/json",
                "x-authorization": "Token test_token",
            },
            json={"data": "value"},
        )


def test_post_helper_bad_token_type():
    with pytest.raises(HTTPException) as exc_info:
        PostHelper(
            "InvalidType",
            "test_token",
            "http://test.url",
            data={"data": "value"},
        )
    assert exc_info.value.status_code == HTTPStatus.BAD_REQUEST
    assert exc_info.value.detail == "Bad Token Type"


def test_post_helper_http_error():
    with patch("requests.post") as mock_post:
        mock_response = Mock()
        mock_response.status_code = 404
        mock_response.json.return_value = {"error": "not found"}
        mock_post.return_value = mock_response

        with pytest.raises(HTTPException) as exc_info:
            PostHelper(
                AuthType.Bearer,
                "test_token",
                "http://test.url",
                data={"data": "value"},
            )
        assert exc_info.value.status_code == 404
        assert exc_info.value.detail == {"error": "not found"}
