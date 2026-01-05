import time
from abc import ABC, abstractmethod
from tempfile import mkdtemp
import os

import chromedriver_autoinstaller
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from loguru import logger

# Install chromedriver
try:
    chromedriver_path = chromedriver_autoinstaller.install()
    logger.info(f"ChromeDriver installed at: {chromedriver_path}")
except Exception as e:
    logger.warning(f"ChromeDriver auto-install failed: {e}")
    chromedriver_path = None


class BaseCrawler(ABC):

    @abstractmethod
    def extract(self, link: str, title: str, **kwargs) -> None: ...


class BaseSeleniumCrawler(BaseCrawler, ABC):
    def __init__(self, scroll_limit: int = 5) -> None:
        self.scroll_limit = scroll_limit
        
        # Kill any existing Chrome processes to avoid conflicts
        self._cleanup_chrome_processes()
        
        # Create service object if chromedriver path is available
        service = None
        if chromedriver_path and os.path.exists(chromedriver_path):
            service = Service(chromedriver_path)
        
        # Start with the most basic configuration possible
        options = self._get_ultra_basic_chrome_options()
        
        try:
            if service:
                self.driver = webdriver.Chrome(service=service, options=options)
            else:
                self.driver = webdriver.Chrome(options=options)
            
            # Set conservative timeouts
            self.driver.set_page_load_timeout(60)
            self.driver.implicitly_wait(10)
            
            logger.info("Chrome WebDriver initialized with ultra-basic options")
        except Exception as e:
            logger.error(f"Failed with ultra-basic options: {e}")
            # Try even more minimal
            try:
                options = self._get_emergency_chrome_options()
                if service:
                    self.driver = webdriver.Chrome(service=service, options=options)
                else:
                    self.driver = webdriver.Chrome(options=options)
                
                self.driver.set_page_load_timeout(60)
                self.driver.implicitly_wait(10)
                
                logger.info("Chrome WebDriver initialized with emergency options")
            except Exception as e2:
                logger.error(f"All Chrome configurations failed: {e2}")
                raise Exception(f"Cannot initialize Chrome WebDriver: {e2}")

    def _cleanup_chrome_processes(self):
        """Kill only related Chrome processes to avoid interfering with user's browser"""
        try:
            import psutil
            import os
            current_pid = os.getpid()
            killed_count = 0
            
            for proc in psutil.process_iter(['pid', 'name', 'ppid']):
                try:
                    if 'chrome' in proc.info['name'].lower() and 'chromedriver' not in proc.info['name'].lower():
                        # Only kill Chrome processes that are children of this process
                        if proc.info.get('ppid') == current_pid:
                            proc.kill()
                            killed_count += 1
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass
            
            if killed_count > 0:
                logger.info(f"Killed {killed_count} orphan Chrome processes")
                time.sleep(1)
                
        except Exception as e:
            logger.warning(f"Could not cleanup Chrome processes: {e}")

    def _get_ultra_basic_chrome_options(self):
        """Ultra-basic Chrome options - absolute minimum"""
        options = webdriver.ChromeOptions()
        
        # Only the most essential options
        options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")
        # Remove --single-process as it causes renderer crashes
        # options.add_argument("--single-process") 
        options.add_argument("--disable-setuid-sandbox")
        options.add_argument("--window-size=800,600")
        
        # Disable everything possible
        options.add_argument("--disable-extensions")
        options.add_argument("--disable-plugins")
        options.add_argument("--disable-images")
        # options.add_argument("--disable-javascript")  # Enabled JS for modern sites
        options.add_argument("--disable-css")
        options.add_argument("--disable-web-security")
        options.add_argument("--disable-features=VizDisplayCompositor,TranslateUI")
        options.add_argument("--disable-ipc-flooding-protection")
        options.add_argument("--disable-background-networking")
        options.add_argument("--disable-sync")
        options.add_argument("--disable-default-apps")
        options.add_argument("--no-first-run")
        options.add_argument("--no-default-browser-check")
        options.add_argument("--log-level=3")
        options.add_argument("--silent")
        
        # Use a simple temp directory
        temp_dir = os.path.join(os.environ.get('TEMP', '/tmp'), f'chrome_data_{os.getpid()}')
        options.add_argument(f"--user-data-dir={temp_dir}")
        
        # Disable automation detection
        options.add_experimental_option('excludeSwitches', ['enable-automation', 'enable-logging'])
        options.add_experimental_option('useAutomationExtension', False)
        
        self.set_extra_driver_options(options)
        return options
    
    def _get_emergency_chrome_options(self):
        """Emergency fallback - bare minimum options"""
        options = webdriver.ChromeOptions()
        
        # Absolute bare minimum
        options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        # Remove --single-process
        # options.add_argument("--single-process")
        
        self.set_extra_driver_options(options)
        return options

    def set_extra_driver_options(self, options: Options) -> None:
        pass

    def login(self) -> None:
        pass
    
    #Implemented scroll_page functionality which can be used for something like substack but as of now not using it anywhere
    #ingore the following piece of code
    def scroll_page(self) -> None:
        """Scroll page with timeout protection"""
        try:
            current_scroll = 0
            last_height = self.driver.execute_script("return document.body.scrollHeight")
            
            while current_scroll < self.scroll_limit:
                # Scroll down
                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                
                # Wait for page to load - reduced from 5 to 2 seconds
                time.sleep(2)
                
                # Check if we've reached the bottom
                new_height = self.driver.execute_script("return document.body.scrollHeight")
                if new_height == last_height:
                    break
                    
                last_height = new_height
                current_scroll += 1
                
        except Exception as e:
            logger.warning(f"Error during page scrolling: {e}")
            # Continue without scrolling if there's an issue
