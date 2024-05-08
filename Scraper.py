from requests_html import HTMLSession
from getpass import getpass
import json
import os
from bs4 import BeautifulSoup
from re import sub
from markdownify import markdownify as md

root_p = "all_challenges"

class Scraper:
    def __init__(self, endpoint = None):
        self.s = HTMLSession()
        self.credentials = {
            "email": "",
            "password": ""
        }
        self.cookies = {}
        self.endpoint = endpoint
        self.html = None

    def __credentials_prompt(self):
        self.credentials["email"] = input("Email: ")
        self.credentials["password"] = getpass("Password: ")

    def login(self, path: str ="/api/login"):
        if not self.credentials["email"]:
            self.__credentials_prompt()
        r = self.s.post(self.endpoint + path, json=self.credentials)
        cookies = json.loads(r.text)
        self.cookies['token'] = cookies['token']

    def __get(self, path: str = ""):
        r = self.s.get(self.endpoint + path)
        r.html.render(sleep=5, localStorage=[self.cookies])
        self.html = r.html.html
    
    def __get_attachment(self, path: str = ""):
        r = self.s.get(self.endpoint + path)
        return r.content
    
    def get_challenges(self):
        self.__get("/challenges")
        soup = BeautifulSoup(self.html, 'html.parser')
        root = soup.findAll("h2")
        for titles in root:
            title_p = self.__ftitles(titles.parent.parent.text)
            print(title_p)
            path = f"{root_p}/{title_p}/"
            print(path)
            if not os.path.exists(path):
                os.makedirs(path)
            category = titles.parent.parent.parent.findAll("h3")
            for el in category:
                category_p = self.__ftitles(el.text)
                print("\t" + category_p)
                path = f"{root_p}/{title_p}/{category_p}/"
                print(path)
                if not os.path.exists(path):
                    os.makedirs(path)
                challenges = el.parent.parent.next_sibling.findChildren("a")
                for chall in challenges:
                    self.__get("/challenges#challenge-" + chall['href']
                           .split("-")[1])
                    csoup = BeautifulSoup(self.html, 'html.parser')
                    card = csoup.select("div.fade.modal.show")[0]
                    chall_title_normal = card.find("div", {"class":"h4"}).text
                    chall_title = self.__ftitles(chall_title_normal)
                    path = f"{root_p}/{title_p}/{category_p}/{chall_title}/"
                    if not os.path.exists(path):
                        os.makedirs(path)
                    chall_description = "\n".join([
                        el.decode_contents() 
                        for el in card.select("div.markdown.bg-body.p-3.mt-3")[0]
                                      .findChildren("p")
                    ])
                    print("\t\t" + chall_title + ".md")
                    with open(f"{path}/{chall_title}.md", "w+") as f:
                        f.write(f'# {chall_title_normal}\n\n')
                        f.write(f'{md(chall_description)}')
                    attachment = card.select("div.mt-2")
                    if attachment:
                        for file in attachment:
                            url = file.find("a")['href']
                            file_name = file.find("button").text.strip()
                            print("\t\t" + file_name)
                            with open(f"{path}/{file_name}", "wb+") as f:
                                f.write(self.__get_attachment(url))
                    print(path)

    def __snake_case(self, s: str = ""):
        return '_'.join(
            sub('\([0-9]+\/[0-9]+\)+', '',
            sub('([A-Z][a-z]+)', r' \1',
            sub('([A-Z]+)', r' \1',
                s.replace('-', ' ').replace('.','')
                 .replace(':','').replace("'", "")))).split()).lower()

    def __ftitles(self, s: str = ""):
        try:
            return self.__snake_case(s) + "_" + s.split("/")[1].strip(")")
        except:
            return self.__snake_case(s)
