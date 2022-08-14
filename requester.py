import re
import requests
import time
# from  page_paser import _parse_entryPoint, _parse_identifier, _parse_docid
from utils import _init_request_vars


def _get_headers(pageurl):
    '''
    Send a request to get cookieid as headers.
    '''
    pageurl = re.sub('www', 'm', pageurl)
    resp = requests.get(pageurl)
    headers = {
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'accept-language': 'en'}
    headers['cookie'] = '; '.join(
        ['{}={}'.format(cookieid, resp.cookies.get_dict()[cookieid]) for cookieid in resp.cookies.get_dict()])
    # headers['cookie'] = headers['cookie'] + '; locale=en_US'
    return headers


def _get_homepage(pageurl, headers):
    '''
    Send a request to get the homepage response
    '''
    pageurl = re.sub('/$', '', pageurl)
    timeout_cnt = 0
    while True:
        try:
            homepage_response = requests.get(pageurl, headers=headers, timeout=3)
            return homepage_response
        except:
            time.sleep(5)
            timeout_cnt = timeout_cnt + 1
            if timeout_cnt > 20:
                class homepage_response():
                    text = 'Sorry, something went wrong.'

                return homepage_response


def _get_pageabout(homepage_response, entryPoint, headers):
    '''
    Send a request to get the about page response
    '''
    pageurl = re.sub('/$', '', homepage_response.url)
    pageabout = requests.get(pageurl + '/about', headers=headers)
    return pageabout


def _get_pagetransparency(homepage_response, entryPoint, headers):
    '''
    Send a request to get the transparency page response
    '''
    pageurl = re.sub('/$', '', homepage_response.url)
    if entryPoint in ['ProfilePlusCometLoggedOutRouteRoot.entrypoint']:
        transparency_response = requests.get(pageurl + '/about_profile_transparency', headers=headers)
        return transparency_response


def _get_posts(headers, identifier, entryPoint, docid, cursor):
    '''
    Send a request to get new posts from fanspage/group.
    '''
    if entryPoint in ['nojs']:
        params = {'page_id': identifier,
                  'cursor': str({"timeline_cursor": cursor,
                                 "timeline_section_cursor": '{}',
                                 "has_next_page": 'true'}),
                  'surface': 'www_pages_posts',
                  'unit_count': 10,
                  '__a': '1'}
        resp = requests.get(url='https://www.facebook.com/pages_reaction_units/more/',
                            params=params)

    else:  # entryPoint in ['CometSinglePageHomeRoot.entrypoint', 'ProfilePlusCometLoggedOutRouteRoot.entrypoint', 'CometGroupDiscussionRoot.entrypoint']
        data = {'variables': str({'cursor': cursor,
                                  'id': identifier}),
                'doc_id': docid}
        resp = requests.post(url='https://www.facebook.com/api/graphql/',
                             data=data,
                             headers=headers)
    return resp

#
# if __name__ == '__main__':
#     pageurl = 'https://www.facebook.com/ec.ltn.tw/'
#     pageurl = 'https://www.facebook.com/Gooaye'
#     pageurl = 'https://www.facebook.com/groups/pythontw'
#     headers = _get_headers(pageurl)
#     homepage_response = _get_homepage(pageurl=pageurl, headers=headers)
#     # entryPoint = _parse_entryPoint(homepage_response)
#     # identifier = _parse_identifier(entryPoint, homepage_response)
#     # docid = _parse_docid(entryPoint, homepage_response)
#     # df, cursor, max_date, break_times = _init_request_vars()
#
#     # resp = _get_posts(headers=headers,
#     #                 identifier=identifier,
#     #                 entryPoint=entryPoint,
#     #                 docid=docid,
#     #                 cursor=cursor)
#     # print(len(resp.text))
