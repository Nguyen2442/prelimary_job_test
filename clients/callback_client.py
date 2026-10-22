import argparse
import random
from datetime import datetime, timezone
from typing import Any, Dict, List
import httpx
from tenacity import retry, stop_after_attempt, wait_exponential


def fake_inventory(n: int) -> Dict[str, Any]:
    qty = random.randint(10, 200)
    return {
        "sku": f"WH-{n}",
        "partnerSKU": f"P-WH-{n}",
        "warehouseCode": "WH-HCM-01",
        "physicalQty": qty,
        "availableQty": qty,
        "pendingInQty": 0,
        "pendingOutQty": 0,
        "freezeQty": 0,
        "lastUpdatedDate": datetime.now(timezone.utc).isoformat(),
    }


@retry(stop=stop_after_attempt(4), wait=wait_exponential(multiplier=0.2, max=2.0), reraise=True)
def push(cdms_url: str, items: List[Dict[str, Any]]) -> Dict[str, Any]:
    resp = httpx.post(f"{cdms_url}/api/v1/cdc/webhook", json=items, timeout=5.0)
    resp.raise_for_status()
    return resp.json()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--cdms-url", default="http://localhost:18000")
    parser.add_argument("--count", type=int, default=5)
    args = parser.parse_args()

    print(push(args.cdms_url, [fake_inventory(9000 + i) for i in range(args.count)]))
