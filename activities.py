from dataclasses import asdict, dataclass

import httpx
from temporalio import activity
from temporalio.exceptions import ApplicationError


@dataclass
class Purchase:
    item_id: str
    user_id: str


@activity.defn
async def do_purchase(purchase: Purchase) -> None:
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://localhost:5001/purchase", json=asdict(purchase)
        )

        status_code = response.status_code

        if status_code >= 400 and status_code < 500:
            raise ApplicationError(
                f"Status: {status_code}", response.json(), non_retryable=True
            )

        response.raise_for_status()
