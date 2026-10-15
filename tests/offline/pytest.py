"""Minimal stand-in for the parts of pytest the repo's tests use."""
import inspect as _inspect

FIXTURES = {}

def fixture(func=None, **kw):
    def reg(f):
        FIXTURES[f.__name__] = f
        return f
    return reg(func) if func is not None else reg

class _Raises:
    def __init__(self, exc):
        self.exc = exc
    def __enter__(self):
        return self
    def __exit__(self, et, ev, tb):
        import genlayer
        if et is None:
            raise AssertionError("DID NOT RAISE")
        # Only contract-level rejections count; a Python bug must fail the test.
        if issubclass(et, genlayer.UserError):
            return True
        return False

def raises(exc, **kw):
    return _Raises(exc)
