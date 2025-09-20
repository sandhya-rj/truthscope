# 🔍 TruthScope  

**TruthScope** is an AI-powered misinformation detection platform. It verifies news headlines, articles, and media content against trusted sources using RSS feeds, APIs, and AI-powered fact-checking models.  

---

## 🚀 Features
- ✅ **Fact-checking** using trusted RSS sources (BBC, Reuters, Al Jazeera, WHO, etc.)
- 🤖 **AI-powered verdicts** (real/fake/unverified) with explanations
- 📰 **News Ticker** showing live trusted headlines
- 🎨 **Cyberpunk-styled frontend** with neon UI
- 🔍 **Fuzzy matching** of headlines to catch misleading variations
- 📷 **DeepFake analysis** using DeepFace + OpenCV (optional extension)
- ⚡ Runs on **Flask** + **Pathway** for stream processing  

---

## ⚙️ Setup Instructions (Windows + WSL Required ⚠️)

> ⚠️ **Important:** Pathway SDK does not support Windows natively.  
> You **must** use **Windows Subsystem for Linux (WSL – Ubuntu)**.  
> All project files should be created **inside Ubuntu**, not in Windows filesystem.

### 1️⃣ Open Ubuntu Terminal (WSL)
Make sure your project folder exists inside Ubuntu. Example:
```bash
cd ~
mkdir truthscope
cd truthscope
2️⃣ Clone the Repository
bash
Copy code
git clone https://github.com/sandhya-rj/truthscope.git
cd truthscope
3️⃣ Create Virtual Environment
Before running anything, create and activate a Python virtual environment:

bash
Copy code
python3 -m venv venv
source venv/bin/activate
⚠️ You must activate venv every time before running app.py.

4️⃣ Install Dependencies
bash
Copy code
pip install -r requirements.txt
5️⃣ Run the App
bash
Copy code
python3 app.py
Now open http://127.0.0.1:5000 in your browser 🎉

📂 Project Structure
lua
Copy code
truthscope/
│-- app.py              # Flask backend
│-- requirements.txt    # Dependencies
│-- static/             # CSS, JS, images
│-- templates/          # HTML templates
│-- .gitignore
│-- README.md
🌍 Deployment Notes
Works only inside Ubuntu (WSL) on Windows.

venv must always be activated before installing dependencies or running the app.

Can be deployed to Render / Railway / Heroku / Vercel if needed.

👩‍💻 Author
Sandhya RJ → GitHub

yaml
Copy code

---

Now just run these to push it:

```bash
cd ~/truthscope
echo "<PASTE THE README ABOVE>" > README.md
git add README.md
git commit -m "Add detailed README with WSL + venv instructions"
git push
