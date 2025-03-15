import time
import json

class ApiException(Exception):
    def __init__(self, code, msg):
        super().__init__(f"{code} {msg}")
      
class Post:
    def __init__(self):
        self.reset = None
        self.remaining = None
        self.limit = None

async def post(self, endpoint, json: dict, retries: int = 3):
    async with self.lock:
        for i in range(retries):
            now = time.time()
            
            if self._post.remaining is not None and self._post.reset is not None:
                if self._post.remaining < 1:
                    await asyncio.sleep(self._post.reset - now)

            async with self.bot.session.post(
                url=self.url_api_base + endpoint,
                headers=self.headers,
                json=json
            ) as response: #aiohttp.ClientSession, authentication
                _json = await response.json()

                headers = response.headers
                remaining = headers.get("X-RateLimit-Remaining")
                limit = headers.get("X-RateLimit-Limit")
                reset = headers.get("X-RateLimit-Reset")

                if not remaining or not reset:
                    raise Exception("No remaining or reset header")
                
                reset = float(reset)
                remaining = float(remaining)

                self._post.remaining = remaining
                self._post.limit = limit
                self._post.reset = reset

                try:
                    response.raise_for_status()
                    return _json
                except aiohttp.ClientResponseError as response_error:
                    status = response_error.status

                    try:
                        json = await response.json()
                    except:
                        json = {"message": "JSON not returned"}
                    
                    if i == retries - 1:
                        raise ApiException(f"Failed to send request", response_error.status)

                    if status == 429:
                        retry_after = json.get("retry_after", 5) + 1 # adding 1 since retry_after is usually inaccurate
                        await asyncio.sleep(retry_after)
