import asyncio
from tavily import TavilyClient
from loguru import logger
from tenacity import retry, stop_after_attempt, wait_exponential
from src.config import settings
from datetime import date

class DataFetcher:
    def __init__(self):
        self.client = TavilyClient(api_key=settings.TAVILY_API_KEY.get_secret_value())

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    async def fetch_market_data(self):
        today = date.today()
        # Queries yang lebih spesifik untuk mengurangi halusinasi
        queries = [
            f"harga emas antam per gram hari ini {today} indonesia resmi",
            f"indeks harga saham gabungan IHSG penutupan terbaru {today}",
            f"berita ekonomi makro indonesia terkini {today}"
        ]

        # ⚡ Bolt Optimization: Parallelize searches to reduce total fetch time from O(N) to O(1) relative to request count.
        # This prevents blocking the event loop and significantly speeds up data retrieval.
        logger.info(f"Fetching market data for {len(queries)} queries in parallel...")

        tasks = [
            asyncio.to_thread(self.client.search, query=query, search_depth="advanced", max_results=3)
            for query in queries
        ]

        all_results = await asyncio.gather(*tasks)
        logger.info("Parallel fetching completed successfully.")
        return all_results

fetcher = DataFetcher()
