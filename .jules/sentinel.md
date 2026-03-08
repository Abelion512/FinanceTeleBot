## 2025-05-23 - [Secret Protection & Error Sanitization]
**Vulnerability:** API keys (Tavily, Groq) and Telegram Bot Tokens were stored as plain strings in configuration and potentially leaked in logs or error messages.
**Learning:** Using plain strings for sensitive credentials in Pydantic models allows them to be accidentally printed or logged. Additionally, returning raw exception strings to users can leak internal system details.
**Prevention:** Use `SecretStr` for all sensitive credentials and implement generic error messages for end-users while logging detailed errors internally.
