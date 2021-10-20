import re
import json
import requests

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

