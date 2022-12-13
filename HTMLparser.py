from cgitb import text
from pydoc import plain
from tkinter import Place
import requests
import json
import random
from bs4 import BeautifulSoup

def shuffle ():
    url = "https://everynoise.com/"
    href_list = {}
    r = requests.get(url)

    soup = BeautifulSoup(r.content, 'html.parser')
    counter = 0
    table = soup.find(name='div', attrs={'class': 'canvas'})
    for row in table.findAll('div', attrs={'class': 'genre scanme'}):

        href_list.update({row.text[:-2] : reminder(row.text[:-2])}) # row['preview_url']

    # with open('genres.txt', 'w') as file:
        
    #     file.write(json.dumps(href_list, sort_keys=True, indent=2))

    rand_key = random.choice(list(href_list.keys()))
    print (rand_key)

    url += 'engenremap-' + rand_key.replace(' ','') +'.html'
    print (url)

    r = requests.get(url)
    soup = BeautifulSoup(r.content, 'html.parser')

    for link in soup.find_all('a', text = 'playlist'):
        return (link.get('href'))

    return  


def reminder (name):
    url = "https://everynoise.com/"
   

    url += 'engenremap-' + name.replace(' ','') +'.html'   

    r = requests.get(url)
    soup = BeautifulSoup(r.content, 'html.parser')

    for link in soup.find_all('a', text = 'playlist'):
        return (link.get('href'))


# shuffle()
