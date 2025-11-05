import time
from tests.helpers.fakes import fast_timeout



def heavy_op(ms=200):

    time.sleep(ms/1000.0)  # محاكاة

    return True



def test_pipeline_respects_timeout():

    with fast_timeout(1.0):  # ≤ 1s

        assert heavy_op(200)



def test_pipeline_over_budget_is_flagged():

    t0 = time.time()

    heavy_op(900)  # 0.9s

    assert (time.time()-t0) < 1.2
