import os
import shutil
import tempfile


class TemporaryDirectory:
    """Create and return a temporary directory.  This has the same
    behavior as mkdtemp but can be used as a context manager.  For
    example:

        with TemporaryDirectory() as tmpdir:
            ...

    Upon exiting the context, the directory and everything contained
    in it are removed.
    """

    def __init__(self, suffix="", prefix=tempfile.template, dir=None):
        self.name = tempfile.mkdtemp(suffix, prefix, dir)

    def __enter__(self):
        return self.name

    def cleanup(self):
        if os.path.exists(self.name):
            shutil.rmtree(self.name)

    def __exit__(self, exc, value, tb):
        self.cleanup()