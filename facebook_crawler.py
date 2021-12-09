import requests
import re
import json
from bs4 import BeautifulSoup
import time
import datetime
import pandas as pd
import numpy as np
import urllib


# ============== Fanspage ==============
def Crawl_PagePosts(pageurl, until_date='2019-01-01'):
    
    # init parameters
    rs = requests.Session()
    content_df = [] # post
    feedback_df = [] # reactions
    timeline_cursor = ''
    break_times = 0
    max_date =  datetime.datetime.now().strftime('%Y-%m-%d')
    
    # Get PageID
    try:
        resp = rs.get(pageurl)
        pageid = re.findall('page_id=(.*?)"',resp.text)[0]
    except:
        print('Error at stage1: get pageid.')
    
    # request date and break loop when reach the goal 
    while max_date >= until_date:
        # request params
        url = 'https://www.facebook.com/pages_reaction_units/more/'
        params = {'page_id': pageid,
                  'cursor': str({"timeline_cursor":timeline_cursor,
                                 "timeline_section_cursor":'{}',
                                 "has_next_page":'true'}), 
                  'surface': 'www_pages_posts',
                  'unit_count': 20,
                  '__a': '1'}
        try:
            resp = rs.get(url, params=params)
            data = json.loads(re.sub(r'for \(;;\);','',resp.text))
            
            # Post info: poster's name, poster's ID, post ID, time, content
            soup = BeautifulSoup(data['domops'][0][3]['__html'], 'lxml')
            for content in soup.findAll('div', {'class':'userContentWrapper'}):
                # message
                message = content.find('div', {'data-testid':'post_message'})
                try:
                    message = ''.join(p.text for p in message.findAll('p'))
                except:
                    message = ''
                    
                content_df.append([
                    content.find('img')['aria-label'], # name
                    content.find('div', {'data-testid':'story-subtitle'})['id'], # id
                    content.find('abbr')['data-utime'], #time
                    message, # message
                    content.find('a')['href'].split('?')[0] #link
                ]) 
                                   
            # reactions--normal post
            for mod in data['jsmods']['pre_display_requires']:
                try:
                    feedback_df.append([
                        mod[3][1]['__bbox']['result']['data']['feedback']['subscription_target_id'], # post id
                        mod[3][1]['__bbox']['result']['data']['feedback']['owning_profile']['id'], # page id
                        mod[3][1]['__bbox']['result']['data']['feedback']['comment_count']['total_count'], # comment_count
                        mod[3][1]['__bbox']['result']['data']['feedback']['reaction_count']['count'], # reaction_count
                        mod[3][1]['__bbox']['result']['data']['feedback']['share_count']['count'], # share_count
                        mod[3][1]['__bbox']['result']['data']['feedback']['top_reactions']['edges'], # reactions
                        mod[3][1]['__bbox']['result']['data']['feedback']['display_comments_count']['count'] # display_comments_count
                    ])
                except:
                    pass
            
            # reactions--video post
            for mod in data['jsmods']['require']:
                try:
                    feedback_df.append([
                        mod[3][2]['feedbacktarget']['entidentifier'], # post id
                        mod[3][2]['feedbacktarget']['actorid'], # page id
                        mod[3][2]['feedbacktarget']['commentcount'], # comment count
                        mod[3][2]['feedbacktarget']['likecount'], # reaction count
                        mod[3][2]['feedbacktarget']['sharecount'], # sharecount
                        [], # reactions
                        mod[3][2]['feedbacktarget']['commentcount'] # display_comments_count
                    ])
                except:
                    pass

            # update request params
            max_date = max([time['data-utime'] for time in soup.findAll('abbr')])
            max_date = datetime.datetime.fromtimestamp(int(max_date)).strftime('%Y-%m-%d')
            print(f'TimeStamp: {max_date}.')
            timeline_cursor = re.findall(r'timeline_cursor\\u002522\\u00253A\\u002522(.*?)\\u002522\\u00252C\\u002522timeline_section_cursor',resp.text)[0]
            # break times to zero
            break_times = 0
        except:
            break_times += 1
            print('break_times:', break_times)
            if break_times > 10:
                break
        time.sleep(4)

    # join content and reactions
    content_df = pd.DataFrame(content_df, columns=['NAME', 'ID', 'TIME', 'MESSAGE', 'LINK'])
    content_df['PAGEID'] = content_df['ID'].apply(lambda x: re.findall('[0-9]{5,}', x)[0])
    content_df['POSTID'] = content_df['ID'].apply(lambda x: re.findall('[0-9]{5,}', x)[1])
    content_df['TIME'] = content_df['TIME'].apply(lambda x: datetime.datetime.fromtimestamp(int(x)).strftime("%Y-%m-%d %H:%M:%S"))
    
    feedback_df = pd.DataFrame(feedback_df, columns=['POSTID', 'PAGEID', 'COMMENTCOUNT', 'REACTIONCOUNT', 'SHARECOUNT', 'REACTIONS', 'DISPLAYCOMMENTCOUNT'])
    
    reaction_df = feedback_df.loc[:,['PAGEID', 'POSTID', 'REACTIONS']].explode('REACTIONS')
    reaction_df = reaction_df.loc[reaction_df['REACTIONS'].notnull()]
    reaction_df['COUNT'] = reaction_df['REACTIONS'].apply(lambda x: x['reaction_count'])
    reaction_df['TYPE'] = reaction_df['REACTIONS'].apply(lambda x: x['node']['reaction_type'])
    reaction_df = reaction_df.drop_duplicates(['PAGEID', 'POSTID', 'TYPE'], keep='first')
    reaction_df = reaction_df.pivot(index=['PAGEID', 'POSTID'], columns='TYPE', values='COUNT').reset_index()
    
    df = pd.merge(left=content_df, right=feedback_df, how='left', on=['POSTID', 'PAGEID'])
    df = pd.merge(left=df, right=reaction_df, how='left', on=['POSTID', 'PAGEID'])
    df = df.drop(['ID', 'REACTIONS'], axis=1)
    df = df.fillna(value={'ANGER':0, 'HAHA':0, 'LIKE': 0, 'LOVE':0, 'SORRY':0, 'SUPPORT':0, 'WOW': 0}) 
    df['UPDATETIME'] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")      
    return df


