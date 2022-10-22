import sqlite3
import re
import datetime
import requests


def _connect_db():
    conn = sqlite3.connect('./facebook_crawler.db', check_same_thread=False)
    return conn


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


def _init_request_vars(cursor=''):
    # init parameters
    # cursor = ''
    df = []
    max_date = datetime.datetime.now().strftime('%Y-%m-%d')
    break_times = 0
    return df, cursor, max_date, break_times


def _download_images(link):
    filename = link.split(r'?')[0].split(r'/')[-1]
    resp = requests.get(link)
    with open(f'data/photos/{filename}', 'wb') as f:
        f.write(resp.content)


def parse_raw_json(string):
    dic = {}
    for line in string.split('\n'):
        if line != '':
            values = line.split(': ', -1)
            dic[values[0]]= values[1]
    return dic

if '__name__' == '__main__':

    df, cursor, max_date, break_times = _init_request_vars(cursor='aa')
    cursor
