import pytest

from post_paser import _parse_edgelist, _parse_edge, _parse_domops, _parse_jsmods, _parse_composite_graphql
from utils import _init_request_vars


@pytest.fixture
def pageurl():
    return 'https://www.facebook.com/groups/pythontw'


@pytest.fixture
def headers(pageurl):
    from requester import _get_headers
    return _get_headers(pageurl)


@pytest.fixture
def homepage_response(pageurl, headers):
    from requester import _get_homepage
    return _get_homepage(pageurl=pageurl, headers=headers)


@pytest.fixture
def entryPoint(homepage_response):
    from page_paser import _parse_entryPoint
    return _parse_entryPoint(homepage_response)


@pytest.fixture
def identifier(entryPoint, homepage_response):
    from page_paser import _parse_identifier
    return _parse_identifier(entryPoint, homepage_response)


@pytest.fixture
def docid(entryPoint, homepage_response):
    from page_paser import _parse_docid
    return _parse_docid(entryPoint, homepage_response)


@pytest.fixture
def cursor():
    _, cursor, _, _ = _init_request_vars()
    return cursor


@pytest.fixture
def posts_response(headers, identifier, entryPoint, docid, cursor):
    from requester import _get_posts
    return _get_posts(headers=headers,
                      identifier=identifier,
                      entryPoint=entryPoint,
                      docid=docid,
                      cursor=cursor)


@pytest.fixture()
def edges(posts_response):
    return _parse_edgelist(posts_response)


def test_parse_edgelist(posts_response):
    edges = _parse_edgelist(posts_response)
    assert len(edges) > 0


def test_parse_edge(edges):
    for edge in edges:
        result = _parse_edge(edge)
        assert result


def test_parse_domops(posts_response):
    content_list, cursor = _parse_domops(posts_response)
    assert content_list is not None
    assert cursor is not None


def test_parse_jsmods(posts_response):
    _parse_jsmods(posts_response)


def test_parse_composite_graphql(posts_response):
    df, max_date, cursor = _parse_composite_graphql(posts_response)
    assert df is not None
    assert max_date is not None
    assert cursor is not None


def test_parse_composite_nojs(posts_response):
    df, max_date, cursor = _parse_composite_graphql(posts_response)
    assert df is not None
    assert max_date is not None
    assert cursor is not None
