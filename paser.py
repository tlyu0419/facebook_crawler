import re
import json
import pandas as pd
from bs4 import BeautifulSoup
from utils import _extract_id, _init_request_vars
import datetime
from requester import _get_pageabout, _get_pagetransparency, _get_homepage, _get_posts, _get_headers
import requests
# Post-Paser


def _parse_edgelist(resp):
    '''
    Take edges from the response by graphql api
    '''
    edges = []
    try:
        edges = resp.json()['data']['node']['timeline_feed_units']['edges']
    except:
        for data in resp.text.split('\r\n', -1):
            try:
                if 'timeline_list_feed_units' in json.loads(data)['data']['node']:
                    edges.append(json.loads(data)['data']['node']['timeline_list_feed_units']['edges'][0])
                elif 'timeline_feed_units' in json.loads(data)['data']['node']:
                    edges.append(json.loads(data)['data']['node']['timeline_feed_units']['edges'][0])
                else:
                    edges.append(json.loads(data)['data']['node']['timeline_list_feed_units']['edges'][0])
            except:
                edges.append(json.loads(data)['data'])
    return edges


def _parse_edge(edge):
    '''
    Parse edge to take informations, such as post name, id, message..., etc. 
    '''
    comet_sections = edge['node']['comet_sections']
    # name
    name = comet_sections['context_layout']['story']['comet_sections']['actor_photo']['story']['actors'][0]['name']

    # creation_time
    creation_time = comet_sections['context_layout']['story']['comet_sections']['metadata'][0]['story']['creation_time']

    # message
    try:
        message = comet_sections['content']['story']['comet_sections']['message']['story']['message']['text']
    except:
        try:
            message = comet_sections['content']['story']['comet_sections']['message_container']['story']['message']['text']
        except:
            message = comet_sections['content']['story']['comet_sections']['message_container']
    # postid
    postid = comet_sections['feedback']['story']['feedback_context'][
        'feedback_target_with_context']['ufi_renderer']['feedback']['subscription_target_id']

    # actorid
    pageid = comet_sections['context_layout']['story']['comet_sections']['actor_photo']['story']['actors'][0]['id']

    # comment_count
    comment_count = comet_sections['feedback']['story']['feedback_context'][
        'feedback_target_with_context']['ufi_renderer']['feedback']['comment_count']['total_count']

    # reaction_count
    reaction_count = comet_sections['feedback']['story']['feedback_context']['feedback_target_with_context'][
        'ufi_renderer']['feedback']['comet_ufi_summary_and_actions_renderer']['feedback']['reaction_count']['count']

    # share_count
    share_count = comet_sections['feedback']['story']['feedback_context']['feedback_target_with_context'][
        'ufi_renderer']['feedback']['comet_ufi_summary_and_actions_renderer']['feedback']['share_count']['count']

    # toplevel_comment_count
    toplevel_comment_count = comet_sections['feedback']['story']['feedback_context'][
        'feedback_target_with_context']['ufi_renderer']['feedback']['toplevel_comment_count']['count']

    # top_reactions
    top_reactions = comet_sections['feedback']['story']['feedback_context']['feedback_target_with_context']['ufi_renderer'][
        'feedback']['comet_ufi_summary_and_actions_renderer']['feedback']['cannot_see_top_custom_reactions']['top_reactions']['edges']

    # comet_footer_renderer for link
    try:
        comet_footer_renderer = comet_sections['content']['story']['attachments'][0]['comet_footer_renderer']
        # attachment_title
        attachment_title = comet_footer_renderer['attachment']['title_with_entities']['text']
        # attachment_description
        attachment_description = comet_footer_renderer['attachment']['description']['text']
    except:
        attachment_title = ''
        attachment_description = ''

    # all_subattachments for photos
    try:
        try:
            media = comet_sections['content']['story']['attachments'][0]['styles']['attachment']['all_subattachments']['nodes']
            attachments_photos = ', '.join(
                [image['media']['viewer_image']['uri'] for image in media])
        except:
            media = comet_sections['content']['story']['attachments'][0]['styles']['attachment']
            attachments_photos = media['media']['photo_image']['uri']
    except:
        attachments_photos = ''

    # cursor
    cursor = edge['cursor']

    # actor url
    actor_url = comet_sections['context_layout']['story']['comet_sections']['actor_photo']['story']['actors'][0]['url']

    # post url
    post_url = comet_sections['content']['story']['wwwURL']

    return [name, pageid, postid, creation_time, message, reaction_count, comment_count, toplevel_comment_count, share_count, top_reactions, attachment_title, attachment_description, attachments_photos, cursor, actor_url, post_url]


