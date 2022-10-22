from paser import _parse_category, _parse_pagename, _parse_creation_time, _parse_pagetype, _parse_likes, _parse_docid, _parse_pageurl
from paser import _parse_entryPoint, _parse_identifier, _parse_docid, _parse_composite_nojs, _parse_composite_graphql, _parse_relatedpages, _parse_pageinfo
from requester import _get_homepage, _get_posts, _get_headers
from utils import _init_request_vars
from bs4 import BeautifulSoup
import os
import re

import json
import time
import tqdm

import pandas as pd
import pickle

import datetime
import warnings
warnings.filterwarnings("ignore")


def Crawl_PagePosts(pageurl, until_date='2018-01-01', cursor=''):
    # initial request variables
    df, cursor, max_date, break_times = _init_request_vars(cursor)

    # get headers
    headers = _get_headers(pageurl)

    # Get pageid, postid and entryPoint from homepage_response
    homepage_response = _get_homepage(pageurl, headers)
    entryPoint = _parse_entryPoint(homepage_response)
    identifier = _parse_identifier(entryPoint, homepage_response)
    docid = _parse_docid(entryPoint, homepage_response)

    # Keep crawling post until reach the until_date
    while max_date >= until_date:
        try:
            # Get posts by identifier, docid and entryPoint
            resp = _get_posts(headers, identifier, entryPoint, docid, cursor)
            if entryPoint == 'nojs':
                ndf, max_date, cursor = _parse_composite_nojs(resp)
                df.append(ndf)
            else:
                ndf, max_date, cursor = _parse_composite_graphql(resp)
                df.append(ndf)
            # Test
            # print(ndf.shape[0])
            break_times = 0
        except:
            # print(resp.json()[:3000])
            try:
                if resp.json()['data']['node']['timeline_feed_units']['page_info']['has_next_page'] == False:
                    print('The posts of the page has run over!')
                    break
            except:
                pass
            print('Break Times {}: Something went wrong with this request. Sleep 20 seconds and send request again.'.format(
                break_times))
            print('REQUEST LOG >>  pageid: {}, docid: {}, cursor: {}'.format(
                identifier, docid, cursor))
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


