from nltk.corpus import wordnet
from bs4 import BeautifulSoup

import functools
import timeit
import os, glob, re, requests

word = input('Enter a word to search for : ');
nor = int(input('How many Search Results ? '));
nhood = int(input('NeighbourHood for the keyword ? '))

curr_path = os.getcwd()

stopwords = ['ourselves', 'hers', 'between', 'yourself', 'but', 'again', 'there', 'about', 'once', 'during', 'out', 'very', 'having', 'with', 'they', 'own', 'an', 'be', 'some', 'for', 'do', 'its', 'yours', 'such', 'into', 'of', 'most', 'itself', 'other', 'off', 'is', 's', 'am', 'or', 'who', 'as', 'from', 'him', 'each', 'the', 'themselves', 'until', 'below', 'are', 'we', 'these', 'your', 'his', 'through', 'don', 'nor', 'me', 'were', 'her', 'more', 'himself', 'this', 'down', 'should', 'our', 'their', 'while', 'above', 'both', 'up', 'to', 'ours', 'had', 'she', 'all', 'no', 'when', 'at', 'any', 'before', 'them', 'same', 'and', 'been', 'have', 'in', 'will', 'on', 'does', 'yourselves', 'then', 'that', 'because', 'what', 'over', 'why', 'so', 'can', 'did', 'not', 'now', 'under', 'he', 'you', 'herself', 'has', 'just', 'where', 'too', 'only', 'myself', 'which', 'those', 'i', 'after', 'few', 'whom', 't', 'being', 'if', 'theirs', 'my', 'against', 'a', 'by', 'doing', 'it', 'how', 'further', 'was', 'here', 'than']

##########################################################################
####################  FROM WORDNET  ######################################
##########################################################################

def wordDetails(f,x):

    text = x.definition()
    text = re.sub(r'[^a-zA-Z ]','', text)
    text = text.split()
    res  = [word for word in text if word.lower() not in stopwords]
    text = ' '.join(res)
    f.write(text + " ")

    for text in x.examples():
        text = re.sub(r'[^a-zA-Z ]','', text)
        text = text.split()
        res  = [word for word in text if word.lower() not in stopwords]
        text = ' '.join(res)
        f.write(text + " ")

    for synonym in x.lemmas():
        text = synonym.name()
        text = re.sub(r'[^a-zA-Z ]','', text)
        text = text.split()
        res  = [word for word in text if word.lower() not in stopwords]
        text = ' '.join(res)
        f.write(text + " ")

    return;

def get_hyponyms(synset):
    hyponyms = set()
    for hyponym in synset.hyponyms():
        hyponyms |= set(get_hyponyms(hyponym))
    return hyponyms | set(synset.hyponyms())

def get_hypernyms(synset):
    hypernyms = set()
    for hypernym in synset.hypernyms():
        hypernyms |= set(get_hypernyms(hypernym))
    return hypernyms | set(synset.hypernyms())


def writeDataWord(f, x):
    wordDetails(f,x)
    for hypo in get_hyponyms(x):
        wordDetails(f, hypo)
    for hyper in get_hypernyms(x):
        wordDetails(f, hyper)
    for mero in x.part_meronyms():
        wordDetails(f, mero)
    return;
        
def comparator(x, y):
    return wordnet.synset(x.name()).lemmas()[0].count() - wordnet.synset(y.name()).lemmas()[0].count();

syns = []
syns.append(wordnet.synsets(word, pos=wordnet.VERB))
syns.append(wordnet.synsets(word, pos=wordnet.NOUN))
syns.append(wordnet.synsets(word, pos=wordnet.ADJ))
syns.append(wordnet.synsets(word, pos=wordnet.ADV))

for x in range(0,4):
    syns[x].sort(key = functools.cmp_to_key(comparator), reverse = True)

directory = os.path.join(curr_path, word) + '\\X'
dw = directory + '\\'

if not os.path.exists(directory):
    os.makedirs(directory)

