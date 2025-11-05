from contextlib import contextmanager

import time



@contextmanager

def fast_timeout(seconds=2.0):

    start = time.time()

    yield

    assert (time.time() - start) <= seconds, "Timeout exceeded"



class DummyImage:

    def __init__(self, w, h, corrupt=False):

        self.w, self.h, self.corrupt = w, h, corrupt

    def is_valid(self):

        return self.w>0 and self.h>0 and not self.corrupt
