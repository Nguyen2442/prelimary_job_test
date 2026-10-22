import argparse
from io import BytesIO
from typing import Any, Dict, List
import httpx
import pandas as pd
from tenacity import retry, stop_after_attempt, wait_exponential

from callback_client import fake_inventory


def create_excel_bytes(items: List[Dict[str, Any]]) -> bytes:
    buf = BytesIO()
    pd.DataFrame(items).to_excel(buf, index=False)
    return buf.getvalue()


@retry(stop=stop_after_attempt(4), wait=wait_exponential(multiplier=0.2, max=2.0), reraise=True)
def upload(cdms_url: str, items: List[Dict[str, Any]]) -> Dict[str, Any]:
    files = {"file": ("inventory.xlsx", create_excel_bytes(items))}
    resp = httpx.post(f"{cdms_url}/api/v1/cdc/upload-excel", files=files, timeout=10.0)
    resp.raise_for_status()
    return resp.json()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--cdms-url", default="http://localhost:18000")
    parser.add_argument("--count", type=int, default=5)
    args = parser.parse_args()

    print(upload(args.cdms_url, [fake_inventory(8000 + i) for i in range(args.count)]))
