import re
import json
import requests
from bs4 import BeautifulSoup
import time
import datetime
import pandas as pd
import numpy as np



# Fans page ==================================================================

# Crawl_PagePosts
def Crawl_PagePosts(pageurl, until_date='2019-01-01'):
    page_id = pagecrawler.get_pageid(pageurl) 
    timeline_cursor = ''

    content_df = [] # post
    feedback_df = [] # reactions
    
    max_date =  datetime.datetime.now()
    break_times = 0
    rs = requests.session()
    # request date and break loop when reach the goal 
    while max_date >= datetime.datetime.strptime(until_date, '%Y-%m-%d'):
        
        try:
            url = 'https://www.facebook.com/pages_reaction_units/more/'
            params = {'page_id': page_id,
                       'cursor': str({"timeline_cursor":timeline_cursor,
                                       "timeline_section_cursor":'{}',
                                       "has_next_page":'true'}), 
                        # 'surface': 'www_pages_home',
                        'surface': 'www_pages_posts',
                        'unit_count': 20,
                        '__a': '1'}
            resp = rs.get(url, params=params)
            data = json.loads(re.sub(r'for \(;;\);','',resp.text))
            
            # contesnts：poster's name, poster's ID, post ID, time, content
            ndf = pageparser.parse_content(data=data)
            content_df.append(ndf)

            # reactions
            ndf1 = pageparser.get_reaction(data=data)
            feedback_df.append(ndf1)
  
            # update request params
            max_date = ndf['TIME'].max()
            print('TimeStamp: {}.'.format(ndf['TIME'].max()))
            timeline_cursor = re.findall(r'timeline_cursor%22%3A%22(.*?)%22%2C%22timeline_section_cursor', data['domops'][0][3]['__html'])[0]
            # break times to zero
            break_times = 0

        except:
            break_times += 1
            print('break_times:', break_times)
            time.sleep(3)
        
        time.sleep(2)
        if break_times > 5:
            break
    
    # join content and reactions
    content_df = pd.concat(content_df, ignore_index=True)
    feedback_df = pd.concat(feedback_df, ignore_index=True)
    
    df = pd.merge(left=content_df, right=feedback_df, how='left', on=['PAGEID', 'POSTID'])
    df = df.loc[:,['NAME', 'TIME', 'CONTENT', 'PAGEID', 'POSTID', 'display_comments_count', 'total_comments_count', 'reaction_count', 'share_count', 'LIKE', 'LOVE', 'HAHA', 'SUPPORT', 'WOW', 'ANGER', 'SORRY']]
    df = df.rename(columns={'display_comments_count':'DISPLAYCOMMENTS', 'total_comments_count':'TOTAL_COMMENTS', 'reaction_count':'REACTIONS','share_count':'SHARES'})
    df['UPDATETIME'] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")      
    print('There are {} posts in the DataFrame.'.format(str(df.shape[0])))
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
    try:
        df['GROUPID'] = re.findall('\?id=([0-9]{1,})"',resp.text)[0]
    except:
        df['GROUPID'] = re.findall('https://m.facebook.com/groups/([0-9]{1,})\?',resp.text)[0]
    df['TIME'] = df['TIME'].apply(lambda x: datetime.datetime.fromtimestamp(int(x)))
    df['LIKES'] = df['REACTIONS'].apply(lambda x: re.findall('([0-9]{1,}) Like', x)[0] if 'Like' in x else '0')
    df['COMMENTS'] = df['REACTIONS'].apply(lambda x: re.findall('([0-9]{1,}) Comment', x)[0] if 'Comment' in x else '0')
    df['SHARES'] = df['REACTIONS'].apply(lambda x: re.findall('([0-9]{1,}) Share', x)[0] if 'Share' in x else '0')
    df = df.loc[:,['ACTORID', 'NAME', 'GROUPID', 'POSTID', 'TIME', 'STORYNAME', 'CONTENT', 'LIKES', 'COMMENTS', 'SHARES']]
    df['UPDATETIME'] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")   
    return df

## get_bac
def get_bac(resp):
    # string = urllib.parse.unquote(resp.text)
    # try:
    #     bac = re.findall('bac=(.*?)%3D',resp.text)[0]
    # except:
    #     bac = re.findall('bac=(.*?)\&multi',resp.text)[0]
    bac = re.findall('bac=([0-9A-Za-z]{10,})',resp.text)[0]

    return bac

# def get_bac(resp):
#     try:
#         bac = re.findall('bac=(.*?)%3D',resp.text)[0]
#         print('type1')
#     except:
#         try:
#             bac = re.findall('bac=(.*?)&amp',resp.text)[0]
#             print('type2')
#         except:
#             bac = re.findall('bac%3D(.*?)%26', resp.text)[0]
#             print('type3')
#     return bac

## Crawl_GroupPosts
def Crawl_GroupPosts(groupurl, until_date='2021-05-01'):
    
    groupurl = re.sub('www','m', groupurl)
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
            
            # update request params
            bac = get_bac(resp) 
            # print(bac)
            # there are some posts will be pinned at top, so we can't take the max date directly
            max_date = ndf['TIME'].sort_values(ascending=False,ignore_index=True)[3] 
            print('TimeStamp: {}.'.format(max_date))
            break_times = 0 # break times to zero

        except:
            break_times += 1
            print('break_times:', break_times)
        
        time.sleep(2)
        if break_times > 5:
            return resp
            # return print('ERROR: Please send the following URL to the author. \n', resp.url)
    
    # concat data we collect
    df = pd.concat(df, ignore_index=True)
    print('There are {} posts in the DataFrame.'.format(str(df.shape[0])))
    return df