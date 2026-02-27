from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from backend.app.schemas import AskRequest, AskResponse
from backend.app.agent import run_agent

app = FastAPI(title="Titanic Chatbot API")

# Enable CORS (for Streamlit later)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.api_route("/", methods=["GET", "HEAD"])
def root():
    return {"message": "Titanic Chatbot API is running 🚢"}


@app.post("/ask", response_model=AskResponse)
def ask_question(request: AskRequest):
    try:
        question = request.question

        result = run_agent(question)

        return AskResponse(
            answer=result["answer"],
            image=result["image"]
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))