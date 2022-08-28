import pytest


@pytest.fixture
def pageurl():
    return 'https://www.facebook.com/groups/pythontw'


@pytest.fixture
def until_date():
    from datetime import datetime
    from datetime import timedelta
    return str(datetime.now() - timedelta(days=1))


def test_Crawl_PagePosts(pageurl, until_date):
    from facebook_crawler import Crawl_PagePosts
    df = Crawl_PagePosts(pageurl, until_date=until_date)
    assert df


def test_Crawl_GroupPosts(pageurl, until_date):
    from facebook_crawler import Crawl_GroupPosts
    df = Crawl_GroupPosts(pageurl, until_date=until_date)
    assert df