def Crawl_RelatedPages(seedpages, rounds):
    # init
    df = pd.DataFrame(data=[], columns=['SOURCE', 'TARGET', 'ROUND'])
    pageurls = list(set(seedpages))
    crawled_list = list(set(df['SOURCE']))
    headers = _get_headers(pageurls[0])
    for i in range(rounds):
        print('Round {} started at: {}!'.format(
            i, datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
        for pageurl in tqdm(pageurls):
            if pageurl not in crawled_list:
                try:
                    homepage_response = _get_homepage(
                        pageurl=pageurl, headers=headers)
                    if 'Sorry, something went wrong.' not in homepage_response.text:
                        entryPoint = _parse_entryPoint(homepage_response)
                        identifier = _parse_identifier(
                            entryPoint, homepage_response)
                        relatedpages = _parse_relatedpages(
                            homepage_response, entryPoint, identifier)
                        ndf = pd.DataFrame({'SOURCE': homepage_response.url,
                                            'TARGET': relatedpages,
                                            'ROUND': i})
                        df = pd.concat([df, ndf], ignore_index=True)
                except:
                    pass
                    # print('ERROE: {}'.format(pageurl))
        pageurls = list(set(df['TARGET']))
        crawled_list = list(set(df['SOURCE']))
    return df


def Crawl_PageInfo(pagenum, pageurl):
    break_times = 0
    global headers
    while True:
        try:
            homepage_response = _get_homepage(pageurl, headers)
            pageinfo = _parse_pageinfo(homepage_response)
            with open('data/pageinfo/' + str(pagenum) + '.pickle', "wb") as fp:
                pickle.dump(pageinfo, fp)
            break
        except:
            break_times = break_times + 1
            if break_times >= 5:
                break
            time.sleep(5)
            headers = _get_headers(pageurl=pageurl)


if __name__ == '__main__':

    os.makedirs('data/', exist_ok=True)
    # ===== fb_api_req_friendly_name: ProfileCometTimelineFeedRefetchQuery ====
    pageurl = 'https://www.facebook.com/Gooaye'  # 股癌 Gooaye: 30.4萬追蹤,
    pageurl = 'https://www.facebook.com/StockOldBull'  # 股海老牛: 16萬
    pageurl = 'https://www.facebook.com/twherohan'
    pageurl = 'https://www.facebook.com/diudiu333'
    pageurl = 'https://www.facebook.com/chengwentsan'
    pageurl = 'https://www.facebook.com/MaYingjeou'
    pageurl = 'https://www.facebook.com/roberttawikofficial'
    pageurl = 'https://www.facebook.com/NizamAbTitingan'
    pageurl = 'https://www.facebook.com/joebiden'

    # ==== fb_api_req_friendly_name: CometModernPageFeedPaginationQuery ====
    pageurl = 'https://www.facebook.com/ebcmoney/'  # 東森財經: 81萬追蹤
    pageurl = 'https://www.facebook.com/moneyweekly.tw/'  # 理財周刊: 36.3萬
    pageurl = 'https://www.facebook.com/cmoneyapp/'  # CMoney 理財寶: 84.2萬
    pageurl = 'https://www.facebook.com/emily0806'  # 艾蜜莉-自由之路: 20.9萬追蹤
    pageurl = 'https://www.facebook.com/imoney889/'  # 林恩如-飆股女王: 10.2萬
    pageurl = 'https://www.facebook.com/wealth1974/'  # 財訊: 17.5萬
    pageurl = 'https://www.facebook.com/smart16888/'  # 郭莉芳理財講堂: 1.6萬
    pageurl = 'https://www.facebook.com/smartmonthly/'  # Smart 智富月刊: 52.6萬
    pageurl = 'https://www.facebook.com/ezmoney.tw/'  # 統一投信: 1.5萬
    pageurl = 'https://www.facebook.com/MoneyMoneyMeg/'  # Money錢: 20.7萬
    pageurl = 'https://www.facebook.com/imoneymagazine/'  # iMoney 智富雜誌: 38萬
    pageurl = 'https://www.facebook.com/edigest/'  # 經濟一週 EDigest: 36.2萬
    pageurl = 'https://www.facebook.com/BToday/'  # 今周刊:107萬
    pageurl = 'https://www.facebook.com/GreenHornFans/'  # 綠角財經筆記: 25萬
    pageurl = 'https://www.facebook.com/ec.ltn.tw/'  # 自由時報財經頻道 42,656人在追蹤
    pageurl = 'https://www.facebook.com/MoneyDJ'  # MoneyDJ理財資訊 141,302人在追蹤
    pageurl = 'https://www.facebook.com/YahooTWFinance/'  # Yahoo奇摩股市理財 149,624人在追蹤
    pageurl = 'https://www.facebook.com/win3105'
    pageurl = 'https://www.facebook.com/Diss%E7%BA%8F%E7%B6%BF-111182238148502/'

    # fb_api_req_friendly_name: CometUFICommentsProviderQuery
    pageurl = 'https://www.facebook.com/anuetw/'  # Anue鉅亨網財經新聞: 31.2萬追蹤
    pageurl = 'https://www.facebook.com/wealtholic/'  # 投資癮 Wealtholic: 2.萬

    # fb_api_req_friendly_name: PresenceStatusProviderSubscription_ContactProfilesQuery
    # fb_api_req_friendly_name: GroupsCometFeedRegularStoriesPaginationQuery
    pageurl = 'https://www.facebook.com/groups/pythontw'
    pageurl = 'https://www.facebook.com/groups/corollacrossclub/'

    df = Crawl_PagePosts(pageurl, until_date='2022-08-10')
    # df = Crawl_RelatedPages(seedpages=pageurls, rounds=10)

    df = pd.read_csv(
        './data/relatedpages_edgetable.csv')[['SOURCE', 'TARGET', 'ROUND']]

    headers = _get_headers(pageurl=pageurl)

    for pagenum in tqdm(df['index']):
        try:
            Crawl_PageInfo(pagenum=pagenum, pageurl=df['pageurl'][pagenum])
        except:
            pass

    homepage_response = _get_homepage(pageurl, headers)
    pageinfo = _parse_pageinfo(homepage_response)

    #
    import pandas as pd
    from main import Crawl_PagePosts
    pageurl = 'https://www.facebook.com/hatendhu'
    df = Crawl_PagePosts(pageurl, until_date='2014-11-01')
    df
    df.to_pickle('./data/20220926_hatendhu.pkl')
