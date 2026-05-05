import unittest

import httpx

from src.main import app


class AppSmokeTests(unittest.IsolatedAsyncioTestCase):
    async def test_read_root(self) -> None:
        transport = httpx.ASGITransport(app=app)
        async with httpx.AsyncClient(
            transport=transport,
            base_url="http://testserver",
        ) as client:
            response = await client.get("/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"message": "Welcome to StockAI API"})


if __name__ == "__main__":
    unittest.main()
