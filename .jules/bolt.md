## 2026-03-08 - [Sequential I/O in Async Methods]
**Learning:** Found that `DataFetcher.fetch_market_data` and `AnalysisEngine.analyze` were performing synchronous API calls sequentially within async functions, blocking the event loop and increasing total execution time.
**Action:** Use `asyncio.gather` with `asyncio.to_thread` (or native async clients) to parallelize I/O operations and prevent event loop blocking.