def _parse_domops(resp):
    '''
    Take name, data id, time , message and page link from domops
    '''
    data = re.sub(r'for \(;;\);', '', resp.text)
    data = json.loads(data)
    domops = data['domops'][0][3]['__html']
    cursor = re.findall(
        'timeline_cursor%22%3A%22(.*?)%22%2C%22timeline_section_cursor', domops)[0]
    content_list = []
    soup = BeautifulSoup(domops, 'lxml')

    for content in soup.findAll('div', {'class': 'userContentWrapper'}):
        # name
        name = content.find('img')['aria-label']
        # id
        dataid = content.find('div', {'data-testid': 'story-subtitle'})['id']
        # actorid
        pageid = _extract_id(dataid, 0)
        # postid
        postid = _extract_id(dataid, 1)
        # time
        time = content.find('abbr')['data-utime']
        # message
        message = content.find('div', {'data-testid': 'post_message'})
        if message == None:
            message = ''
        else:
            if len(message.findAll('p')) >= 1:
                message = ''.join(p.text for p in message.findAll('p'))
            elif len(message.select('span > span')) >= 2:
                message = message.find('span').text

        # attachment_title
        try:
            attachment_title = content.find(
                'a', {'data-lynx-mode': 'hover'})['aria-label']
        except:
            attachment_title = ''
        # attachment_description
        try:
            attachment_description = content.find(
                'a', {'data-lynx-mode': 'hover'}).text
        except:
            attachment_description = ''
        # actor_url
        actor_url = content.find('a')['href'].split('?')[0]

        # post_url
        post_url = 'https://www.facebook.com/' + postid
        content_list.append([name, pageid, postid, time, message, attachment_title,
                            attachment_description, cursor, actor_url, post_url])
    return content_list, cursor


def _parse_jsmods(resp):
    '''
    Take postid, pageid, comment count , reaction count, sharecount, reactions and display_comments_count from jsmods
    '''
    data = re.sub(r'for \(;;\);', '', resp.text)
    data = json.loads(data)
    jsmods = data['jsmods']

    requires_list = []
    for requires in jsmods['pre_display_requires']:
        try:
            feedback = requires[3][1]['__bbox']['result']['data']['feedback']
            # subscription_target_id ==> postid
            subscription_target_id = feedback['subscription_target_id']
            # owning_profile_id ==> pageid
            owning_profile_id = feedback['owning_profile']['id']
            # comment_count
            comment_count = feedback['comment_count']['total_count']
            # reaction_count
            reaction_count = feedback['reaction_count']['count']
            # share_count
            share_count = feedback['share_count']['count']
            # top_reactions
            top_reactions = feedback['top_reactions']['edges']
            # display_comments_count
            display_comments_count = feedback['display_comments_count']['count']

            # append data to list
            requires_list.append([subscription_target_id, owning_profile_id, comment_count,
                                 reaction_count, share_count, top_reactions, display_comments_count])
        except:
            pass

    # reactions--video posts
    for requires in jsmods['require']:
        try:
            # entidentifier ==> postid
            entidentifier = requires[3][2]['feedbacktarget']['entidentifier']
            # pageid
            actorid = requires[3][2]['feedbacktarget']['actorid']
            # comment count
            commentcount = requires[3][2]['feedbacktarget']['commentcount']
            # reaction count
            likecount = requires[3][2]['feedbacktarget']['likecount']
            # sharecount
            sharecount = requires[3][2]['feedbacktarget']['sharecount']
            # reactions
            reactions = []
            # display_comments_count
            commentcount = requires[3][2]['feedbacktarget']['commentcount']

            # append data to list
            requires_list.append(
                [entidentifier, actorid, commentcount, likecount, sharecount, reactions, commentcount])
        except:
            pass
    return requires_list


