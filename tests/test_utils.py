import pytest

from utils import _extract_id, _extract_reactions


@pytest.fixture
def dataid():
    return 'feed_subtitle_107207125979624;5762739400426340;;9'


def test_extract_pageid(dataid):
    pageid = _extract_id(dataid, 0)
    assert pageid == '107207125979624'


def test_extract_postid(dataid):
    postid = _extract_id(dataid, 1)
    assert postid == '5762739400426340'


# def test_extract_reactions(reactions, reaction_type):
#     reactions = _extract_reactions(reactions, reaction_type)
#     assert reactions is not None
