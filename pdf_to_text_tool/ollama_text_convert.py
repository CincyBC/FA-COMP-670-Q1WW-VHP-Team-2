import os
import ollama
from pdf2image import convert_from_path
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)

def validate_return_files(files: list, base_dir: os.path) -> list:
    """
    This function takes in a list of files and returns only the files in the list
    Parameters:
        files (list): list of files
        base_dir (os.path): the base directory

    Returns: 
        list: a list of files
    """
    return [
        entry
        for entry in files
        if os.path.isfile(os.path.join(base_dir, entry))
    ]

def validate_directories(base_dir: str) -> tuple:
    """
    This function takes in a base directory and creates tmp and output directories if necessary
    Parameters:
        base_dir (str): the base directory
    
    Returns:
        tuple: a tuple of the input, tmp, and output directories
    """
    inputs_path = os.path.join(base_dir, "inputs")
    try:
        os.mkdir(os.path.join(base_dir, "tmp"))
    except FileExistsError:
        pass
    tmp_path = os.path.join(base_dir, "tmp")
    try:
        os.mkdir(os.path.join(base_dir, "outputs"))
    except FileExistsError:
        pass
    outputs_path = os.path.join(base_dir, "outputs")
    return inputs_path, tmp_path, outputs_path

def convert_pdf_to_image(input_path: str, tmp_path: str, file_name: str) -> str:
    """
    This function takes in a PDF file and converts it to one image per page
    Parameters:
        input_path (str): the input path where the file lives
        tmp_path (str): the temporary path where the images will be stored
        file_name (str): the file name
    
    Returns:
        str: the base file name of the PDF which is the root of the images
    """
    base_file = file_name.split(".")
    if base_file[1].lower() != "pdf":
        logging.info(f"Skipping {file_name}. It is not a pdf file")
    else:
        images = convert_from_path(os.path.join(inputs_path, file_name))
        os.chdir(tmp_path)
        for i in range(len(images)):
            images[i].save(base_file[0] + str(i) + ".jpg", "JPEG")
        logging.info(f"Created the following images: {os.listdir(tmp_path)}")
        os.chdir("../")
        return base_file[0]
    return None


def ollama_convert_to_text(file_root: str, tmp_path: str, output_path: str, model: str='llama3.2-vision') -> None:
    """
    This function takes in an Ollama model, file root name, temp file path, and output path 
    and converts the images to text

    Parameters:
        model (str): the Ollama model to use with the default as llama3.2-vision
        file_root (str): the file root of the images
        tmp_path (str): the temporary path where the images are stored
        output_path (str): the output path where the text file will be stored
    """
    files = validate_return_files(os.listdir(tmp_path), tmp_path)
    files.sort()
    
    os.chdir(tmp_path)

    text_file = os.path.join(output_path, file_root + ".txt")
    prompt = "You are a transcription service copying what is in an image and converting it to plain text. You will output only the text and charts in the image. If you see a chart, please use the markdown method for the text."
    for index, file in enumerate(files):
        logging.info(f"Processing {file}")
        response = ollama.chat(
            model=model,
            messages=[{"role": "user", "content": prompt, "images": [file]}],
        )
        if index == 0:
            with open(text_file, "w") as output_file:
                output_file.write(response.message.content)
                logging.info(f"Created the following text file: {file_root}.txt")
        else:
            with open(text_file, "a") as output_file:
                output_file.write(response.message.content)
                logging.info(f"Appended {file}")

        os.remove(os.path.join(tmp_path, file))
    os.chdir("../")


if __name__ == "__main__":
    # create all the necessary directory paths    
    inputs_path, tmp_path, outputs_path = validate_directories(os.path.abspath(os.getcwd()))

    # get all files in the inputs directory
    all_entries = validate_return_files(os.listdir(inputs_path), inputs_path)

    # process all the files in the inputs directory
    for file in all_entries:
        # First convert the pdf to images since the model requires images
        file_root = convert_pdf_to_image(inputs_path, tmp_path, file)
        # Then convert the images to markdown text
        if file_root:
            ollama_convert_to_text(file_root=file_root, tmp_path=tmp_path, output_path=outputs_path, model='llama3.2-vision')
