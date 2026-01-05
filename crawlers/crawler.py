from bs4 import BeautifulSoup
from loguru import logger
from .base import BaseSeleniumCrawler


class genericCrawler(BaseSeleniumCrawler):

    def set_extra_driver_options(self, options) -> None:
        pass

    def extract(self, link, titlez, **kwargs) -> None:
        try:
            logger.info(f"Starting scrapping of article: {link}")

            self.driver.get(link)
            
            # Skip scrolling to avoid potential issues - just get the initial page content
            # Most content is available without scrolling anyway
            
            soup = BeautifulSoup(self.driver.page_source, "html.parser")
            title = soup.find_all("h1", class_="pw-post-title")
            subtitle = soup.find_all("h2", class_="pw-subtitle-paragraph")

            data = {
                "Title": title[0].string if title else None,
                "Subtitle": subtitle[0].string if subtitle else None,
                "Content": soup.get_text(),
            }

            user = kwargs.get("user")
            
            #some xyz folder this is to be saved
            # Suppose your data is in this variable
            with open(titlez+".txt", "w", encoding="utf-8") as file:
                file.write(str(data))

            #push to database placeholder or put it in a txt file or something something this is all before preprocessing
            #we can have a txt file created like title_link1.txt for each URL we parsed and if that file doesn't exist in the folder.

            logger.info(f"Successfully scraped and saved article: {link}")
            
        except Exception as e:
            logger.error(f"Error scraping {link}: {str(e)}")
            raise
        finally:
            try:
                if hasattr(self, 'driver'):
                    self.driver.quit()
                    logger.info("Chrome driver closed successfully")
            except Exception as e:
                logger.warning(f"Error during driver.quit(): {str(e)}")


def main():
    link = "https://www.geeksforgeeks.org/system-design/system-design-of-uber-app-uber-system-architecture/"

    crawler = genericCrawler()
    crawler.extract(link=link, user=None, titlez="Default")  # pass real user if required

if __name__ == "__main__":
    main()

