import re
from bs4 import BeautifulSoup
import json
import datetime
import requests
from requester import _get_pageabout, _get_pagetransparency, _get_homepage
from utils import _get_headers

def _parse_pagetype(homepage_response):
    if '/groups/' in homepage_response.url:
        pagetype = 'Group'
    else:
        pagetype = 'Fanspage'
    return pagetype

def _parse_pagename(homepage_response):
    raw_json = homepage_response.text.encode('utf-8').decode('unicode_escape')
    # pattern1
    if len(re.findall(r'{"page":{"name":"(.*?)",', raw_json))>=1:
        pagename = re.findall(r'{"page":{"name":"(.*?)",', raw_json)[0]
        pagename = re.sub(r'\s\|\sFacebook', '', pagename)
        return pagename
    # pattern2
    if len(re.findall('","name":"(.*?)","', raw_json))>=1:
        pagename = re.findall('","name":"(.*?)","', raw_json)[0]
        pagename = re.sub(r'\s\|\sFacebook', '', pagename)
        return pagename

def _parse_entryPoint(homepage_response):
    try:
        entryPoint = re.findall('"entryPoint":{"__dr":"(.*?)"}}', homepage_response.text)[0]
    except:
        entryPoint = 'nojs'
    return entryPoint

def _parse_identifier(entryPoint, homepage_response):
    if entryPoint in ['ProfilePlusCometLoggedOutRouteRoot.entrypoint', 'CometGroupDiscussionRoot.entrypoint']:
        # pattern 1
        if len(re.findall('"identifier":"{0,1}([0-9]{5,})"{0,1},', homepage_response.text))>=1:
            identifier = re.findall('"identifier":"{0,1}([0-9]{5,})"{0,1},', homepage_response.text)[0]
        
        # pattern 2
        elif len(re.findall('fb://profile/(.*?)"', homepage_response.text))>=1:
            identifier = re.findall('fb://profile/(.*?)"', homepage_response.text)[0]
        
        # pattern 3
        elif len(re.findall('content="fb://group/([0-9]{1,})" />', homepage_response.text))>=1:
            identifier = re.findall('content="fb://group/([0-9]{1,})" />', homepage_response.text)[0]
        
    elif entryPoint in ['CometSinglePageHomeRoot.entrypoint', 'nojs']:
        # pattern 1
        if len(re.findall('"pageID":"{0,1}([0-9]{5,})"{0,1},', homepage_response.text))>=1:
            identifier = re.findall('"pageID":"{0,1}([0-9]{5,})"{0,1},', homepage_response.text)[0]       
            
    return identifier

def _parse_docid(entryPoint, homepage_response):
    soup = BeautifulSoup(homepage_response.text, 'lxml')
    if entryPoint == 'nojs':
        docid = 'NoDocid'
    else: 
        for link in soup.findAll('link', {'rel': 'preload'}):
            resp = requests.get(link['href'])
            for line in resp.text.split('\n', -1):
                if 'ProfileCometTimelineFeedRefetchQuery_' in line:
                    docid = re.findall('e.exports="([0-9]{1,})"', line)[0]
                    break

                if 'CometModernPageFeedPaginationQuery_' in line:
                    docid = re.findall('e.exports="([0-9]{1,})"', line)[0]
                    break

                if 'CometUFICommentsProviderQuery_' in line:
                    docid = re.findall('e.exports="([0-9]{1,})"', line)[0]
                    break

                if 'GroupsCometFeedRegularStoriesPaginationQuery' in line:
                    docid = re.findall('e.exports="([0-9]{1,})"', line)[0]
                    break
            if 'docid' in locals():
                break
    return docid

def _parse_likes(homepage_response, entryPoint, headers):
    if entryPoint in ['CometGroupDiscussionRoot.entrypoint']:
        pageabout = _get_pageabout(homepage_response, entryPoint, headers)
        members = re.findall(',"group_total_members_info_text":"(.*?) total members","', pageabout.text)[0]
        members = re.sub(',', '', members)
        return members
    else:
        # pattern 1
        data = re.findall('"page_likers":{"global_likers_count":([0-9]{1,})},"', homepage_response.text)
        if len(data) >= 1:
            likes = data[0]
            return likes
        # pattern 2
        data = re.findall(' ([0-9]{0,},{0,}[0-9]{0,},{0,}[0-9]{0,},{0,}[0-9]{0,},{0,}[0-9]{0,},{0,}) likes', homepage_response.text)
        if len(data) >= 1:
            likes = data[0]
            likes = re.sub(',', '', likes)
            return likes

