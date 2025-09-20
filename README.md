TruthScope 🕵️‍♂️🔍

AI-powered Fake News Detection System

TruthScope is an end-to-end project that detects fake news using machine learning and deep learning models.
Built with Python, Flask, and NLP techniques, this tool analyzes news content and predicts whether it is real or fake.

⚡ Features

End-to-end Fake News Detection pipeline.

Deep Learning model (model_fake_detection.h5) trained on news datasets.

Flask web app (app.py) for easy user interaction.

Deployed and run inside Ubuntu (WSL) due to Pathway SDK not being supported on Windows.

Virtual environment setup for clean dependency management.

🛠️ Tech Stack

Python 3

Flask (Web Framework)

TensorFlow / Keras (Deep Learning)

scikit-learn, pandas, numpy (ML + Data Handling)

NLTK / NLP Preprocessing

Ubuntu (WSL) for execution

📂 Project Structure
truthscope/
│── app.py               # Flask app entry point  
│── requirements.txt      # Dependencies  
│── model_fake_detection.h5  # Trained ML/DL model  
│── static/               # CSS, JS, images  
│── templates/            # HTML templates  
│── README.md             # Project documentation  
│── .gitignore            # Ignored files (venv, caches, etc.)

⚙️ Installation & Setup

Since Pathway SDK is not supported on Windows, we run everything inside Ubuntu (WSL).
Follow these steps:

# 1. Navigate to project folder
cd ~/truthscope

# 2. Create virtual environment
python3 -m venv venv

# 3. Activate venv
source venv/bin/activate

# 4. Install dependencies
pip install -r requirements.txt

# 5. Run Flask app
python3 app.py

🚀 Usage

Open browser → go to http://127.0.0.1:5000/

Enter a news headline/article → Get prediction (REAL or FAKE)

⚠️ Notes

The trained model file (model_fake_detection.h5) is large (>80MB). Consider using Git LFS for version control.

Always activate virtual environment before running app.py or installing requirements.

Keep project inside Ubuntu WSL (not Windows native) to avoid compatibility issues.
