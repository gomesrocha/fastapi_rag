from fastapi import FastAPI, UploadFile, HTTPException
import os
from pydantic import BaseModel
from dotenv import load_dotenv
import openai

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
    folder = "sources"
    os.makedirs(folder, exist_ok=True)  # Create the folder if it doesn't exist

    file_location = os.path.join(folder, file.filename)
    with open(file_location, "wb+") as file_object:
        file_object.write(await file.read())  # Write the file to the directory

    return {"info": "File saved", "filename": file.filename}

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
