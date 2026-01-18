import numpy as np
import tensorflow as tf
import kagglehub
import os
import pickle
from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.preprocessing.sequence import pad_sequences
from tensorflow.keras.models import Sequential, load_model
from tensorflow.keras.layers import Embedding, LSTM, Dense
from tensorflow.keras.callbacks import EarlyStopping, ModelCheckpoint

# --- CONFIGURATION ---
MODEL_FILENAME = "next_word_lstm.keras"
TOKENIZER_FILENAME = "tokenizer.pkl"
BATCH_SIZE = 64
BUFFER_SIZE = 1000

# --- 1. DATASET DOWNLOAD ---
print("--- 1. Downloading/Checking Dataset ---")
try:
    path = kagglehub.dataset_download("ashishpandey2062/next-word-predictor-text-generator-dataset")
    print("Dataset Path:", path)
except Exception as e:
    print(f"Error downloading dataset: {e}")
    exit()

txt_file_path = next((os.path.join(path, f) for f in os.listdir(path) if f.endswith(".txt")), None)
if not txt_file_path:
    raise FileNotFoundError("No .txt file found!")

# --- 2. PREPROCESSING ---
print("--- 2. Processing Data ---")

with open(txt_file_path, 'r', encoding='utf-8') as f:
    text_data = f.read().lower()

# Load Tokenizer if exists, else fit new one
if os.path.exists(TOKENIZER_FILENAME):
    print("Loading saved tokenizer...")
    with open(TOKENIZER_FILENAME, 'rb') as handle:
        tokenizer = pickle.load(handle)
else:
    print("Fitting new tokenizer...")
    tokenizer = Tokenizer()
    tokenizer.fit_on_texts([text_data])
    # Save tokenizer for future use
    with open(TOKENIZER_FILENAME, 'wb') as handle:
        pickle.dump(tokenizer, handle, protocol=pickle.HIGHEST_PROTOCOL)

total_words = len(tokenizer.word_index) + 1
print(f"Vocab size: {total_words}")

# Create Input Sequences (N-Grams)
input_sequences = []
for line in text_data.split('\n'):
    token_list = tokenizer.texts_to_sequences([line])[0]
    for i in range(1, len(token_list)):
        n_gram_sequence = token_list[:i+1]
        input_sequences.append(n_gram_sequence)

# Pad Sequences
max_sequence_len = max([len(x) for x in input_sequences])
input_sequences = np.array(pad_sequences(input_sequences, maxlen=max_sequence_len, padding='pre'))

# Split X and y (Sparse)
X = input_sequences[:, :-1]
y = input_sequences[:, -1]
print(f"Training sequences: {len(X)}")

# --- 3. TF.DATA PIPELINE ---
dataset = tf.data.Dataset.from_tensor_slices((X, y))
dataset = (dataset
           .shuffle(BUFFER_SIZE)
           .batch(BATCH_SIZE)
           .cache()
           .prefetch(tf.data.AUTOTUNE))

# --- 4. BUILD OR LOAD MODEL ---
if os.path.exists(MODEL_FILENAME):
    print(f"--- 4. Loading Saved Model ({MODEL_FILENAME}) ---")
    model = load_model(MODEL_FILENAME)
else:
    print("--- 4. Building New LSTM Model ---")
    model = Sequential([
        Embedding(total_words, 100, input_length=max_sequence_len-1),
        LSTM(150),
        Dense(total_words, activation='softmax')
    ])
    model.compile(loss='sparse_categorical_crossentropy', optimizer='adam', metrics=['accuracy'])
    
    # Checkpoint to save best model during training
    checkpoint = ModelCheckpoint(MODEL_FILENAME, save_best_only=True, monitor='loss')
    early_stop = EarlyStopping(monitor='loss', patience=3)

    print("--- 5. Training Model ---")
    model.fit(dataset, epochs=100, verbose=1, callbacks=[checkpoint, early_stop])

# --- 6. PREDICTION FUNCTIONS (With Temperature) ---

def sample(preds, temperature=1.0):
    """
    Helper function to sample an index from a probability array.
    """
    preds = np.asarray(preds).astype('float64')
    # Prevent division by zero or log(0)
    preds = np.log(preds + 1e-7) / temperature
    exp_preds = np.exp(preds)
    preds = exp_preds / np.sum(exp_preds)
    probas = np.random.multinomial(1, preds, 1)
    return np.argmax(probas)

def generate_text(seed_text, next_words, temperature=1.0):
    output_text = seed_text
    for _ in range(next_words):
        token_list = tokenizer.texts_to_sequences([seed_text])[0]
        token_list = pad_sequences([token_list], maxlen=max_sequence_len-1, padding='pre')
        
        predicted_probs = model.predict(token_list, verbose=0)[0]
        
        # Use temperature sampling
        predicted_index = sample(predicted_probs, temperature)
        
        output_word = ""
        for word, index in tokenizer.word_index.items():
            if index == predicted_index:
                output_word = word
                break
        
        if not output_word: continue # Skip if unknown
            
        seed_text += " " + output_word
        output_text += " " + output_word
    return output_text

# --- 7. INTERACTIVE LOOP ---
print("\n--- READY TO PREDICT ---")
print("Modes: Low Temp = Safe/Repetitive | High Temp = Creative/Chaotic")

while True:
    user_input = input("\nEnter start word (or 'q' to quit): ")
    if user_input.lower() == 'q': break
    
    try:
        # Generate 3 variations
        print(f"\nSafe (0.2):     {generate_text(user_input, 5, temperature=0.2)}")
        print(f"Balanced (0.7): {generate_text(user_input, 5, temperature=0.7)}")
        print(f"Wild (1.2):     {generate_text(user_input, 5, temperature=1.2)}")
        print("-" * 40)
    except Exception as e:
        print(f"Error: {e}. Try a word that exists in the dataset.")