def _parse_composite_graphql(resp):
    edges = _parse_edgelist(resp)
    df = []
    for edge in edges:
        try:
            ndf = _parse_edge(edge)
            df.append(ndf)
        except:
            pass
    df = pd.DataFrame(df, columns=['NAME', 'PAGEID', 'POSTID', 'TIME', 'MESSAGE', 'REACTIONCOUNT', 'COMMENTCOUNT', 'DISPLAYCOMMENTCOUNT',
                                   'SHARECOUNT', 'REACTIONS', 'ATTACHMENT_TITLE', 'ATTACHMENT_DESCRIPTION', 'ATTACHMENT_PHOTOS', 'CURSOR', 'ACTOR_URL', 'POST_URL'])
    df = df[['NAME', 'PAGEID', 'POSTID', 'TIME', 'MESSAGE', 'ATTACHMENT_TITLE', 'ATTACHMENT_DESCRIPTION', 'ATTACHMENT_PHOTOS', 'REACTIONCOUNT',
             'COMMENTCOUNT', 'DISPLAYCOMMENTCOUNT', 'SHARECOUNT', 'REACTIONS', 'CURSOR', 'ACTOR_URL', 'POST_URL']]
    cursor = df['CURSOR'].to_list()[-1]
    df['TIME'] = df['TIME'].apply(lambda x: datetime.datetime.fromtimestamp(
        int(x)).strftime("%Y-%m-%d %H:%M:%S"))
    max_date = df['TIME'].max()
    print('The maximum date of these posts is: {}, keep crawling...'.format(max_date))
    return df, max_date, cursor


def _parse_composite_nojs(resp):
    domops, cursor = _parse_domops(resp)
    domops = pd.DataFrame(domops, columns=['NAME', 'PAGEID', 'POSTID', 'TIME', 'MESSAGE',
                          'ATTACHMENT_TITLE', 'ATTACHMENT_DESCRIPTION', 'CURSOR', 'ACTOR_URL', 'POST_URL'])
    domops['TIME'] = domops['TIME'].apply(
        lambda x: datetime.datetime.fromtimestamp(int(x)).strftime("%Y-%m-%d %H:%M:%S"))

    jsmods = _parse_jsmods(resp)
    jsmods = pd.DataFrame(jsmods, columns=[
                          'POSTID', 'PAGEID', 'COMMENTCOUNT', 'REACTIONCOUNT', 'SHARECOUNT', 'REACTIONS', 'DISPLAYCOMMENTCOUNT'])

    df = pd.merge(left=domops,
                  right=jsmods,
                  how='inner',
                  on=['PAGEID', 'POSTID'])

    df = df[['NAME', 'PAGEID', 'POSTID', 'TIME', 'MESSAGE', 'ATTACHMENT_TITLE', 'ATTACHMENT_DESCRIPTION',
             'REACTIONCOUNT', 'COMMENTCOUNT', 'DISPLAYCOMMENTCOUNT', 'SHARECOUNT', 'REACTIONS', 'CURSOR',
             'ACTOR_URL', 'POST_URL']]
    max_date = df['TIME'].max()
    print('The maximum date of these posts is: {}, keep crawling...'.format(max_date))
    return df, max_date, cursor

# Page paser


def _parse_pagetype(homepage_response):
    if '/groups/' in homepage_response.url:
        pagetype = 'Group'
    else:
        pagetype = 'Fanspage'
    return pagetype


