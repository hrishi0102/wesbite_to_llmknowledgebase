import asyncio
from crawl4ai import *

async def main():
    async with AsyncWebCrawler() as crawler:
        result = await crawler.arun(
            url="https://www.nbcnews.com/business",
        )
        # Write the markdown content to a file
        with open('crawl_results.txt', 'w', encoding='utf-8') as f:
            f.write(result.markdown)

if __name__ == "__main__":
    asyncio.run(main())