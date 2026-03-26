from ollama import Client
from pydantic import BaseModel
from typing import List, Optional
from dotenv import load_dotenv
import os

load_dotenv()


class Item(BaseModel):
    name: str
    price: int


class Receipt(BaseModel):
    store_name: Optional[str]
    date: Optional[str]
    items: List[Item]
    total_amount: Optional[int]


client = Client(os.getenv("OLLAMA_URL", "http://localhost:11434"))
model = "qwen3.5:4b"


def parse_receipt(img, debug=False, temperature=0.0):
    if debug:
        return {
            "store_name": "サンプルストア",
            "date": "2024-03-26T15:00:00",
            "items": [
                {"name": "商品A", "price": 100},
                {"name": "商品B", "price": 200}
            ],
            "total_amount": 300,
            "file_name": os.path.basename(img)
        }
    response = client.chat(
        model=model,
        messages=[
            {
                "role": "system",
                "content": "あなたはレシートリーダーです。レシートの画像を解析して、店名、ISO8601形式（YYYY-MM-DDTHH:MM:SS）の日付、購入した商品と価格、合計金額をjsonで抽出してください。"
            },
            {
                "role": "user",
                "content": "レシートの画像を解析してください",
                "images": [img]
            }
        ],
        format=Receipt.model_json_schema(),
        options={"temperature": temperature}
    )
    data = Receipt.model_validate_json(response.message.content).model_dump()
    data["file_name"] = os.path.basename(img)
    return data