def _parse_pagename(homepage_response):
    raw_json = homepage_response.text.encode('utf-8').decode('unicode_escape')
    # pattern1
    if len(re.findall(r'{"page":{"name":"(.*?)",', raw_json)) >= 1:
        pagename = re.findall(r'{"page":{"name":"(.*?)",', raw_json)[0]
        pagename = re.sub(r'\s\|\sFacebook', '', pagename)
        return pagename
    # pattern2
    if len(re.findall('","name":"(.*?)","', raw_json)) >= 1:
        pagename = re.findall('","name":"(.*?)","', raw_json)[0]
        pagename = re.sub(r'\s\|\sFacebook', '', pagename)
        return pagename


def _parse_entryPoint(homepage_response):
    try:
        entryPoint = re.findall(
            '"entryPoint":{"__dr":"(.*?)"}}', homepage_response.text)[0]
    except:
        entryPoint = 'nojs'
    return entryPoint


def _parse_identifier(entryPoint, homepage_response):
    if entryPoint in ['ProfilePlusCometLoggedOutRouteRoot.entrypoint', 'CometGroupDiscussionRoot.entrypoint']:
        # pattern 1
        if len(re.findall('"identifier":"{0,1}([0-9]{5,})"{0,1},', homepage_response.text)) >= 1:
            identifier = re.findall(
                '"identifier":"{0,1}([0-9]{5,})"{0,1},', homepage_response.text)[0]

        # pattern 2
        elif len(re.findall('fb://profile/(.*?)"', homepage_response.text)) >= 1:
            identifier = re.findall(
                'fb://profile/(.*?)"', homepage_response.text)[0]

        # pattern 3
        elif len(re.findall('content="fb://group/([0-9]{1,})" />', homepage_response.text)) >= 1:
            identifier = re.findall(
                'content="fb://group/([0-9]{1,})" />', homepage_response.text)[0]

    elif entryPoint in ['CometSinglePageHomeRoot.entrypoint', 'nojs']:
        # pattern 1
        if len(re.findall('"pageID":"{0,1}([0-9]{5,})"{0,1},', homepage_response.text)) >= 1:
            identifier = re.findall(
                '"pageID":"{0,1}([0-9]{5,})"{0,1},', homepage_response.text)[0]

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
        members = re.findall(
            ',"group_total_members_info_text":"(.*?) total members","', pageabout.text)[0]
        members = re.sub(',', '', members)
        return members
    else:
        # pattern 1
        data = re.findall(
            '"page_likers":{"global_likers_count":([0-9]{1,})},"', homepage_response.text)
        if len(data) >= 1:
            likes = data[0]
            return likes
        # pattern 2
        data = re.findall(
            ' ([0-9]{0,},{0,}[0-9]{0,},{0,}[0-9]{0,},{0,}[0-9]{0,},{0,}[0-9]{0,},{0,}) likes', homepage_response.text)
        if len(data) >= 1:
            likes = data[0]
            likes = re.sub(',', '', likes)
            return likes


def _parse_creation_time(homepage_response, entryPoint, headers):
    try:
        if entryPoint in ['ProfilePlusCometLoggedOutRouteRoot.entrypoint']:
            transparency_response = _get_pagetransparency(
                homepage_response, entryPoint, headers)
            transparency_info = re.findall(
                '"field_section_type":"transparency","profile_fields":{"nodes":\[{"title":(.*?}),"field_type":"creation_date",', transparency_response.text)[0]
            creation_time = json.loads(transparency_info)['text']

        elif entryPoint in ['CometSinglePageHomeRoot.entrypoint']:
            creation_time = re.findall(
                ',"page_creation_date":{"text":"Page created - (.*?)"},', homepage_response.text)[0]

        elif entryPoint in ['nojs']:
            if len(re.findall('<span>Page created - (.*?)</span>', homepage_response.text)) >= 1:
                creation_time = re.findall(
                    '<span>Page created - (.*?)</span>', homepage_response.text)[0]
            else:
                creation_time = re.findall(
                    ',"foundingDate":"(.*?)"}', homepage_response.text)[0][:10]

        elif entryPoint in ['CometGroupDiscussionRoot.entrypoint']:
            pageabout = _get_pageabout(homepage_response, entryPoint, headers)
            creation_time = re.findall(
                '"group_history_summary":{"text":"Group created on (.*?)"}},', pageabout.text)[0]

        try:
            creation_time = datetime.datetime.strptime(
                creation_time, '%B %d, %Y')
        except:
            creation_time = creation_time + ', ' + datetime.datetime.now().year
            creation_time = datetime.datetime.strptime(
                creation_time, '%B %d, %Y')
        creation_time = creation_time.strftime('%Y-%m-%d')
    except:
        creation_time = 'NotAvailable'
    return creation_time


