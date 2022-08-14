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


def test_parse_pagetype(homepage_response):
    from page_paser import _parse_pagetype
    page_type = _parse_pagetype(homepage_response)
    assert page_type.lower() in ['group', 'fanspage']


def test_parse_pagename(homepage_response):
    from page_paser import _parse_pagename
    page_name = _parse_pagename(homepage_response)
    assert page_name


def test_parse_entryPoint(homepage_response):
    from page_paser import _parse_entryPoint
    entryPoint = _parse_entryPoint(homepage_response)
    assert entryPoint


def test_parse_identifier(entryPoint, homepage_response):
    from page_paser import _parse_identifier
    identifier = _parse_identifier(entryPoint, homepage_response)
    assert identifier


def test_parse_docid(entryPoint, homepage_response):
    from page_paser import _parse_docid
    docid = _parse_docid(entryPoint, homepage_response)
    assert docid


def test_parse_likes(homepage_response, entryPoint, headers):
    from page_paser import _parse_likes
    likes = _parse_likes(homepage_response, entryPoint, headers)
    assert likes


def test_parse_creation_time(homepage_response, entryPoint, headers):
    from page_paser import _parse_creation_time
    creation_time = _parse_creation_time(homepage_response, entryPoint, headers)
    assert creation_time


def test_parse_category(homepage_response, entryPoint, headers):
    from page_paser import _parse_category
    category = _parse_category(homepage_response, entryPoint, headers)
    assert category


def test_parse_pageurl(homepage_response):
    from page_paser import _parse_pageurl
    pageurl = _parse_pageurl(homepage_response)
    assert pageurl
