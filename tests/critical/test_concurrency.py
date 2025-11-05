import concurrent.futures, threading


counter = 0

lock = threading.Lock()


def step():

    global counter

    with lock:

        v = counter

        v += 1

        counter = v

    return True


def test_thread_safety_basic():

    global counter

    counter = 0

    with concurrent.futures.ThreadPoolExecutor(max_workers=8) as ex:

        list(ex.map(lambda _: step(), range(100)))

    assert counter == 100
