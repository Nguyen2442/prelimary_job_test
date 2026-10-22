from collections import Counter
from typing import Dict
import httpx
from tenacity import retry, stop_after_attempt, wait_exponential

from app.change_service import process_batch
from app.config import VIETFUL_BASE_URL
from app.models import InventoryItem

PAGE_SIZE = 50


@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=0.2, max=2.0), reraise=True)
def fetch_page(page_index: int) -> dict:
    resp = httpx.get(
        f"{VIETFUL_BASE_URL}/api/v1/Products/inventories",
        params={"PageIndex": page_index, "PageSize": PAGE_SIZE},
        timeout=5.0,
    )
    resp.raise_for_status()
    return resp.json()


def run_poll_cycle() -> Dict[str, int]:
    total = Counter()
    page_index = 0
    while True:
        page = fetch_page(page_index)
        items = [InventoryItem(**i) for i in page["items"]]
        total.update(process_batch(items, "POLL"))
        if not page["hasNextPage"]:
            return dict(total)
        page_index += 1
