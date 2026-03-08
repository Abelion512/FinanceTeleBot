from groq import Groq
from pydantic import BaseModel, Field, field_validator
from typing import List, Optional
from src.config import settings
from loguru import logger
from datetime import datetime
from tenacity import retry, stop_after_attempt, wait_exponential
import json

class MarketAnalysis(BaseModel):
    gold_price: float = Field(description="Harga emas antam dalam IDR per gram")
    ihsg_point: float = Field(description="Poin IHSG terbaru")
    summary: str = Field(description="Ringkasan kondisi pasar dalam 2-3 kalimat")
    sentiment: str = Field(description="Sentimen pasar (Positif/Negatif/Netral)")
    recommendation: str = Field(description="Rekomendasi (BELI/JUAL/TUNGGU)")
    reasoning: str = Field(description="Alasan logis dibalik rekomendasi")
    data_date: str = Field(description="Tanggal data yang ditemukan (YYYY-MM-DD)")

    @field_validator('data_date')
    @classmethod
    def validate_date(cls, v):
        try:
            datetime.strptime(v, '%Y-%m-%d')
            return v
        except ValueError:
            return datetime.today().strftime('%Y-%m-%d')

class AnalysisEngine:
    def __init__(self):
        # Menggunakan .get_secret_value() karena GROQ_API_KEY sekarang bertipe SecretStr
        self.client = Groq(api_key=settings.GROQ_API_KEY.get_secret_value())
        self.model = "llama-3.1-8b-instant"

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    async def analyze(self, search_results: List[dict]) -> MarketAnalysis:
        today = datetime.today().strftime('%Y-%m-%d')
        prompt = f"""
        Kamu adalah analis keuangan profesional. Ekstrak data dari hasil pencarian berikut:
        {json.dumps(search_results)}

        PENTING:
        - Tanggal hari ini adalah {today}.
        - JANGAN GUNAKAN DATA JADUL. Jika tidak ada data hari ini, cari data paling baru dan sebutkan tanggalnya di field 'data_date'.
        - Jika harga emas dalam 'juta', konversikan ke angka penuh (misal 1.2jt -> 1200000).
        - Pastikan poin IHSG berupa angka desimal (misal 7200.5).

        Keluarkan hasil dalam format JSON yang valid sesuai dengan schema MarketAnalysis.
        """

        completion = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "You are a financial analyst. Always output JSON based on provided schema."},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"}
        )

        raw_content = completion.choices[0].message.content
        logger.debug(f"LLM Raw Output: {raw_content}")
        return MarketAnalysis.model_validate_json(raw_content)

analyzer = AnalysisEngine()
