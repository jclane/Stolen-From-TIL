import requests
import csv
import os.path
from twitter import *
from time import sleep


class Fact:
    
    """
    This is a class to store the JSON data
    retrieved from get_fact().
    
    Class attribue 'post' contains the JSON
    data for the most recent post.
    
    Class attribute 'title' is title of the 
    post.
    
    Class attribute 'url' is the link to the 
    source of the fact.
    """
    
    
    def __init__(self, data):  
        """
        Initialize Fact object with 'post', 'title', 
        and 'url' attributes.  
        
        Effort is made to clean up the punctuation 
        and wording of the title by removing 'TIL', 
        'about', 'that', 'of', and a comma from the 
        beginning of the string.  A period is added
        at the end if one is not present and the 
        first letter of the string is capitalized if
        not already.
        """
        
        self.post = data['data']['children'][0]['data']
        self.id = self.post['id']
        self.title = self.post['title'].replace("TIL", "").strip()
        self.url = self.post['url']
        
        if self.title.startswith("about"):
            self.title = self.title.replace("about", "", 1).strip()

        if self.title.startswith("that"):
            self.title = self.title.replace("that", "", 1).strip()
            
        if self.title.startswith(","):
            self.title = self.title.replace(",", "", 1).strip()
            
        if self.title.startswith("of"):
            self.title = self.title.replace("of", "", 1).strip()
            
        if not self.title.endswith("."):
            self.title = self.title + "."
            
        self.title = self.title[0].upper() + self.title[1:]
        
    def show(self):
        """
        Prints the title and url to the console
        """
        
        print("\nFACT:")
        print("\n" + self.title)
        print("\n" + self.url + "\n")


def save_fact(data):
    """
    Writes the data to the 'facts.csv' file.
    Will create the file if it does not 
    already exist.
    
    :param data: A list containing the title and url
        of a Fact object.
    """
    
    file_path = "facts.csv"

    if os.path.exists(file_path):
        with open(file_path, "a", newline='', encoding="UTF8") as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(data)
    else:
        with open(file_path, "w", newline='', encoding="UTF8") as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(data)


def check_for_duplicates(title):
    """
    Reads the 'facts.csv' file and compares
    each line to the 'title' parameter.  If
    'title' is found returns 'True' else
    returns 'False'.
    
    :param title: Title as string of the Fact object to 
        be checked.
    :return: Boolean indicating if 'title' is already
        present in the 'facts.csv' file.
    """
    
    file_path = "facts.csv"

    if os.path.exists(file_path):
        with open(file_path, "r", encoding="UTF8") as csvfile:
            reader = csv.reader(csvfile, quotechar='"')
            for row in reader:
                if title == row[0]:
                    return True
                else:
                    continue
    else:
        return False
        

def get_fact():
    """
    Uses 'requests' module to retrieve most recent post from 
    /r/todayilearned in JSON format.
    """
    
    url = "https://www.reddit.com/r/todayilearned/new/.json"
    resp = requests.get(url, headers={'User-agent': 'Simple Test'})
    data = resp.json()
    
    if 'error' not in data.keys():
        return data
    else:
        print("Error fetching fact.")


def tweet_fact(fact):
    """
    Uses 'twitter' module to send tweet.
    
    Tokens and keys are stored in a seperate file
    not included in this repo.
    
    :param fact: 'title' attribute as string of the Fact object to 
        be tweeted.
    """
    
    with open("keys_file.txt", "r") as keys_file:
        keys = keys_file.readlines()
        TOKEN = keys[0].strip("\n")
        TOKEN_KEY = keys[1].strip("\n")
        CON_SEC = keys[2].strip("\n")
        CON_SEC_KEY = keys[3].strip("\n")

    t = Twitter(auth=OAuth(TOKEN, TOKEN_KEY, CON_SEC, CON_SEC_KEY))

    t.statuses.update(status=fact)


while True:
    fact = Fact(get_fact())
        
    if not check_for_duplicates(fact.title):
        fact.show()
        if len(fact.title) <= 140:
            tweet_fact(fact.title)
        save_fact([fact.title, fact.url])
        
    sleep(60)
