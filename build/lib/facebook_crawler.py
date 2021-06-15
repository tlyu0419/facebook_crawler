import requests
import re
import json
from bs4 import BeautifulSoup
import time
import datetime
import pandas as pd
import numpy as np

# Fans page ==================================================================

## get page id
def get_pageid(pageurl):
    resp = requests.get(pageurl)
    pageid = re.findall('page_id=(.*?)"',resp.text)[0]
    return pageid

## parse_content
def parse_content(data):
    df = []
    soup = BeautifulSoup(data['domops'][0][3]['__html'], 'lxml')
    # post
    for ele in soup.findAll('div', {'class':'userContentWrapper'}):
        try:
            df.append([
                ele.find('img')['aria-label'], #name
                ele.find('div', {'data-testid':'story-subtitle'})['id'], # ID
                ele.find('abbr')['data-utime'], # time
                ''.join([i.text for i in ele.find('div', {'data-testid':'post_message'}).findAll('p')]), # content
                ele.find('a')['href'].split('?')[0] # link
                    ])
        except:
            pass  
    df = pd.DataFrame(data=df, columns=['NAME', 'ID', 'TIME', 'CONTENT', 'LINK'])
    df['PAGEID'] = df['ID'].apply(lambda x: re.split(r'_|;',x)[2])
    df['POSTID'] = df['ID'].apply(lambda x: re.split(r'_|;',x)[3])
    df['TIME'] = df['TIME'].apply(lambda x: datetime.datetime.fromtimestamp(int(x)))
    df = df.drop('ID',axis=1)
    return df

## get_reaction
def get_reaction(data):
    df = []
    # posts
    for ele in data['jsmods']['pre_display_requires']:
        try:
            df.append([
                ele[3][1]['__bbox']['variables']['storyID'], # storyID
                ele[3][1]['__bbox']['result']['data']['feedback']['display_comments_count']['count'],  # display_comments_count
                ele[3][1]['__bbox']['result']['data']['feedback']['comment_count']['total_count'], # total_comments_count
                ele[3][1]['__bbox']['result']['data']['feedback']['reaction_count']['count'], # reaction_count
                ele[3][1]['__bbox']['result']['data']['feedback']['share_count']['count'], # share_count
                ele[3][1]['__bbox']['result']['data']['feedback']['top_reactions']['edges'], # reactions
            ])
        except:
            pass
    
    # vidoes
    for ele in data['jsmods']['require']:
        try:
            
            df.append([
                'S:_I'+ele[3][2]['feedbacktarget']['actorid']+':'+ele[3][2]['feedbacktarget']['targetfbid'], # storyID
                ele[3][2]['feedbacktarget']['commentcount'], # display_comments_count
                ele[3][2]['feedbacktarget']['commentcount'], # total_comments_count
                ele[3][2]['feedbacktarget']['likecount'], # likecount
                ele[3][2]['feedbacktarget']['sharecount'], # sharecount
                [] # reactions
            ])
        except:
            pass
    df = pd.DataFrame(df, columns=['storyID','display_comments_count', 'total_comments_count', 'reaction_count', 'share_count', 'reactions'])
    df['storyID'] = df['storyID'].apply(lambda x: re.sub('S:_I', '',x))
    df['PAGEID'] = df['storyID'].apply(lambda x: re.split(r':',x)[0])
    df['POSTID'] = df['storyID'].apply(lambda x: re.split(r':',x)[1])
    
    # 
    def get_reactions(reactname, reactions):
        for react in reactions:
            if reactname in str(react):
                return react['reaction_count']
        return 0
    df['LIKE'] = df['reactions'].apply(lambda x: get_reactions('LIKE', x))
    df['LOVE'] = df['reactions'].apply(lambda x: get_reactions('LOVE', x))
    df['HAHA'] = df['reactions'].apply(lambda x: get_reactions('HAHA', x))
    df['SUPPORT'] = df['reactions'].apply(lambda x: get_reactions('SUPPORT', x))
    df['WOW'] = df['reactions'].apply(lambda x: get_reactions('WOW', x))
    df['ANGER'] = df['reactions'].apply(lambda x: get_reactions('ANGER', x))
    df['SORRY'] = df['reactions'].apply(lambda x: get_reactions('SORRY', x))
    
    # for vidoe's tpye post
    df['LIKE'] = np.select(condlist = [df['reactions'].apply(lambda x: len(x)==0)], 
                           choicelist=[df['reaction_count']], 
                           default=df['LIKE'])
    return df

