from fiicha.parser import feature_flags_from_environ, parse_feature_flags_string


def test_parse_feature_flags_string() -> None:
    assert parse_feature_flags_string("a !b  c ") == {
        "a": True,
        "b": False,
        "c": True,
    }


def test_parse_feature_flags_none() -> None:
    assert parse_feature_flags_string(None) == {}


def test_parse_feature_flags_string_custom() -> None:
    assert parse_feature_flags_string("a,-b,c", ",", "-") == {
        "a": True,
        "b": False,
        "c": True,
    }


def test_feature_flags_from_environ() -> None:
    true = [
        "1",
        "true",
        "True",
        "TrUe",
        "t",
        "T",
        "yes",
        "Yes",
        "yES",
        "y",
        "Y",
        "on",
        "ON",
    ]
    false = [
        "",
        "0",
        "false",
        "fAlSe",
        "f",
        "F",
        "no",
        "nO",
        "n",
        "N",
        "off",
        "OfF",
    ]
    environ = {
        **{f"TEST_T{i}": value for i, value in enumerate(true)},
        **{f"TEST_F{i}": value for i, value in enumerate(false)},
        "TEST_X": "test",
        "TSET_Y": "1",
    }

    assert feature_flags_from_environ("TEST_", environ) == {
        **{f"t{i}": True for i in range(len(true))},
        **{f"f{i}": False for i in range(len(false))},
    }
