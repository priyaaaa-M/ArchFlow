from dotenv import load_dotenv
import os
import crawler
import cleaner

load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

def getURL():
    pass
'''
Write the chatgpt code here to fetch 5 URL I'll have a prompt for that, so input for GPT will be "topic"+"HLD/LLD"+"prompt"
store the links that we got in a list named 'URL'
'''

URL = [] #list of 5 URLs we got from GPT send them to crawler

def scraping():
    #in the crawler.py we have extract function which takes 2 inputs link, topic
    #output for this will a txt file stored in crawler/output directory
    for i in range(len(URL)):
        crawler = genericCrawler()
        crawler.extract(URL[i],topic+str(i+1))
        
def cleaning():
    #read txt files and send them to the following ones and the cleaned files are saved in some directory
    cleaner = SystemDesignCleaner()
    cleaned = cleaner.clean(inp)

'''
Here we need to pass the cleaned txt files all files at once, then the prompt and we get json output returning components
input is "prompt"+"directory" (that contains cleaned .txt files)
'''
def getComponets():
    pass

# htmls are formed from the above thing 