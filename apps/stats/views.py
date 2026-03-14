from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from apps.blog.models import Post, Comment
from apps.users.models import User

import httpx
import asyncio
from datetime import datetime
import pytz
import logging

logger = logging.getLogger("stats")


class StatsView(APIView):
    """
    GET /api/stats/
    
    Returns blog statistics combined with external data:
    
    - Blog stats: total posts, comments, users
    - Exchange rates (KZT, RUB, EUR)
    - Current time in Asia/Almaty timezone
    
    No authentication required.

    Async chosen so the two external API calls can run concurrently with asyncio.gather.
    If this were synchronous (await one after the other), response time would be the *sum*
    of both latencies instead of the *maximum*.
    """

    async def fetch_exchange_rates(self):
        url = "https://open.er-api.com/v6/latest/USD"
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                resp = await client.get(url)
                resp.raise_for_status()
                data = resp.json()
                rates = data.get("rates", {})
                return {
                    "KZT": rates.get("KZT"),
                    "RUB": rates.get("RUB"),
                    "EUR": rates.get("EUR"),
                }
        except Exception as e:
            logger.error("Failed to fetch exchange rates: %s", e)
            return {"KZT": None, "RUB": None, "EUR": None}

    async def fetch_current_time(self):
        url = "https://timeapi.io/api/time/current/zone?timeZone=Asia/Almaty"
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                resp = await client.get(url)
                resp.raise_for_status()
                data = resp.json()
                return data.get("dateTime")
        except Exception as e:
            logger.error("Failed to fetch current time: %s", e)
            # Fallback: return server UTC time
            return datetime.utcnow().replace(tzinfo=pytz.UTC).isoformat()

    async def get(self, request, *args, **kwargs):
        # Local blog stats
        blog_stats = {
            "total_posts": await asyncio.to_thread(Post.objects.count),
            "total_comments": await asyncio.to_thread(Comment.objects.count),
            "total_users": await asyncio.to_thread(User.objects.count),
        }

        # Concurrent external API calls
        exchange_rates, current_time = await asyncio.gather(
            self.fetch_exchange_rates(),
            self.fetch_current_time(),
        )

        response_data = {
            "blog": blog_stats,
            "exchange_rates": exchange_rates,
            "current_time": current_time,
        }

        return Response(response_data, status=status.HTTP_200_OK)