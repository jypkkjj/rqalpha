# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     error
   Description :
   Author :        mixbe
   date：          2020/10/16
-------------------------------------------------
   Change Activity:
                   2020/10/16:
-------------------------------------------------
"""
class Error(Exception):
    pass


class AuthError(Error):
    pass


class InvalidTokenError(Error):
    pass


class TimeOutError(Error):
    pass


class ServerError(Error):
    pass


class UnknownError(Error):
    pass