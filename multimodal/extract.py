import aiohttp
import asyncio
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import os
from pathlib import Path
from typing import List
import time
import nest_asyncio
import platform

# Enable nested event loops (needed for Jupyter/IPython)
nest_asyncio.apply()

class ImageExtractor:
    """
    Asynchronous image extractor for downloading PNG and JPEG images from multiple webpages.
    """
    def __init__(self, output_dir='downloaded_images'):
        self.output_dir = output_dir
        self.downloaded_count = 0
        self.ALLOWED_TYPES = {
            'image/png': '.png'
        }
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        
    async def fetch_page(self, session: aiohttp.ClientSession, url: str) -> str:
        """Fetch webpage content."""
        try:
            async with session.get(url) as response:
                return await response.text()
        except Exception as e:
            print(f"Error fetching {url}: {str(e)}")
            return ""

    async def download_image(self, session: aiohttp.ClientSession, img_url: str, base_url: str) -> bool:
        """Download a single image."""
        try:
            # Convert relative URLs to absolute
            img_url = urljoin(base_url, img_url)
            
            # Skip data URLs
            if img_url.startswith('data:'):
                return False

            # Check content type
            async with session.head(img_url) as head_response:
                content_type = head_response.headers.get('content-type', '').lower()
                if content_type not in self.ALLOWED_TYPES:
                    return False

            # Download image
            async with session.get(img_url) as response:
                if response.status != 200:
                    return False
                    
                file_extension = self.ALLOWED_TYPES[content_type]
                file_name = f"image_{self.downloaded_count}{file_extension}"
                file_path = os.path.join(self.output_dir, file_name)
                
                # Save image
                content = await response.read()
                async with asyncio.Lock():
                    with open(file_path, 'wb') as f:
                        f.write(content)
                    self.downloaded_count += 1
                    print(f"Downloaded: {file_name} from {base_url}")
                return True
                
        except Exception as e:
            print(f"Error downloading {img_url}: {str(e)}")
            return False

    async def process_page(self, session: aiohttp.ClientSession, url: str):
        """Process a single webpage."""
        html = await self.fetch_page(session, url)
        if not html:
            return
            
        soup = BeautifulSoup(html, 'html.parser')
        img_tags = soup.find_all('img')
        
        # Create tasks for all images
        tasks = []
        for img in img_tags:
            img_url = img.get('src')
            if img_url:
                task = self.download_image(session, img_url, url)
                tasks.append(task)
        
        # Execute all image downloads concurrently
        if tasks:
            await asyncio.gather(*tasks)

    async def process_urls(self, urls: List[str]):
        """Process multiple URLs concurrently."""
        connector = aiohttp.TCPConnector(limit=10)  # Limit concurrent connections
        async with aiohttp.ClientSession(
            connector=connector,
            headers={'User-Agent': 'Mozilla/5.0'}
        ) as session:
            tasks = [self.process_page(session, url) for url in urls]
            await asyncio.gather(*tasks)

def extract_images(urls: List[str], output_dir='downloaded_images'):
    """
    Main function to extract images from multiple URLs.
    
    Args:
        urls (List[str]): List of webpage URLs to extract images from
        output_dir (str): Directory to save the images
    """
    start_time = time.time()
    
    # Create extractor instance
    extractor = ImageExtractor(output_dir)
    
    # Get or create event loop based on platform and environment
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    
    # Run the async code
    try:
        loop.run_until_complete(extractor.process_urls(urls))
    finally:
        # Clean up
        if platform.system() != 'Windows':  # Windows doesn't like closing the loop
            loop.close()
    
    # Print summary
    elapsed_time = time.time() - start_time
    print(f"\nDownload complete:")
    print(f"Total images downloaded: {extractor.downloaded_count}")
    print(f"Time taken: {elapsed_time:.2f} seconds")