# ============== Group ==============
## Crawl_GroupPosts
def Crawl_GroupPosts(groupurl, until_date='2019-01-01'):
    # init parameters
    rs = requests.Session()
    content_df = [] # post
    feedback_df = [] # reactions
    bac = ''
    break_times = 0
    max_date =  datetime.datetime.now().strftime('%Y-%m-%d')
    headers = {'sec-fetch-site': 'same-origin',
               'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.55 Safari/537.36 Edg/96.0.1054.43',
               'x-fb-lsd': 'GoogleBot'}
    data = {'lsd': 'GoogleBot', 
            '__a': 'GoogleBot'}
    
    # redirect to m.facebook
    groupurl = re.sub('www','m', groupurl)

    # request data and break loop until reach the goal 
    while max_date >= until_date:
        
        # request params
        params = {
            'bac': bac,
            'multi_permalinks': '',
            'refid': '18'
            }
        resp = rs.post(groupurl, headers=headers, params=params, data=data)
        resp = re.sub(r'for \(;;\);', '', resp.text)
        try:
            resp = json.loads(resp)
        except:
            print('Error at josn.load stage.')
            return resp
        soup = BeautifulSoup(resp['payload']['actions'][0]['html'])
        reactions = re.findall('\(new \(require\("ServerJS"\)\)\(\)\).handle\((.*?)\);', resp['payload']['actions'][2]['code'])[0]
        
        try:
            # Parse content
            for post in soup.select('section > article'):
                try:
                    content_df.append([
                        re.findall('"content_owner_id_new":(.*?),', str(post))[0], # ACTORID
                        post.select('strong > a')[0].text, # NAME
                        re.findall('"page_id":"(.*?)"', str(post))[0], # GROUPID
                        re.findall('"mf_story_key":"(.*?)"', str(post))[0], # POSTID
                        re.findall('"publish_time":(.*?),', str(post))[0], # TIME
                        post.find('div',{'data-ft':'{"tn":"*s"}'}).text # CONTENT
                    ])
                except:
                    pass
            # Parse reaction
            for ele in json.loads(reactions)['require']:
                if 'counts' in str(ele):
                    feedback_df.append([
                        ele[3][1]['ft_ent_identifier'], # POSTID
                        ele[3][1]['comment_count'], # comment_count
                        ele[3][1]['share_count'], # # share_count
                        ele[3][1]['like_count'] # like_count
                    ])
             # Update information
            max_date = max([re.findall('"publish_time":(.*?),', str(time['data-ft']))[0] for time in soup.select('section > article')])
            max_date = datetime.datetime.fromtimestamp(int(max_date)).strftime('%Y-%m-%d')
            print(f'TimeStamp: {max_date}.')
            try:
                bac = re.findall('bac=(.*?)%3D', soup.select('div > a.primary')[0]['href'])[0]
            except:
                bac = re.findall('bac=(.*?)&', soup.select('div > a.primary')[0]['href'])[0]
            break_times = 0 # reset break times to zero
            
        except:
            break_times += 1
            print('break_times:', break_times)
            if break_times > 5:
                return soup.select('div > a.primary')[0]['href']
                # return print('ERROR: Please send the following URL to the author. \n', rs.url)
        time.sleep(4)    
    # join content and reactions
    content_df = pd.DataFrame(content_df, columns=['ACTORID','NAME', 'GROUPID', 'POSTID','TIME', 'CONTENT'])
    content_df['TIME'] = content_df['TIME'].apply(lambda x: datetime.datetime.fromtimestamp(int(x)).strftime("%Y-%m-%d %H:%M:%S"))
    
    feedback_df = pd.DataFrame(feedback_df, columns=['POSTID', 'COMMENTCOUNT',  'SHARECOUNT', 'LIKECOUNT'])
    
    df = pd.merge(left=content_df, right=feedback_df, how='left', on='POSTID')
    df['UPDATETIME'] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")  
    return df