import re
import json
import requests
from bs4 import BeautifulSoup
import time
import datetime
import pandas as pd
import numpy as np

# Fanspage Crawler

## get page id
def get_pageid(pageurl):
    try:
        headers= {'accept': 'text/html',
                  'sec-fetch-mode': 'navigate'}
        resp = requests.get(pageurl, headers=headers)
        pageid = re.findall('page_id=(.*?)"',resp.text)[0]
        return pageid
    except:
        print('Error at get_pageid stage, please check the fanspage could visit in private mode.')
        print(f'You Link: {pageurl}')

## parse page data

## parse_content
def parse_content(data):
    df = []
    soup = BeautifulSoup(data['domops'][0][3]['__html'], features="html.parser")
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
    df['PAGEID'] = df['ID'].apply(lambda x: re.split(r'_|;|-|:',x)[2])
    df['POSTID'] = df['ID'].apply(lambda x: re.split(r'_|;|:-',x)[3])
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

###########################################################################

# Group Crawler
def get_groupid(pageurl):
    try:
        print('To be developed.')
    except:
        pass
