import openai
import json
import os
import requests
from PIL import Image
from io import BytesIO

def explain(subject, context=None):
    """
    Generates an explanation of a given subject in Python terms and saves it to an HTML file.
    
    Parameters:
    subject (str): The subject to explain.
    context (str, optional): The context in which to explain the subject.
    
    Returns: HTML-file and JPG as an explanation
    """

    # Function to load API key from JSON file 
    def load_api_key(file_path): 
        with open(file_path, 'r') as file: 
            data = json.load(file) 
            return data['openai_api_key']

    # Set up OpenAI API
    openAIpath = input("Provide please your OpenAI API key - file name: ")
    api_key = load_api_key(openAIpath)
    openai.api_key = api_key
    
#    if not openai.api_key:
#        raise ValueError("API key not found. Please set the environment variable OPENAI_API_KEY.")

    # Generate the prompt for text explanation
    text_prompt = f"Explain, please, {subject} in Python terms (using functions, classes, loops, variables, etc.), clarifying the purpose, how it works, and its dependence with other parts of the whole system."
    if context:
        text_prompt += f" in the context of {context}"
    
    try:
        # Request explanation from ChatGPT
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": text_prompt}
            ],
            max_tokens=500
        )
        explanation = response.choices[0].message['content'].strip()
    except Exception as e:
        print(f"An error occurred: {e}")
        return
    
    # Generate the prompt for DALL-E
    image_prompt = f"An illustration explaining the concept of {subject} as a scheme showing connections of {subject}'s parts and processes and its ties with outer systems."
    
    try:
        # Request illustration from DALL-E
        image_response = openai.Image.create(
            prompt=image_prompt,
            n=1,
            size="1024x1024"
        )
        image_url = image_response['data'][0]['url']
        # Download the image
        img_response = requests.get(image_url)
        img = Image.open(BytesIO(img_response.content))
        img_path = f"{subject}_illustration.jpg"
        img.save(img_path)
    except Exception as e:
        print(f"An error occurred while fetching the image: {e}")
        return

    # Create folder for the subject
    folder_name = subject.replace(" ", "_")
    if not os.path.exists(folder_name):
        os.makedirs(folder_name)

    # Move the image to the subject folder
    os.rename(img_path, os.path.join(folder_name, img_path))

    # Write explanation to HTML
    html_content = f"""
    <html>
        <body>
            <h1>{subject}</h1>
            <p>{explanation}</p>
            <img src="{subject}_illustration.jpg" alt="Illustration">
            <pre><code>{explanation}</code></pre>
        </body>
    </html>
    """

    with open(f"{folder_name}/explanation.html", "w") as f:
        f.write(html_content)
        
    # Save code in a .py file (this can be your Python explanation code)
    with open(f"{folder_name}/code.py", "w") as f:
        f.write("# Python code for explanation\n")
        f.write(f"# Example code for {subject}\n")

    print(f"Explanation and files saved in {folder_name}.")

# Example usage
# explain("beer", context="esoteric")

def main():
    while True:
        idea = input("What do you want to understand? ")
        if len(idea) > 1:
            break
        else:
            print(f"Not so short, please.")

    ctext = input("Wonna set a context?: ")
    if len(ctext) < 1 or ctext in ["n", "N", "no", "NO", "No"]:
        explain(idea)
    else:
        explain(idea, context=ctext)

main()
