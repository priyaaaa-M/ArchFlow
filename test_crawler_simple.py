from crawlers.crawler import genericCrawler
import os

def test_crawler():
    link = "https://www.google.com" # Using a very stable site for testing
    titlez = "test_scrape"
    
    print(f"Testing crawler with {link}...")
    try:
        crawler = genericCrawler()
        crawler.extract(link=link, titlez=titlez)
        
        if os.path.exists(titlez + ".txt"):
            print("SUCCESS: Data scraped and saved.")
            # os.remove(titlez + ".txt")
        else:
            print("FAILURE: File not created.")
            
    except Exception as e:
        print(f"ERROR: {e}")

if __name__ == "__main__":
    test_crawler()