# Crawl_PagePosts
def Crawl_PagePosts(pageurl, until_date='2019-01-01'):
    pageid = get_pageid(pageurl) 

    content_df = [] # post
    feedback_df = [] # reactions
    timeline_cursor = ''
    max_date =  datetime.datetime.now()
    break_times = 0
    
    # request date and break loop when reach the goal 
    while max_date >= datetime.datetime.strptime(until_date, '%Y-%m-%d'):
        
        # request params
        url = 'https://www.facebook.com/pages_reaction_units/more/'
        params = {'page_id': pageid,
                  'cursor': str({"timeline_cursor":timeline_cursor,
                                 "timeline_section_cursor":'{}',
                                 "has_next_page":'true'}), 
                  'surface': 'www_pages_home',
                  'unit_count': 20,
                  '__a': '1'}

        try:
            resp = requests.get(url, params=params)
            data = json.loads(re.sub(r'for \(;;\);','',resp.text))
            
            # contesnts：poster's name, poster's ID, post ID, time, content
            ndf = parse_content(data=data)
            content_df.append(ndf)

            # reactions
            ndf1 = get_reaction(data=data)
            feedback_df.append(ndf1)
  
            # update request params
            max_date = ndf['TIME'].max()
            print('TimeStamp: {}.'.format(ndf['TIME'].max()))
            timeline_cursor = re.findall(r'timeline_cursor\\u002522\\u00253A\\u002522(.*?)\\u002522\\u00252C\\u002522timeline_section_cursor',resp.text)[0]
            # break times to zero
            break_times = 0

        except:
            break_times += 1
            print('break_times:', break_times)
        
        time.sleep(2)
        if break_times > 10:
            break
    
    # join content and reactions
    content_df = pd.concat(content_df, ignore_index=True)
    feedback_df = pd.concat(feedback_df, ignore_index=True)
    df = pd.merge(left=content_df, right=feedback_df, how='left', on=['PAGEID', 'POSTID'])
    df = df.loc[:,['NAME', 'TIME', 'CONTENT', 'PAGEID', 'POSTID', 'display_comments_count', 'total_comments_count', 'reaction_count', 'share_count', 'LIKE', 'LOVE', 'HAHA', 'SUPPORT', 'WOW', 'ANGER', 'SORRY']]
    df = df.rename(columns={'display_comments_count':'DISPLAYCOMMENTS', 'total_comments_count':'TOTAL_COMMENTS', 'reaction_count':'REACTIONS','share_count':'SHARES'})
    df['UPDATETIME'] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")      
    print('There are {} posts in DataFrame.'.format(str(df.shape[0])))
    return df

# Group page ==================================================================

## parse_group_content
def parse_group_content(resp):
    soup = BeautifulSoup(resp.text, 'lxml')
    df = []
    for ele in soup.findAll('article'):
        try:
            df.append([
                re.findall('"actor_id":([0-9]{1,})' ,str(ele))[0], # actorid
                re.findall('"top_level_post_id":"(.*?)"' ,str(ele))[0], # postid
                ele.find('strong').text, # actorname
                json.loads(re.findall(r'"post_context":({.*?})', str(ele))[0])['publish_time'], # TIME
                json.loads(re.findall(r'"post_context":({.*?})', str(ele))[0])['story_name'], # story_name
                ele.select_one('div.story_body_container > div').text, # content
                ' '.join([i.text for i in ele.findAll('span', {'class':'_28wy'})]) # reactions
            ])
        except:
            pass

    df = pd.DataFrame(data=df, columns = ['ACTORID','POSTID', 'NAME', 'TIME','STORYNAME', 'CONTENT', 'REACTIONS'])
    df['GROUPID'] = re.findall('\?id=([0-9]{1,})"',resp.text)[0]
    df['TIME'] = df['TIME'].apply(lambda x: datetime.datetime.fromtimestamp(int(x)))
    df['LIKES'] = df['REACTIONS'].apply(lambda x: re.findall('([0-9]{1,}) Like', x)[0] if 'Like' in x else '0')
    df['COMMENTS'] = df['REACTIONS'].apply(lambda x: re.findall('([0-9]{1,}) Comment', x)[0] if 'Comment' in x else '0')
    df['SHARES'] = df['REACTIONS'].apply(lambda x: re.findall('([0-9]{1,}) Share', x)[0] if 'Share' in x else '0')
    df = df.loc[:,['ACTORID', 'NAME', 'GROUPID', 'POSTID', 'TIME', 'STORYNAME', 'CONTENT', 'LIKES', 'COMMENTS', 'SHARES']]
    df['UPDATETIME'] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")   
    return df

## get_bac
def get_bac(resp):
    try:
        bac = re.findall('bac=(.*?)%3D',resp.text)[0]
    except:
        bac = re.findall('bac%3D(.*?)%26', resp.text)[0]
    return bac

## Crawl_GroupPosts
def Crawl_GroupPosts(groupurl, until_date='2019-01-01'):
    
    groupurl = re.sub('www','m','https://www.facebook.com/groups/pythontw')
    headers = {
        'referer': 'https://m.facebook.com/',
        'cookie': 'locale=en_US',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.101 Safari/537.36'
        }
    
    df = []
    bac = ''
    max_date =  datetime.datetime.now()
    break_times = 0
    
    # request data and break loop when reach the goal 
    while max_date >= datetime.datetime.strptime(until_date, '%Y-%m-%d'):
        # request params
        params = {
            'bac': bac,
            'multi_permalinks': '',
            'refid': '18'
            }
        
        resp = requests.get(groupurl, headers=headers, params=params)
        try:
            ndf = parse_group_content(resp)
            df.append(ndf)
            bac = get_bac(resp)
            # update request params
            max_date = ndf['TIME'].sort_values(ascending=False,ignore_index=True)[3] # there are some posts will be pinned at top, so we can't take the max date directly
            print('TimeStamp: {}.'.format(max_date))
            break_times = 0 # break times to zero

        except:
            break_times += 1
            print('break_times:', break_times)
        
        time.sleep(2)
        if break_times > 15:
            break
    
    
    # concat data we collect
    df = pd.concat(df, ignore_index=True)
    print('There are {} posts in DataFrame.'.format(str(df.shape[0])))
    return df