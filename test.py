# from cgitb import text
# from pydoc import plain
# from tkinter import Place
# import requests
# import json
# import re
# import random
# from bs4 import BeautifulSoup


# url = "https://everynoise.com/"
# href_list = []
# list_genre = {}

# r = requests.get(url)

# soup = BeautifulSoup(r.content, 'html.parser')
# counter = 0
# table = soup.find(name='div', attrs={'class': 'canvas'})

# for row in table.findAll('div', attrs={'class': 'genre scanme'}):
#     label = row.text[:-2]
#     href_list.append(label)

# with open('href_list.txt', 'w') as file:        
#     file.write(json.dumps(href_list, indent=2))
# print (len(href_list))

# for label in href_list:
#     try:
#         s = "musica cabo-verdiana"
#         input_ = re.sub('[^0-9a-zA-Z]+', '', label)
#         # print(input_)
#         r = requests.get("https://everynoise.com/engenremap-"+ input_ +'.html')
#         soup = BeautifulSoup(r.content, 'html.parser')
#         link = soup.find("a", string="playlist")
#         try:
#             link = link.get('href')   
#         except Exception as E:       
#             print (str(E))     
#             list_genre.update({label: " empty "})            
#         else :
#             list_genre.update({label: link})

#             # for link in soup.find_all('a', text = 'playlist'):
#             #     href_list.update({label : link.get('href')})
#             #     # print (label,'\t'*3,link.get('href'))
#             # counter+=1
#             # print (counter, ': ', label, ' -> ', link)
#             # if counter is 10:
#             #     break

#         finally:
#             counter+=1
#             with open('genres.txt', 'w') as file:        
#                 file.write(json.dumps(list_genre, indent=2))

#     except Exception as E:
#         print(str(E))

    

    

from cgitb import text
from pydoc import plain
from tkinter import Place
import requests
import json
import re
import random
from bs4 import BeautifulSoup

with open('genres.txt', 'r') as file:        
    g_list = json.load(file)
    file.close()

for key, value in g_list.items():
    if value == " empty ":
        try:
            r = requests.get("https://everynoise.com/engenremap-"+ re.sub('[^0-9a-zA-Z]+', '', key) +'.html')
            # print (key)
            soup = BeautifulSoup(r.content, 'html.parser')
            link = soup.find("a", string="playlist")
            # print (link)
            try:
                link = link.get('href')   
            except Exception as E:       
                print (key , " INNER Exception",str(E))     
                # g_list.update({key: " empty "})            
            else :
                g_list[key] = link
            

        except Exception as E:
            print("top Exception",str(E))

        finally:                
            with open('genres.txt', 'w') as file:        
                file.write(json.dumps(g_list, indent=2))
                file.close()


# url = "https://everynoise.com/"
# href_list = []
# list_genre = {}

# r = requests.get(url)

# soup = BeautifulSoup(r.content, 'html.parser')
# counter = 0
# table = soup.find(name='div', attrs={'class': 'canvas'})

# for row in table.findAll('div', attrs={'class': 'genre scanme'}):
#     label = row.text[:-2]
#     href_list.append(label)

# with open('href_list.txt', 'w') as file:        
#     file.write(json.dumps(href_list, indent=2))
# print (len(href_list))

# for label in href_list:
#     try:
#         s = "musica cabo-verdiana"
#         input_ = re.sub('[^0-9a-zA-Z]+', '', label)
#         # print(input_)
#         r = requests.get("https://everynoise.com/engenremap-"+ input_ +'.html')
#         soup = BeautifulSoup(r.content, 'html.parser')
#         link = soup.find("a", string="playlist")
#         try:
#             link = link.get('href')   
#         except Exception as E:       
#             print (str(E))     
#             list_genre.update({label: " empty "})            
#         else :
#             list_genre.update({label: link})

#             # for link in soup.find_all('a', text = 'playlist'):
#             #     href_list.update({label : link.get('href')})
#             #     # print (label,'\t'*3,link.get('href'))
#             # counter+=1
#             # print (counter, ': ', label, ' -> ', link)
#             # if counter is 10:
#             #     break

#         finally:
#             counter+=1
#             with open('genres.txt', 'w') as file:        
#                 file.write(json.dumps(list_genre, indent=2))

#     except Exception as E:
#         print(str(E))

    

    

