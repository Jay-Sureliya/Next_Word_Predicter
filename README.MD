# 👻 Ghost Text: AI-Powered Next Word Predictor

![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)
![TensorFlow](https://img.shields.io/badge/TensorFlow-2.x-orange.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.95+-green.svg)
![Streamlit](https://img.shields.io/badge/Streamlit-1.22+-red.svg)

Ghost Text is a deep learning application that provides real-time, inline text completion suggestions, similar to "Smart Compose" or code autocomplete features. It features a decoupled architecture with a high-performance FastAPI backend and a custom Streamlit frontend.

## 🌟 Features

* **Real-time Autocomplete:** Suggestions appear instantly as "ghost text" overlaying your input.
* **LSTM Neural Network:** Trained on a large corpus to understand context and syntax.
* **Decoupled Architecture:**
    * **Backend:** FastAPI for high-speed model inference.
    * **Frontend:** Streamlit with custom HTML/JS components for the editor UI.
* **Smart Interactions:** Press `Tab` to accept suggestions seamlessly.

## 📂 Project Structure

```text
Next_Word_Predicter/
├── app/
│   ├── api.py           # FastAPI backend server
│   └── frontend.py      # Streamlit frontend with custom JS editor
├── model/
│   ├── next_word_lstm.keras  # Trained Model file
│   └── tokenizer.pkl         # Tokenizer object
├── src/
│   └── train_model.py   # Script to train the LSTM model
└── README.md            # Project documentation



🚀 Getting Started
Prerequisites
Ensure you have Python installed. It is recommended to use a virtual environment.

Bash

pip install tensorflow numpy pandas scikit-learn fastapi uvicorn streamlit kagglehub
1. Train the Model
If you haven't trained the model yet, run the training script. This will download the dataset, train the LSTM, and save the artifacts to the model/ directory.

Bash

python src/train_model.py
2. Start the Backend API
Open a terminal and run the FastAPI server. This loads the model into memory and listens for requests.

Bash

uvicorn app.api:app --reload
The API will start at http://127.0.0.1:8000

3. Start the Frontend UI
Open a new terminal window and launch the Streamlit app.

Bash

streamlit run app/frontend.py
The application will open in your default web browser.

🧠 How It Works
Input: As you type in the browser, a JavaScript event listener captures your text.

Request: The JS sends an asynchronous POST request to the backend /autocomplete endpoint.

Inference: The FastAPI server tokenizes your input and feeds it into the LSTM model to predict the most probable next word.

Response: The predicted word is sent back to the frontend.

Display: The frontend renders the suggestion as a gray "ghost" overlay behind your cursor.

🛠️ Tech Stack
Deep Learning: TensorFlow / Keras (LSTM, Embedding Layers)

API Framework: FastAPI, Uvicorn

Frontend: Streamlit, HTML5, CSS3, JavaScript (Fetch API)

Data Processing: NumPy, Pickle

📝 License
This project is open-source and available for educational purposes.