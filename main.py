import urllib
from urllib.request import Request, urlopen, urlretrieve
from bs4 import BeautifulSoup
import os
import pandas as pd 


def getLinks(lang, start, end):
    cols = ['Japanese','Translation','Pronounce','ClipName', 'ClipLink', 'Tag']
    df = pd.DataFrame(columns=cols)
    for lesson in range(start, end + 1):
        # Get the tag: lang + lesson: eg. english_1
        Tag = lang + '_' + str(lesson)
        print('-------------------------------')
        print(Tag)
        url = "https://www.nhk.or.jp/lesson/" + lang + "/learn/list/" + str(lesson) + ".html"
        # print(url)
        
        req = Request(url,headers={'User-Agent': 'Mozilla/5.0'})
        html = urlopen(req).read().decode('utf-8')

        soup = BeautifulSoup(html, features='lxml')

        for tr in soup.find_all('tr', attrs={'class':['line-ja','line-yomi']}):
            if tr.has_attr('class') and tr['class'][0] == 'line-ja':
                Ja_name = tr.find_all('th')[0].text 
                Ja_data = tr.find_all('td')[0].text 
                # Get the Japanese: eg. はじめまして。私はアンナです。(アンナ)
                Japanese = Ja_data + ' ♪ ' + Ja_name
                # print(Japanese)
            else:
                Tr_name = tr.find_all('th')[0].text
                Tr_data = tr.find('div', attrs={'class':'sp-view spDisplay'}).text.strip()
                
                # Get the Translation: eg.  How do you do? I'm Anna. (Anna)  
                Translation = Tr_data
                # print(Translation)

                # Get the Pronounce: eg. HAJIMEMASHITE. WATASHI WA ANNA DESU.
                Pronounce = tr.find_all('td')[0].text.strip().split('\n')[0] + ' ♪ ' + Tr_name
                # print(Pronounce)

                clipNs = tr.find('input')['value'].split(',')
                
                # Get the ClipName: eg. le_1_v_1_sc01.mp3
                ClipName = 'le' + clipNs[0] + '_v_' + clipNs[-1] + '.mp3'

                # Get the ClipLink: eg. 'https://www.nhk.or.jp/lesson/update/mp3/' + clipName
                ClipLink = 'https://www.nhk.or.jp/lesson/update/mp3/' + ClipName
                # print(ClipLink)
                
                # Save to df
                df.loc[len(df)] = [Japanese, Translation, Pronounce, ClipName, ClipLink, Tag]           
    return df



class AppURLopener(urllib.request.FancyURLopener):
    version = "Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 \
               (KHTML, like Gecko) Chrome/47.0.2526.69 Safari/537.36"
urllib._urlopener = AppURLopener()

def download(url, localName):
    print('Downloading ' + localName + ' ...')
    urllib._urlopener.retrieve(url, localName)




def getText(langList, start, end):
    for lang in langList:
        # Create folder according to language.
        lfolder = os.path.join('.', lang)
        if os.path.exists(lfolder) != True:
            os.makedirs(lfolder)
        
        # Get all the text
        df = getLinks(lang, start, end)
        df.to_csv(os.path.join(lfolder, 'text.csv'))


def getMedia(start, end):
    # There is no difference about the source audio --  It's all
    # Japanese. So we don't need to loop all languages. So we choose 
    # the first one. 
    lang = 'arabic'
    # Create folder for media
    mfolder = os.path.join('.', 'Media')
    if os.path.exists(mfolder) != True:
        os.makedirs(mfolder)
    
    df = pd.read_csv(os.path.join('.', lang, 'text.csv'))
    for row in range(len(df)):
        url = df.loc[row]['ClipLink']
        localName = os.path.join(mfolder, df.loc[row]['ClipName'])
        download(url = url, localName = localName)

def makeAnkiCard(langList):
    cols = ['front', 'back', 'tag']
    for lang in langList:
        anki_df = pd.DataFrame(columns=cols)

        # Find and add data df 
        df = pd.read_csv(os.path.join('.', lang, 'text.csv'))
        for row in range(len(df)):
            front = df.loc[row]['Japanese']
            back = df.loc[row]['Translation'] + ' <br/>' + df.loc[row]['Pronounce'] + ' [sound:' + df.loc[row]['ClipName'] + '] '
            tag = df.loc[row]['Tag']
            anki_df.loc[len(anki_df)] = [front, back, tag]  
        # save to file.
        anki_df.to_csv(os.path.join('.', lang, lang + '_anki.csv'), sep = ';', index = False , header=None)



def main():
    languages = ['arabic', 'bengali', 'burmese','chinese', 'english','french',\
                  'hindi','indonesian','korean','persian','portuguese','russian',\
                  'spanish','swahili','thai','urdu','vietnamese']  

    getText(langList=languages, start = 1, end = 48)

    getMedia(start = 1, end = 48)
    
    languages = ['arabic', 'bengali', 'burmese','chinese', 'english','french',\
                  'hindi','indonesian','korean','persian','portuguese','russian',\
                  'spanish','swahili','thai','urdu','vietnamese']  

    makeAnkiCard(langList=languages)

main()