def _parse_category(homepage_response, entryPoint, headers):
    pageabout = _get_pageabout(homepage_response, entryPoint, headers)
    if entryPoint in ['ProfilePlusCometLoggedOutRouteRoot.entrypoint']:
        if 'Page \\u00b7 Politician' in pageabout.text:
            category = 'Politician'
        if len(re.findall(r'"text":"Page \\u00b7 (.*?)"}', homepage_response.text)) >= 1:
            category = re.findall(
                r'"text":"Page \\u00b7 (.*?)"}', homepage_response.text)[0]
        else:
            soup = BeautifulSoup(pageabout.text)
            for script in soup.findAll('script', {'type': 'application/ld+json'}):
                if 'BreadcrumbList' in script.text:
                    data = script.text.encode('utf-8').decode('unicode_escape')
                    category = json.loads(data)['itemListElement']
                    category = ' / '.join([cate['name'] for cate in category])
    elif entryPoint in ['CometSinglePageHomeRoot.entrypoint', 'nojs']:
        if len(re.findall('","category_name":"(.*?)","', homepage_response.text)) >= 1:
            category = re.findall(
                '","category_name":"(.*?)","', homepage_response.text)
            category = ' / '.join([cate for cate in category])
        else:
            soup = BeautifulSoup(homepage_response.text)
            if len(soup.findAll('span', {'itemprop': 'itemListElement'})) >= 1:
                category = [span.text for span in soup.findAll(
                    'span', {'itemprop': 'itemListElement'})]
                category = ' / '.join(category)
            else:
                for script in soup.findAll('script', {'type': 'application/ld+json'}):
                    if 'BreadcrumbList' in script.text:
                        data = script.text.encode(
                            'utf-8').decode('unicode_escape')
                        category = json.loads(data)['itemListElement']
                        category = ' / '.join([cate['name']
                                              for cate in category])
    elif entryPoint in ['PagesCometAdminSelfViewAboutContainerRoot.entrypoint']:
        category = eval(re.findall(
            '"page_categories":(.*?),"addressEditable', homepage_response.text)[0])
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


def _parse_relatedpages(homepage_response, entryPoint, identifier):
    relatedpages = []
    if entryPoint in ['CometSinglePageHomeRoot.entrypoint']:
        try:
            data = re.findall(
                r'"related_pages":\[(.*?)\],"view_signature"', homepage_response.text)[0]
            data = re.sub('},{', '},,,,{', data)
            for pages in data.split(',,,,', -1):
                # print('id:', json.loads(pages)['id'])
                # print('category_name:', json.loads(pages)['category_name'])
                # print('name:', json.loads(pages)['name'])
                url = json.loads(pages)['url']
                url = url.split('?', -1)[0]
                url = re.sub(r'/$', '', url)
                # print('url:', url)
                # print('========')
                relatedpages.append(url)
        except:
            pass

    elif entryPoint in ['nojs']:
        soup = BeautifulSoup(homepage_response.text, 'lxml')
        soup = soup.find(
            'div', {'id': 'PageRelatedPagesSecondaryPagelet_{}'.format(identifier)})
        for page in soup.select('ul > li > div'):
            # print('name: ', page.find('img')['aria-label'])
            url = page.find('a')['href']
            url = url.split('?', -1)[0]
            url = re.sub(r'/$', '', url)
            # print('url:', url)
            # print('===========')
            relatedpages.append(url)

    elif entryPoint in ['ProfilePlusCometLoggedOutRouteRoot.entrypoint', 'CometGroupDiscussionRoot.entrypoint']:
        pass
        # print('There\'s no related pages recommend.')
    return relatedpages


