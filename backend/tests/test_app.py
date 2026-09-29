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

    async def test_core_routes_are_registered(self) -> None:
        route_paths = {route.path for route in app.routes}

        self.assertIn("/api/stocks/", route_paths)
        self.assertIn("/api/predict/", route_paths)
        self.assertIn("/api/chat/sessions", route_paths)
        self.assertIn("/api/auth/login", route_paths)
        self.assertIn("/api/ml/anomaly/summary", route_paths)


if __name__ == "__main__":
    unittest.main()
