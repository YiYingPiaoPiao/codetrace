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
# Init the TraceFunc
# And declare to trace_func, for east usage.
trace_func = TraceFunc()
trace_func.config()

from .utils.recorder import Recorder
# Init the Recorder
# Ensure each run will recorder
Recorder.register_exit()

__all__ = [
    "trace_func"
]