def _parse_pageinfo(homepage_response):
    '''
    Parse the homepage response to get the page information, including id, docid and api_name.
    '''
    # pagetype
    pagetype = _parse_pagetype(homepage_response)

    # pagename
    pagename = _parse_pagename(homepage_response)

    # entryPoint
    entryPoint = _parse_entryPoint(homepage_response)

    # identifier
    identifier = _parse_identifier(entryPoint, homepage_response)

    # docid
    docid = _parse_docid(entryPoint, homepage_response)

    # likes / members
    likes = _parse_likes(homepage_response, entryPoint, headers)

    # creation time
    creation_time = _parse_creation_time(
        homepage_response, entryPoint, headers)

    # category
    category = _parse_category(homepage_response, entryPoint, headers)

    # pageurl
    pageurl = _parse_pageurl(homepage_response)

    return [pagetype, pagename, identifier, likes, creation_time, category, pageurl]


if __name__ == '__main__':
    # pageurls
    pageurl = 'https://www.facebook.com/mohw.gov.tw'
    pageurl = 'https://www.facebook.com/groups/pythontw'
    pageurl = 'https://www.facebook.com/Gooaye'
    pageurl = 'https://www.facebook.com/emily0806'
    pageurl = 'https://www.facebook.com/anuetw/'
    pageurl = 'https://www.facebook.com/wealtholic/'
    pageurl = 'https://www.facebook.com/hatendhu'

    headers = _get_headers(pageurl)
    headers['Referer'] = 'https://www.facebook.com/hatendhu'
    headers['Origin'] = 'https://www.facebook.com'
    headers['Cookie'] = 'dpr=1.5; datr=rzIwY5yARwMzcR9H2GyqId_l'

    homepage_response = _get_homepage(pageurl=pageurl, headers=headers)

    entryPoint = _parse_entryPoint(homepage_response)
    print(entryPoint)

    identifier = _parse_identifier(entryPoint, homepage_response)

    docid = _parse_docid(entryPoint, homepage_response)

    df, cursor, max_date, break_times = _init_request_vars(cursor='')
    cursor = 'AQHRlIMW9sczmHGnME47XeSdDNj6Jk9EcBOMlyxBdMNbZHM7dwd0rn8wsaxQxeXUsuhKVaMgVwPHb9YS9468INvb5yw2osoEmXd_sMXvj8rLhmBxeaJucMSPIDux_JuiHToC'
    cursor = 'AQHRxSZTqUvlLpkXCnrOjdX0gZeyn-Q1cuJzn4SPJuZ5rkYi7nZFByE5pwy4AsBoUOtcmF28lNfXR_rqv7oO7545iURm_mx46aZLBDiYfPmgI2mjscHUTiVi5vv1vj5EXiF4'
    resp = _get_posts(headers=headers, identifier=identifier,
                      entryPoint=entryPoint, docid=docid, cursor=cursor)

    # graphql
    edges = _parse_edgelist(resp)
    print(len(edges))
    _parse_edge(edges[0])
    edges[0].keys()
    edges[0]['node'].keys()
    edges[0]['node']['comet_sections'].keys()
    edges[0]['node']['comet_sections']
    df, max_date, cursor = _parse_composite_graphql(resp)
    df
    # nojs
    content_list, cursor = _parse_domops(resp)

    df, max_date, cursor = _parse_composite_nojs(resp)

    # page paser

    pagename = _parse_pagename(homepage_response).encode('utf-8').decode()
    likes = _parse_likes(homepage_response, entryPoint, headers)
    creation_time = _parse_creation_time(
        homepage_response=homepage_response, entryPoint=entryPoint, headers=headers)
    category = _parse_category(homepage_response, entryPoint, headers)
    pageurl = _parse_pageurl(homepage_response)
