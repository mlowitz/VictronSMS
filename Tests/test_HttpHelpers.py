from http import HTTPStatus
from unittest.mock import Mock, patch

import pytest
from fastapi import HTTPException

from app.Utilities.HttpHelpers import AuthType, GetHelper, PostHelper


@pytest.fixture
def mock_response():
    mock_resp = Mock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {"key": "value"}
    return mock_resp


@patch("requests.get")
def test_get_helper_bearer(mock_get, mock_response):
    mock_get.return_value = mock_response
    url = "http://example.com"
    token = "test_token"
    response = GetHelper(AuthType.Bearer, token, url)
    assert response == {"key": "value"}
    mock_get.assert_called_once_with(
        url,
        headers={
            "Content-Type": "application/json",
            "x-authorization": "Bearer test_token",
        },
    )


@patch("requests.get")
def test_get_helper_authorization(mock_get, mock_response):
    mock_get.return_value = mock_response
    url = "http://example.com"
    token = "test_token"
    response = GetHelper(AuthType.Authorization, token, url)
    assert response == {"key": "value"}
    mock_get.assert_called_once_with(
        url,
        headers={
            "Content-Type": "application/json",
            "x-authorization": "Token test_token",
        },
    )


@patch("requests.get")
def test_get_helper_invalid_auth_type(mock_get):
    url = "http://example.com"
    token = "test_token"
    with pytest.raises(HTTPException) as excinfo:
        GetHelper("InvalidAuthType", token, url)
    assert excinfo.value.status_code == HTTPStatus.BAD_REQUEST
    assert excinfo.value.detail == "Bad Token Type"


@patch("requests.post")
def test_post_helper_bearer(mock_post, mock_response):
    mock_post.return_value = mock_response
    url = "http://example.com"
    token = "test_token"
    data = {"key": "value"}
    response = PostHelper(AuthType.Bearer, token, url, data)
    assert response == {"key": "value"}
    mock_post.assert_called_once_with(
        url,
        headers={
            "Content-Type": "application/json",
            "x-authorization": "Bearer test_token",
        },
        json=data,
    )


@patch("requests.post")
def test_post_helper_authorization(mock_post, mock_response):
    mock_post.return_value = mock_response
    url = "http://example.com"
    token = "test_token"
    data = {"key": "value"}
    response = PostHelper(AuthType.Authorization, token, url, data)
    assert response == {"key": "value"}
    mock_post.assert_called_once_with(
        url,
        headers={
            "Content-Type": "application/json",
            "x-authorization": "Token test_token",
        },
        json=data,
    )


@patch("requests.post")
def test_post_helper_invalid_auth_type(mock_post):
    url = "http://example.com"
    token = "test_token"
    data = {"key": "value"}
    with pytest.raises(HTTPException) as excinfo:
        PostHelper("InvalidAuthType", token, url, data)
    assert excinfo.value.status_code == HTTPStatus.BAD_REQUEST
    assert excinfo.value.detail == "Bad Token Type"
