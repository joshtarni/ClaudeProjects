from app import title_is_ready


def test_titles_are_unready_without_complete_record():
    assert not title_is_ready("nfsu2_revived", {})
    assert not title_is_ready("vice_city_web", {})


def test_partial_integration_record_does_not_enable_title():
    incomplete = {
        "nfsu2_revived": {
            "authorized_source_build": "/local/nfsu2.exe",
            "rights_evidence": None,
            "passed_TEST_003": False,
        }
    }
    assert not title_is_ready("nfsu2_revived", incomplete)


def test_complete_record_enables_one_title_independently():
    complete = {
        "vice_city_web": {
            "authorized_source_build": "/local/vice.exe",
            "rights_evidence": "documented local-use approval",
            "passed_TEST_003": True,
        }
    }
    assert not title_is_ready("nfsu2_revived", complete)
    assert title_is_ready("vice_city_web", complete)
