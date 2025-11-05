def normalize_meta(meta: dict):

    # واجهة تطبيع وهمية تمثّل ما يلزم توفره دوماً بالناتج

    return {

        "version": str(meta.get("version","1")),

        "pipeline": meta.get("pipeline","base"),

        "duration_ms": int(meta.get("duration_ms", 0))

    }



def test_output_metadata_shape_stable():

    out = {"version":"1.0.0","pipeline":"base","duration_ms": 123}

    m = normalize_meta(out)

    assert set(m.keys()) == {"version","pipeline","duration_ms"}

    assert isinstance(m["duration_ms"], int)
