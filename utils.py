import sqlite3
import re
import datetime
import requests


def _connect_db():
    conn = sqlite3.connect('./facebook_crawler.db', check_same_thread=False)
    return conn

def _get_headers(pageurl):
    '''
    Send a request to get cookieid as headers.
    '''
    pageurl = re.sub('www', 'm', pageurl)
    resp = requests.get(pageurl)
    headers={'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
             'accept-language': 'en'}
    headers['cookie'] = '; '.join(['{}={}'.format(cookieid, resp.cookies.get_dict()[cookieid]) for cookieid in resp.cookies.get_dict()])
    # headers['cookie'] = headers['cookie'] + '; locale=en_US'
    return headers

def _extract_id(string, num):
    '''
    Extract page and post id from the feed_subtitle infroamtion
    '''
    try:
        return re.findall('[0-9]{5,}', string)[num]
    except:
        print('ERROR from extract {}'.froamt(string))
        return string

def _extract_reactions(reactions, reaction_type):
    '''
    Extract reaction_type from reactions.
    Possible reaction_type's value will be one of ['LIKE', 'HAHA', 'WOW', 'LOVE', 'SUPPORT', 'SORRY', 'ANGER'] 
    '''
    for reaction in reactions:
        if reaction['node']['localized_name'].upper() == reaction_type.upper():
            return reaction['reaction_count']
    return 0

def _init_request_vars():
    # init parameters
    df = []
    cursor = ''
    max_date = datetime.datetime.now().strftime('%Y-%m-%d')
    break_times = 0
    return df, cursor, max_date, break_times

if '__name__' == '__main__':
    pass