import os
import datetime
import time
import pandas as pd
import warnings
warnings.filterwarnings("ignore")

from utils import _connect_db, _extract_id, _extract_reactions, _init_request_vars, _get_headers
from requester import _get_homepage, _get_posts
from page_paser import _parse_entryPoint, _parse_identifier, _parse_docid
from post_paser import _parse_composite_nojs, _parse_composite_graphql

def Crawl_PagePosts(pageurl, until_date='2018-01-01'):
    # initial request variables
    df, cursor, max_date, break_times = _init_request_vars()
    
    # get headers
    headers = _get_headers(pageurl)
    
    # Get pageid, postid and entryPoint from homepage_response
    homepage_response = _get_homepage(pageurl, headers)
    entryPoint = _parse_entryPoint(homepage_response)
    identifier = _parse_identifier(entryPoint, homepage_response)
    docid = _parse_docid(entryPoint, homepage_response)
    
    # Keep crawling post until reach the until_date 
    while max_date >= until_date:
        time.sleep(5)
        try:
            # Get posts by identifier, docid and entryPoint
            resp = _get_posts(headers, identifier, entryPoint, docid, cursor)
            if entryPoint == 'nojs':
                ndf, max_date, cursor = _parse_composite_nojs(resp)
                df.append(ndf)
            else:
                ndf, max_date, cursor = _parse_composite_graphql(resp)
                df.append(ndf)
            break_times = 0
        except:
            print('Break Times {}: Something went wrong with this request. Sleep 20 seconds and send request again.'.format(break_times))
            print('REQUEST LOG >>  pageid: {}, docid: {}, cursor: {}'.format(identifier, docid, cursor))
            print('RESPONSE LOG: ', resp.text[:3000])
            print('================================================')
            break_times += 1
            
            if break_times > 15:
                print('Please check your target page/group has up to date.')
                print('If so, you can ignore this break time message, if not, please change your Internet IP and run this crawler again.')
                break
            
            time.sleep(20)
            # Get new headers
            headers = _get_headers(pageurl)
    
    # Concat all dataframes
    df = pd.concat(df, ignore_index=True)
    df['UPDATETIME'] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return df

def Crawl_GroupPosts(pageurl, until_date='2022-01-01'):
    df = Crawl_PagePosts(pageurl, until_date)
    return df

if __name__ == '__main__':

    os.makedirs('data/', exist_ok=True)
    # fb_api_req_friendly_name: ProfileCometTimelineFeedRefetchQuery
    pageurl = 'https://www.facebook.com/Gooaye'

    # fb_api_req_friendly_name: CometModernPageFeedPaginationQuery
    pageurl = 'https://www.facebook.com/emily0806'
    
    # fb_api_req_friendly_name: CometUFICommentsProviderQuery
    pageurl = 'https://www.facebook.com/anuetw/'

    # fb_api_req_friendly_name: GroupsCometFeedRegularStoriesPaginationQuery
    pageurl = 'https://www.facebook.com/groups/corollacrossclub'
    pageurl = 'https://www.facebook.com/groups/pythontw'
    
    # pageurl = 'https://www.facebook.com/diudiu333'

    df = Crawl_PagePosts(pageurl, until_date='2022-08-10')
    df
