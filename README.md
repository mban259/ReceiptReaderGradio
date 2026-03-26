# ReceiptReaderGradio

A Gradio-based web UI that extracts structured data from receipt images using a local Ollama model.

## Features

- Upload multiple receipt images
- Extract store name, date, items, and total amount via Ollama
- Edit extracted JSON directly in the UI
- Retry extraction with higher temperature for better results
- Download a summary JSON with all receipts and grand total

## Requirements

- Python 3.14
- [Ollama](https://ollama.com) running locally or on a remote host
- Model: `qwen3.5:4b` (vision-capable)

## Setup

```bash
pip install -r requirements.txt
cp .env.example .env
```

Edit `.env` to point to your Ollama instance:

```
OLLAMA_URL=http://localhost:11434
```

## Usage

```bash
python app.py
```

Open the URL shown in the terminal (default: `http://localhost:7860`).

## File Structure

| File                  | Description                                   |
| --------------------- | --------------------------------------------- |
| `app.py`            | Gradio UI                                     |
| `receipt_reader.py` | Ollama client, returns parsed receipt as dict |

## Output JSON Format

```json
{
  "receipts": [
    {
      "store_name": "...",
      "date": "2024-01-01T00:00:00",
      "items": [{"name": "...", "price": 100}],
      "total_amount": 300,
      "file_name": "receipt.jpg"
    }
  ],
  "grand_total": 300
}
```
