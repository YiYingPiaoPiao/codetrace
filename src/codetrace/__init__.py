# -*- coding: utf-8 -*-
"""
CodeTrace: A lightweight tool for tracing function inputs and outputs.
"""

__author__    = "LEE SEE CHEN"
__version__   = "0.1.0"
__license__   = "MIT"
__copyright__ = "Copyright 2025, LEE SEE CHEN"
__email__     = "contact@seechen.com"

from .decorators.TraceFunc import TraceFunc

trace_func = TraceFunc()
trace_func.config()

__all__ = [
    "trace_func"
]