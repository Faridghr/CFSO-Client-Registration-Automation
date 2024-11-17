# This file makes the `routes` directory a Python module.
# You can import all routes here if needed.

from .validate import validate_route
from .getdata import getdata_route

__all__ = ["validate_route", "getdata_route"]