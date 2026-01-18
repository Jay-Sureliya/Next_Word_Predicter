import numpy as np
import pickle
import os
from fastapi import FastAPI
from pydantic import BaseModel
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.sequence import pad_sequences
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Ghost Text API")

# --- CRITICAL: ALLOW BROWSER ACCESS (CORS) ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# --- PATH CONFIGURATION ---
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(CURRENT_DIR)
MODEL_PATH = os.path.join(ROOT_DIR, "model", "next_word_lstm.keras")
TOKENIZER_PATH = os.path.join(ROOT_DIR, "model", "tokenizer.pkl")

model = None
tokenizer = None
max_sequence_len = 0

@app.on_event("startup")
def load_resources():
    global model, tokenizer, max_sequence_len
    try:
        model = load_model(MODEL_PATH)
        with open(TOKENIZER_PATH, 'rb') as handle:
            tokenizer = pickle.load(handle)
        max_sequence_len = model.input_shape[1] + 1
        print("✅ Resources loaded!")
    except Exception as e:
        print(f"❌ Error: {e}")

class AutocompleteRequest(BaseModel):
    text: str

@app.post("/autocomplete")
def autocomplete(req: AutocompleteRequest):
    if not model or not req.text.strip(): return {"suggestion": ""}
    
    try:
        # Predict the single best next word
        token_list = tokenizer.texts_to_sequences([req.text])[0]
        token_list = pad_sequences([token_list], maxlen=max_sequence_len-1, padding='pre')
        
        probs = model.predict(token_list, verbose=0)[0]
        idx = np.argmax(probs)
        
        suggestion = tokenizer.index_word.get(idx, "")
        return {"suggestion": suggestion}
    except:
        return {"suggestion": ""}