def _parse_creation_time(homepage_response, entryPoint, headers):
    try:
        if entryPoint in ['ProfilePlusCometLoggedOutRouteRoot.entrypoint']:
            transparency_response = _get_pagetransparency(homepage_response, entryPoint, headers)
            transparency_info = re.findall('"field_section_type":"transparency","profile_fields":{"nodes":\[{"title":(.*?}),"field_type":"creation_date",', transparency_response.text)[0]
            creation_time = json.loads(transparency_info)['text']

        elif entryPoint in ['CometSinglePageHomeRoot.entrypoint']:
            creation_time = re.findall(',"page_creation_date":{"text":"Page created - (.*?)"},', homepage_response.text)[0]

        elif entryPoint in ['nojs']:
            if len(re.findall('<span>Page created - (.*?)</span>', homepage_response.text))>=1:
                creation_time = re.findall('<span>Page created - (.*?)</span>', homepage_response.text)[0]
            else:
                creation_time = re.findall(',"foundingDate":"(.*?)"}', homepage_response.text)[0][:10]

        elif entryPoint in ['CometGroupDiscussionRoot.entrypoint']:
            pageabout = _get_pageabout(homepage_response, entryPoint, headers)
            creation_time =  re.findall('"group_history_summary":{"text":"Group created on (.*?)"}},', pageabout.text)[0]

        try:
            creation_time = datetime.datetime.strptime(creation_time, '%B %d, %Y')
        except:
            creation_time = creation_time + ', ' + datetime.datetime.now().year
            creation_time = datetime.datetime.strptime(creation_time, '%B %d, %Y')
        creation_time = creation_time.strftime('%Y-%m-%d')
    except:
        creation_time = 'NotAvailable'
    return creation_time
    
def _parse_category(homepage_response, entryPoint, headers):
    pageabout = _get_pageabout(homepage_response, entryPoint, headers)
    if entryPoint in ['ProfilePlusCometLoggedOutRouteRoot.entrypoint']:
        if 'Page \\u00b7 Politician' in pageabout.text:
            category = 'Politician'
        if len(re.findall(r'"text":"Page \\u00b7 (.*?)"}', homepage_response.text))>=1:
            category = re.findall(r'"text":"Page \\u00b7 (.*?)"}', homepage_response.text)[0]
        else:
            soup = BeautifulSoup(pageabout.text)
            for script in soup.findAll('script', {'type':'application/ld+json'}):
                if 'BreadcrumbList' in script.text:
                    data = script.text.encode('utf-8').decode('unicode_escape')
                    category = json.loads(data)['itemListElement']
                    category = ' / '.join([cate['name'] for cate in category]) 
    elif entryPoint in ['CometSinglePageHomeRoot.entrypoint', 'nojs']:
        if len(re.findall('","category_name":"(.*?)","', homepage_response.text)) >= 1:
            category = re.findall('","category_name":"(.*?)","', homepage_response.text)
            category = ' / '.join([cate for cate in category])
        else:
            soup = BeautifulSoup(homepage_response.text)
            if len(soup.findAll('span', {'itemprop':'itemListElement'})) >= 1:
                category = [span.text for span in soup.findAll('span', {'itemprop':'itemListElement'})]
                category = ' / '.join(category)
            else:
                for script in soup.findAll('script', {'type':'application/ld+json'}):
                    if 'BreadcrumbList' in script.text:
                        data = script.text.encode('utf-8').decode('unicode_escape')
                        category = json.loads(data)['itemListElement']
                        category = ' / '.join([cate['name'] for cate in category]) 
    elif entryPoint in ['PagesCometAdminSelfViewAboutContainerRoot.entrypoint']:
        category = eval(re.findall('"page_categories":(.*?),"addressEditable', homepage_response.text)[0])
        category = ' / '.join([cate['text'] for cate in category])
    elif entryPoint in ['CometGroupDiscussionRoot.entrypoint']:
        category = 'Group'
    try:
        category = re.sub(r'\\/', '/', category)
    except:
        category = ''
    return category

def _parse_pageurl(homepage_response):
    pageurl = homepage_response.url
    pageurl = re.sub('/$', '', pageurl)
    return pageurl


#
# if __name__ == '__main':
#     pageurl = 'https://www.facebook.com/Gooaye'
#     pageurl = 'https://www.facebook.com/groups/pythontw'
#     headers = _get_headers(pageurl)
#     homepage_response = _get_homepage(pageurl=pageurl, headers=headers)
#     pagename = _parse_pagename(homepage_response).encode('utf-8').decode()
#     entryPoint = _parse_entryPoint(homepage_response)
#     entryPoint = _parse_entryPoint(homepage_response)
#     identifier = _parse_identifier(entryPoint, homepage_response)
#     doc_id = _parse_docid(entryPoint, homepage_response)
#     likes = _parse_likes(homepage_response, entryPoint, headers)
#     creation_time =_parse_creation_time(homepage_response=homepage_response, entryPoint=entryPoint, headers=headers)
#     category = _parse_category(homepage_response, entryPoint, headers)
#     pageurl = _parse_pageurl(homepage_response)
#