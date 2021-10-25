import re
from bs4 import BeautifulSoup
import requests
url = 'https://www.facebook.com/groups/pythontw'
url = re.sub('www','mbasic',url)
url = 'https://mbasic.facebook.com/groups/197223143437?bac=MTYzNDczNjUyMToxMDE2MTY0OTUyMzU1MzQzODoxMDE2MTY0OTUyMzU1MzQzOCwwLDA6NzpLdz09&multi_permalinks&refid=18'

rs = requests.session()
resp = rs.get(url)
soup = BeautifulSoup(resp.text)
soup.find('div',{'id':'m_group_stories_container'}).select('div > div')

soup.findAll('div',{'class':'be bg br'})


soup.select('div#m_group_stories_container > div > div')[1]

# url = 'https://www.facebook.com/api/graphql/'
headers = {
        'referer': 'https://m.facebook.com/',
        'cookie': 'locale=en_US',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.101 Safari/537.36'
        }

data = {
    'av': '0',
    '__user': '0',
    '__a': '1',
    '__dyn': '7xeUmwlEnwn8K2WnFw9-2i5U4e0yoW3q322aew9G2S0zU2lwUx60gu0luq1ew65xOfw9q0woy11xmfz83WwgEcHzoaEd82ly87e2l0Fwqo31wnEcUC1lwlE-Uqw8y4UaEW0D888brwKxm5o2eUlDw-waCm268w4ywJwSyES0QEcU',
    '__csr': 'gogx7T6Nai6_VGObQGTZRiQ_EACV8HP99CmF-FJJWleh5QHFeiWXmVLBhAfAKRyaK9AKVkF8yh2nx2EWuAFXBBByHHGaCx6UzybhprzaCDzAErhVoy4Fp9-4poWUyUvBx69x2eGVqxpadUiCxp7Bw4swCw4qwSwlUVyK261vwk87K2i1pqg0qrw0GBw2Re0gG05jo2Yw8O070o1MU0X-07aU5a0li091wBgtwho461fg0O-0oW68nxycw8Kczof8v8Etz8_y80J20lS5E3_wd611Dw9m0Poy3W1gw46wcu1wwnEao9UfFU9oeU98cU4G0F84J2899U1kU4S0uOcz8760T8lw3l83TG0bcwtE0wa6o8J03DUrwfO0J81982wwbO0g-0iB027o18Utg1kE5u4Efvo6sw5y0JA5Oxu1axjxedzX4yAu19BwaoM2xwZximhUV5ld29ClQSUpyawcm0cPw5zwdK',
    '__req': 's',
    '__hs': '18920.HYP:comet_loggedout_pkg.2.0.0.0.',
    'dpr': '1',
    '__ccg': 'EXCELLENT',
    '__rev': '1004584695',
    '__s': '0oekn6:7klbh8:1nwbyy',
    '__hsi': '7021139148085675833-0',
    '__comet_req': '1',
    'lsd': 'AVoFPEJu7MM',
    'jazoest': '2881',
    '__spin_r': '1004584695',
    '__spin_b': 'trunk',
    '__spin_t': '1634736347',
    'fb_api_caller_class': 'RelayModern',
    'fb_api_req_friendly_name': 'GroupsCometFeedRegularStoriesPaginationQuery',
    'variables': {
        "UFI2CommentsProvider_commentsKey":"CometGroupDiscussionRootSuccessQuery",
        "count":'3',
        "cursor":"Cg8TZXhpc3RpbmdfdW5pdF9jb3VudAIPDwtyZWFsX2N1cnNvcg+rQVFIUkhJRUpSZndjVDFRV1ljTml4SzdVbVpGb2RUdko0b1FKTzZnaVpTRmN1VGdpNktBYzJQMDQxbXBSTkZ2TFRNMm9tTHhrQWNuR2FxYmN4N3R6dlI0MkFBOmV5SXdJam94TmpNME56TTJNelEzTENJeElqb3pOVGcyTENJeUlqb3hOak0wTnpNMk16UTNMQ0l6SWpvMExDSTBJam94TENJMUlqb3pmUT09DxNoZWFkZXJfZ2xvYmFsX2NvdW50AgEPEm1haW5fZmVlZF9wb3NpdGlvbgIPDxhpc19ncm91cHNfcGl2b3RfaW5zZXJ0ZWQRAA8NZmVlZF9vcmRlcmluZw8NYWN0aXZpdHlfdGltZQE=",
        # "displayCommentsContextEnableComment":'',
        # "displayCommentsContextIsAdPreview":'',
        # "displayCommentsContextIsAggregatedShare":'',
        # "displayCommentsContextIsStorySet":'',
        # "displayCommentsFeedbackContext":'',
        "feedLocation":"GROUP",
        "feedType":"DISCUSSION",
        "feedbackSource":'0',
        # "focusCommentID":'',
        "privacySelectorRenderLocation":"COMET_STREAM",
        "renderLocation":"group",
        "scale":'1',
        # "sortingSetting":'',
        "stream_initial_count":'2',
        "useDefaultActor":'false',
        "id":"197223143437"},
    'server_timestamps': 'true',
    'doc_id': '6533501936725035'}

rs = requests.session()
resp = rs.post(url, headers=headers, data=data)
resp.text
pycharm


# import re
# def get_groupid(GroupUrl):
#     resp = requests.get(GroupUrl)
#     groupid = re.findall(r'content="fb://group/\?id=(.*?)" />',resp.text)[0]
#     return groupid
# url = 'https://www.facebook.com/ajax/pagelet/generic.php/GroupEntstreamPagelet'
# end_cursor = ''
# groupid = get_groupid(GroupUrl='https://www.facebook.com/groups/pythontw')
# params = {'ajaxpipe': '1',
#           'data': str({"last_view_time":0,
#                        "end_cursor":end_cursor,
#                        "group_id":groupid,
#                        "multi_permalinks":[]})}
# resp = requests.get(url, params=params)
# resp.text