from tests.helpers.fakes import DummyImage



def validate_input(img: DummyImage):

    # واجهة وهمية تمثّل مدقق الإدخال الحقيقي

    assert img.is_valid(), "invalid image"

    assert min(img.w, img.h) >= 256, "too small"

    assert max(img.w, img.h) <= 8192, "too large"



def test_reject_corrupt():

    bad = DummyImage(1024, 1024, corrupt=True)

    try:

        validate_input(bad)

        assert False, "should fail"

    except AssertionError as e:

        assert "invalid" in str(e)



def test_reject_too_small():

    bad = DummyImage(128, 128)

    try:

        validate_input(bad); assert False

    except AssertionError as e:

        assert "small" in str(e)



def test_accept_normal():

    ok = DummyImage(1024, 768)

    validate_input(ok)
