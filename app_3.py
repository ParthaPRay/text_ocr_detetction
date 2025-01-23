import cv2
import easyocr
import gradio as gr
import pandas as pd
import numpy as np

def process_image(image):
    # Initialize EasyOCR reader
    reader = easyocr.Reader(['en'], gpu=False)  # For English text detection

    # Read the image
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    # Perform text detection
    results = reader.readtext(image, detail=1)

    # Prepare output image
    output_image = image.copy()

    # Data for CSV download
    text_data = []

    for (bbox, text, confidence) in results:
        # Extract bounding box coordinates
        (top_left, top_right, bottom_right, bottom_left) = bbox
        top_left = tuple(map(int, top_left))
        bottom_right = tuple(map(int, bottom_right))

        # Draw rectangle on the image
        cv2.rectangle(output_image, top_left, bottom_right, (0, 255, 0), 2)

        # Put the detected text on the image
        cv2.putText(output_image, text, (top_left[0], top_left[1] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)

        # Add text and confidence to the data list
        text_data.append({"Text": text, "Confidence": f"{confidence:.2f}"})

    # Convert output image back to BGR for Gradio
    output_image = cv2.cvtColor(output_image, cv2.COLOR_RGB2BGR)

    # Create a DataFrame for results
    df = pd.DataFrame(text_data)

    return output_image, df

# Define Gradio app
with gr.Blocks() as app:
    gr.Markdown("## Text Detection with EasyOCR")

    with gr.Row():
        with gr.Column():
            input_image = gr.Image(label="Upload Image", type="numpy")
            submit_button = gr.Button("Submit")
        with gr.Column():
            output_image = gr.Image(label="Annotated Output")
            results_table = gr.Dataframe(headers=["Text", "Confidence"], interactive=False)
            download_button = gr.File(label="Download CSV")

    def process_and_return(image):
        annotated_image, result_df = process_image(image)
        csv_file = "results.csv"
        result_df.to_csv(csv_file, index=False)
        return annotated_image, result_df, csv_file

    submit_button.click(
        process_and_return,
        inputs=[input_image],
        outputs=[output_image, results_table, download_button]
    )

app.launch()

