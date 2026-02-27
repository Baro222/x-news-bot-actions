LibreTranslate self-host quickstart

1. Requirements
   - Docker & docker-compose installed on your host (small VPS or local machine)

2. Start
   - git clone ... (if needed)
   - docker-compose up -d
   - The service will be available at http://<host>:5000/translate

3. Integration
   - Set environment variable LIBRETRANSLATE_URL to your host URL, e.g. http://127.0.0.1:5000/translate
   - ai_processor.py already uses LIBRETRANSLATE_URL or defaults to https://libretranslate.de/translate

4. Notes
   - Self-hosting avoids reliance on public instance and improves reliability.
   - Resource needs are small for light traffic (256-512MB RAM may work for low volume).
