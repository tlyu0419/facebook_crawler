import pytest

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


def test_get_homepage(pageurl, headers):
    from requester import _get_homepage
    homepage_response = _get_homepage(pageurl=pageurl, headers=headers)
    assert homepage_response.status_code == 200
    assert homepage_response.url == pageurl


def test_get_pageabout(homepage_response, entryPoint, headers):
    from requester import _get_pageabout
    pageabout = _get_pageabout(homepage_response, entryPoint, headers)
    assert pageabout.status_code == 200


def test_get_posts(headers, identifier, entryPoint, docid, cursor):
    from requester import _get_posts
    resp = _get_posts(headers=headers,
                      identifier=identifier,
                      entryPoint=entryPoint,
                      docid=docid,
                      cursor=cursor)
    assert resp.status_code == 200
