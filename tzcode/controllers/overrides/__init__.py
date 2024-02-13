# Copyright (c) 2023, Yefri Tavarez and Contributors
# For license information, please see license.txt

# creates an overrides decorator which basically does nothing
# but for developers it will be useful to identify what is going
# at a first glance.

from functools import wraps


def overrides(method):
    @wraps(method)
    def wrapper(self, *args, **kwargs):
        return method(self, *args, **kwargs)
    return wrapper

    