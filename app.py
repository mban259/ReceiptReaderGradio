import gradio as gr
import json
import receipt_reader
import os
import tempfile
from datetime import datetime


def select_item(index, files, state):
    if index is None:
        return None, ""
    return files[index].name, json.dumps(state[index], indent=2, ensure_ascii=False)


def process_images(files, progress=gr.Progress()):
    if files is None:
        return [], gr.Dropdown(choices=[], value=None)
    results = []
    file_names = []

    completed = 0
    total = len(files)

    for file in files:
        results.append(receipt_reader.parse_receipt(
            file.name, temperature=0.0))
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
    return json.dumps(result, indent=2, ensure_ascii=False)


def update(index, json_editor, state):
    try:
        state[index] = json.loads(json_editor)
        gr.Info("Updated successfully")
        return state
    except json.JSONDecodeError:
        raise gr.Error("Invalid JSON format")


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

    selector = gr.Dropdown(
        label="Results",
        type="index"
    )

    with gr.Row():
        preview_image = gr.Image(label="Preview")
        with gr.Column():
            json_editor = gr.Code(
                label="Result", language="json", interactive=True)
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
        outputs=[preview_image, json_editor]
    )

    retry_button.click(
        fn=retry,
        inputs=[selector, input_files],
        outputs=json_editor
    )

    update_button.click(
        fn=update,
        inputs=[selector, json_editor, state],
        outputs=state
    )


app.launch()
