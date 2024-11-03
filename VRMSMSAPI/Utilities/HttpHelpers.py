from enum import Enum
from http import HTTPStatus, request

import requests
from fastapi import HTTPException


class AuthType(Enum):
    Bearer = 1
    Authorization = 2


def GetHelper(authType, token, url, data=None):
    headers = {"Content-Type": "application/json"}
    match authType:
        case AuthType.Bearer:
            headers["x-authorization"] = "Bearer " + token

        case AuthType.Authorization:
            headers["x-authorization"] = "Token " + token
        case _:
            raise HTTPException(
                status_code=HTTPStatus.BAD_REQUEST,
                detail="Bad Token Type",
            )

    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        raise HTTPException(
            status_code=response.status_code,
            detail=response.json(),
        )
    return response.json()


def PostHelper(authType, token, url, data=None):
    headers = {"Content-Type": "application/json"}
    match authType:
        case AuthType.Bearer:
            headers["x-authorization"] = "Bearer " + token

        case AuthType.Authorization:
            headers["x-authorization"] = "Token " + token
        case _:
            raise HTTPException(
                status_code=HTTPStatus.BAD_REQUEST,
                detail="Bad Token Type",
            )

    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        raise HTTPException(
            status_code=response.status_code,
            detail=response.json(),
        )
    return response.json()