fileCnt = 0
for x in syns:
    for i in range(0,min(5, len(x))):
        filePath = os.path.join(directory, (word+str(fileCnt)+".txt"))
        f = open(filePath,"w")
        writeDataWord(f, x[i])
        fileCnt = fileCnt + 1
        f.close()

##########################################################################
##########################################################################
##########################################################################
        
start = timeit.default_timer()

USER_AGENT = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36'}

directory = os.path.join(curr_path, word)
if not os.path.exists(directory):
    os.makedirs(directory)

def fetch_results(search_term, number_results, language_code):
    assert isinstance(search_term, str), 'Search term must be a string'
    assert isinstance(number_results, int), 'Number of results must be an integer'
    escaped_search_term = search_term.replace(' ', '+')

    google_url = 'https://www.google.co.in/search?q={}&num={}&hl={}'.format(escaped_search_term, number_results, language_code)
    response = requests.get(google_url, headers=USER_AGENT)
    response.raise_for_status()

    return search_term, response.text

def cleanify(s):
    import urllib
    from bs4 import BeautifulSoup

    soup = BeautifulSoup(s, 'html.parser')

    for script in soup(['script', 'style']):
        script.extract()

    if soup.body is None:
        return '--- No Body ---'
    
    text = soup.body.get_text(separator = ' ')

    # break into lines and remove leading and trailing space on each
    lines = (line.strip() for line in text.splitlines())

    # break multi-headlines into a line each
    chunks = (phrase.strip() for line in lines for phrase in line.split("  "))

    # drop blank lines
    text = '\n'.join(chunk for chunk in chunks if chunk)

    # text = re.sub('\\n', '', text)
    # text = re.sub('\\t', ' ', text)

    text = re.sub(r'<.*>', ' ', text)
    
    text = re.sub(r'(\\.)', '', text)
    text = re.sub(r'(\\x..)', '', text)

    text = re.sub(r'([a-zA-Z]*\d+[a-zA-Z]*)', '', text)
    text = re.sub(r'[^a-zA-Z ]',' ', text)

    text = re.sub(r' +', ' ', text)

    text = text.split()

    res  = [word for word in text if word.lower() not in stopwords]
    text = ' '.join(res)

    return text

def parseMain(result):
    link = result.find('a', href=True)
    title = result.find('h3', attrs={'class': 'r'})
    description = result.find('span', attrs={'class': 'st'})
    if link and title:
        link = link['href']
        title = title.get_text()
        if link != '#':
            name = re.sub(r'[\/\\:\*\?\"\|]', ' ', title)
            filePath = os.path.join(directory, (name +".txt"))

            f = open(filePath,"w")
            response = requests.get(link, headers=USER_AGENT)
            s = cleanify(str(response.text.encode("utf-8")))
            s = s.lower()
            f.write(s)
            f.close()

            filePath = os.path.join(directory, ("_" + name +".txt"))
            f = open(filePath,"w")
            s1 = s.split(" ")
            s2 = [i for i, x in enumerate(s1) if x == word]
            for x in s2:
                l = [0]*fileCnt;
                s = '  '
                for i in range(max(0,x-nhood),min(len(s1), x+nhood+1)):
                    s = s + s1[i] + " "

                    for g in range(fileCnt):
                        f1 = dw + word + str(g) + '.txt'
                        f1 = open(f1, 'r')
                        s3 = f1.read()
                        if s3.find(s1[i]+" ") != -1:
                            l[g] = l[g] + 1;
                        f1.close()
                        
                f.write(str(l.index(max(l))));
                f.write(s);
                f.write(str(l));
                f.write('\n')
            f.close()
            
import threading
def parse_results(html, keyword):
    soup = BeautifulSoup(html, 'html.parser')
    found_results = []
    
    result_block = soup.find_all('div', attrs={'class': 'g'})
    threads = list()
    for result in result_block:
        t = threading.Thread(target = parseMain, args=(result,))
        t.start()
        threads.append(t)
    for t in threads:
        t.join()       
    return ;


keyword, html = fetch_results(word, nor, 'en')
parse_results(html, keyword)

stop = timeit.default_timer()
print (stop-start)
