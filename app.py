import gradio as gr
import json
import receipt_reader
import os
import tempfile
from datetime import datetime
import pandas as pd

def select_item(index, files, state):
    if index is None:
        return None, ""
    # image,
    # store name
    # date
    # items_df,
    # total
    st = state[index]
    store_name = st["store_name"]
    date = datetime.fromisoformat(st["date"])
    items_df = [{"name": item["name"], "price": item["price"]}
                for item in st["items"]]
    total = st["total_amount"]
    return files[index].name, store_name, date, pd.DataFrame(items_df), total


def process_images(files, progress=gr.Progress()):
    if files is None:
        return [], gr.Dropdown(choices=[], value=None)
    results = []
    file_names = []

    completed = 0
    total = len(files)

    for file in files:
        results.append(receipt_reader.parse_receipt(
            file.name, temperature=0.0, debug=True))
        completed += 1
        name = os.path.basename(file.name)
        file_names.append(name)
        progress(completed / total, f"{name}")
    return results, gr.Dropdown(choices=file_names, value=file_names[0])


def retry(index, files):
    if index is None or files is None:
        return ""
    result = receipt_reader.parse_receipt(
        files[index].name, temperature=0.7)
    print(index)
    # state[index] = result
    store_name = result["store_name"]
    date = datetime.fromisoformat(result["date"])
    items_df = [{"name": item["name"], "price": item["price"]}
                for item in result["items"]]
    total = result["total_amount"]
    return store_name, date, pd.DataFrame(items_df), total


def update(index, state, store_name, date, items_df, total):
    js = {
        "store_name": store_name,
        "date": date.isoformat(),
        "items": items_df.to_dict(orient="records"),
        "total_amount": total
    }
    state[index] = js
    return state


def download(state):
    grand_total = sum(item["total_amount"]
                      for item in state if item.get("total_amount"))
    output = {
        "receipts": state,
        "grand_total": grand_total
    }
    tmp_dir = tempfile.gettempdir()
    filename = f"output_{datetime.now().strftime("%Y%m%d")}.json"
    path = os.path.join(tmp_dir, filename)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
    return path


with gr.Blocks() as app:
    gr.Markdown("# ReceiptReader")
    input_files = gr.File(
        file_types=["image"],
        file_count="multiple",
        label="Upload Images"
    )

    submit_button = gr.Button("Analyze")

    state = gr.State([])
    tmp_json = gr.State()

    selector = gr.Dropdown(
        label="Results",
        type="index"
    )

    with gr.Row():
        preview_image = gr.Image(label="Preview")
        with gr.Column():
            store_name = gr.Textbox(lines=1, interactive=True, label="Store Name")
            date = gr.DateTime(interactive=True, label="Date", type="datetime")
            items_df = gr.Dataframe(interactive=True, label="items")
            total = gr.Number(interactive=True, label="Total Amount")
            retry_button = gr.Button("Retry")
            update_button = gr.Button("Update")

    download_button = gr.DownloadButton(
        value=download, inputs=state
    )

    submit_button.click(
        fn=process_images,
        inputs=input_files,
        outputs=[state, selector]
    )

    selector.change(
        fn=select_item,
        inputs=[selector, input_files, state],
        outputs=[preview_image, store_name, date, items_df, total]
    )

    retry_button.click(
        fn=retry,
        inputs=[selector, input_files],
        outputs=[store_name, date, items_df, total]
    )

    update_button.click(
        fn=update,
        inputs=[selector, state, store_name, date, items_df, total],
        outputs=state
    )


app.launch()
