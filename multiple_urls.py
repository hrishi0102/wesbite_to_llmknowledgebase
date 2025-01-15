import asyncio
import os
from typing import List
from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig
from crawl4ai.markdown_generation_strategy import DefaultMarkdownGenerator
import requests
from xml.etree import ElementTree
from urllib.parse import urlparse

async def crawl_sequential(urls: List[str]):
    print("\n=== Sequential Crawling with Session Reuse ===")

    # Create 'scraped' directory if it doesn't exist
    os.makedirs('scraped', exist_ok=True)

    browser_config = BrowserConfig(
        headless=True,
        extra_args=["--disable-gpu", "--disable-dev-shm-usage", "--no-sandbox"],
    )

    crawl_config = CrawlerRunConfig(
        markdown_generator=DefaultMarkdownGenerator()
    )

    crawler = AsyncWebCrawler(config=browser_config)
    await crawler.start()

    try:
        session_id = "session1"
        for url in urls:
            result = await crawler.arun(
                url=url,
                config=crawl_config,
                session_id=session_id
            )
            if result.success:
                print(f"Successfully crawled: {url}")
                
                # Create a valid filename from the URL
                parsed_url = urlparse(url)
                # Remove the protocol and replace special characters
                filename = parsed_url.netloc + parsed_url.path
                filename = filename.replace('/', '_').replace('\\', '_').replace('.', '_')
                # Ensure filename isn't too long and add .txt extension
                filename = filename[:240] + '.txt'
                
                # Full path to save the file
                filepath = os.path.join('scraped', filename)
                
                # Save the content to a file
                try:
                    with open(filepath, 'w', encoding='utf-8') as f:
                        f.write(result.markdown_v2.raw_markdown)
                    print(f"Saved content to: {filepath}")
                except Exception as e:
                    print(f"Error saving file {filepath}: {e}")
            else:
                print(f"Failed: {url} - Error: {result.error_message}")
    finally:
        await crawler.close()

def get_pydantic_ai_docs_urls():
    """
    Fetches all URLs from the Pydantic AI documentation.
    Uses the sitemap (https://ai.pydantic.dev/sitemap.xml) to get these URLs.
    
    Returns:
        List[str]: List of URLs
    """            
    sitemap_url = "https://ai.pydantic.dev/sitemap.xml"
    try:
        response = requests.get(sitemap_url)
        response.raise_for_status()
        
        root = ElementTree.fromstring(response.content)
        
        namespace = {'ns': 'http://www.sitemaps.org/schemas/sitemap/0.9'}
        urls = [loc.text for loc in root.findall('.//ns:loc', namespace)]
        
        return urls
    except Exception as e:
        print(f"Error fetching sitemap: {e}")
        return []

async def main():
    urls = get_pydantic_ai_docs_urls()
    if urls:
        print(f"Found {len(urls)} URLs to crawl")
        await crawl_sequential(urls)
    else:
        print("No URLs found to crawl")

if __name__ == "__main__":
    asyncio.run(main())