from fastapi import FastAPI, UploadFile, HTTPException
import os
from pydantic import BaseModel
from dotenv import load_dotenv
import openai
import shutil
import io

app = FastAPI()

load_dotenv()  # Load environment variables
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
openai.api_key = OPENAI_API_KEY

class Question(BaseModel):
    question: str

@app.get("/")
def root():
    return "Hello RAG fellow!"

@app.post("/uploadfile/")
async def upload_file(file: UploadFile):
    # Define allowed file extensions
    allowed_extensions = ["txt", "pdf"]

    # Check if the file extension is allowed
    file_extension = file.filename.split('.')[-1]
    if file_extension not in allowed_extensions:
        raise HTTPException(status_code=400, detail="File type not allowed")

    folder = "sources"
    try:
        # Ensure the directory exists
        os.makedirs(folder, exist_ok=True)

        # Secure way to save the file
        file_location = os.path.join(folder, file.filename)
        file_content = await file.read()  # Read file content as bytes
        with open(file_location, "wb+") as file_object:
            # Convert bytes content to a file-like object
            file_like_object = io.BytesIO(file_content)
            # Use shutil.copyfileobj for secure file writing
            shutil.copyfileobj(file_like_object, file_object)

        return {"info": "File saved", "filename": file.filename}

    except Exception as e:
        # Log the exception (add actual logging in production code)
        print(f"Error saving file: {e}")
        raise HTTPException(status_code=500, detail="Error saving file")

@app.post("/ask/")
async def ask_question(question: Question):
    if OPENAI_API_KEY is None:
        raise HTTPException(status_code=500, detail="OpenAI API key is not set")
    try:
        response = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": question.question},
            ]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
    return {"response": response.choices[0].message.content}
