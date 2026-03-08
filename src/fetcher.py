from tavily import TavilyClient
from loguru import logger
from tenacity import retry, stop_after_attempt, wait_exponential
from src.config import settings
from datetime import date

class DataFetcher:
    def __init__(self):
        # Menggunakan .get_secret_value() karena TAVILY_API_KEY sekarang bertipe SecretStr
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

        all_results = []
        for query in queries:
            logger.info(f"Searching: {query}")
            search_result = self.client.search(query=query, search_depth="advanced", max_results=3)
            all_results.append(search_result)

        return all_results

fetcher = DataFetcher()
