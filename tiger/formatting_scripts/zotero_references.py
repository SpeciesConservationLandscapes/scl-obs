from pyzotero import zotero
import pandas as pd
import os
import datetime

# PATHS
PROJECT_DIR = r'C:\Users\jesse\PycharmProjects\scl-obs\tiger'
DATA_DIR = r'C:\Users\jesse\Documents\wcs_tiger\data'

# ZOTERO PARAMETERS
LIBRARY_ID = 2516009
LIBRARY_TYPE = 'group'
API_KEY = "JmEl73qnqQGg1yyZdCilykmM"

def zotero_to_csv(library_id, library_type, api_key, save_dir):

    date = datetime.date.today().strftime("%Y-%m-%d")

    zot = zotero.Zotero(library_id=LIBRARY_ID, library_type=LIBRARY_TYPE, api_key=API_KEY)
    items = zot.everything(zot.top())

    references = []

    for item in items:

        date = item['meta']['parsedDate'].split('-')[0] if 'parsedDate' in item['meta'] else ''

        key = item['data']['key']

        title = item['data']['title']

        if 'creators' in item['data']:
            authors = []
            for author in item['data']['creators']:
                if 'lastName' in author and 'firstName' in author:
                    firstname = author['lastName']
                    lastname = author['lastName']
                    if len(firstname) > 0:
                        firstname = firstname[0]
                    authors.append('{} {}'.format(lastname, firstname))
                elif 'name' in author:
                    authors.append(author['name'])
        authors = ', '.join(authors)

        doi = ''
        if 'DOI' in item['data']:
            doi = item['data']['DOI']

        references.append({ 'key': key, 'date': date, 'title': title, 'authors':authors, 'DOI': doi})

    zotero_df = pd.DataFrame(references)

    if save_dir is True:
        zotero_df.to_csv(os.path.join(save_dir, '{}_{}_references.csv'.format(date, library_id)), index=False)

    return zotero_df