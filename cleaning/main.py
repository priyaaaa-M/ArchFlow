from loguru import logger
from generic import GenericBlogCleaner

raw_text = open("C:/LS_Hackathon/crawlers/Default.txt",encoding="utf-8").read()
logger.info(f"Starting cleaning of article")
generic_cleaned = GenericBlogCleaner().clean(raw_text)

with open("abc.txt", "w", encoding="utf-8") as file:
    file.write(str(generic_cleaned))
logger.info("Article cleaning done and saved to text file")