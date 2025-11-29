# Script-to-Image Automation (Vertex AI)

This app segments your timestamped script, generates image prompts with Gemini, and creates matching images with Vertex AI's image model. It is designed for non-Python users and works locally with a single command once configured.

If you have **zero coding experience**, follow the step-by-step “Quick start (no coding knowledge)” below. Everything happens in a terminal/command prompt, but you will copy/paste the exact commands provided here.

## What you need
- Python 3.10+ installed on your computer. If you do not have it, download it from https://www.python.org/downloads/ (Windows users: check “Add Python to PATH” during installation).
- A Google Cloud project with the **Vertex AI User** role granted to your service account
- A downloaded service-account JSON key file (this is the file you will point the app to)

## Quick start (no coding knowledge)

### A. Download the project
1. If you have Git installed, open a terminal/command prompt and run:
   ```bash
   git clone <your-repo-url>
   ```
   If you do **not** use Git, click **“Code” → “Download ZIP”** on the GitHub page, unzip it, and open the unzipped `adsteraaa` folder in your file explorer.

### B. Put your Vertex key somewhere safe
1. Pick a location and remember the full path. Examples:
   - Windows: `C:\Users\YOURNAME\vertex\vertex-sa.json`
   - Mac/Linux: `/Users/yourname/vertex/vertex-sa.json`
2. Do **not** store the key inside the project folder to avoid accidental sharing.

### C. Open a terminal in the project folder
1. Windows: open **Command Prompt** → `cd` into the folder, e.g.:
   ```cmd
   cd C:\Users\YOURNAME\Downloads\adsteraaa
   ```
2. Mac/Linux: open **Terminal** → `cd` into the folder, e.g.:
   ```bash
   cd ~/Downloads/adsteraaa
   ```

### D. Create a Python environment and install everything
Copy/paste these commands exactly (one block at a time):

**Windows (Command Prompt):**
```cmd
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

**Mac/Linux (Terminal):**
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### E. Tell the app where your key is (choose one)
**Option 1: Environment variable (recommended)**
- Windows Command Prompt:
  ```cmd
  set GOOGLE_APPLICATION_CREDENTIALS=C:\Users\YOURNAME\vertex\vertex-sa.json
  ```
- Mac/Linux Terminal:
  ```bash
  export GOOGLE_APPLICATION_CREDENTIALS="/Users/yourname/vertex/vertex-sa.json"
  ```

**Option 2: .env file (also easy)**
1. Make a copy of the example file:
   ```bash
   cp .env.example .env
   ```
2. Open `.env` in any text editor and fill in three values:
   ```
   PROJECT_ID=your-gcp-project-id
   LOCATION=us-central1  # or your Vertex region
   GOOGLE_APPLICATION_CREDENTIALS=/full/path/to/vertex-sa.json
   ```
3. Load the file into your terminal session (after activating the virtual environment):
   ```bash
   set -a && source .env && set +a
   ```
   On Windows, use a tool like Git Bash or manually run `set` commands instead.

### F. Run the app
1. Make sure the virtual environment is still active (your prompt usually shows `(.venv)` at the start).
2. Start Streamlit:
   ```bash
   streamlit run app.py
   ```
3. A browser tab will open at `http://localhost:8501`. If it does not, copy the URL from the terminal and paste it into your browser.

### G. Use the UI step by step
1. In the left sidebar:
   - **Project ID**: enter your Google Cloud project ID (or leave the prefilled value if you set it in `.env`).
   - **Region**: enter your Vertex region (e.g., `us-central1`).
   - **Service account JSON path**: paste the full path to the key (if you did not set the environment variable).
   - **Global visual style**: type any style you want applied to every image (e.g., “painterly watercolor, soft light”).
   - **Image size**: pick one of the presets (1:1, 4:3, 3:4, 16:9, or 9:16).
2. In the main area:
   - Paste or upload your timestamped lines JSON. Example structure:
     ```json
     [
       {"start": 0.0, "end": 4.2, "text": "Intro line"},
       {"start": 4.2, "end": 9.7, "text": "Next line"}
     ]
     ```
   - Set **Segment length (seconds)** (default 30).
   - Click **Build segments and generate prompts** → the app creates one image prompt per 30-second segment.
   - Review the generated prompts.
   - Click **Generate images with Vertex** → the app generates one image per prompt.

### H. Where things live
- Your key file stays wherever you placed it (outside the project folder).
- Prompts and images are generated in memory during a session. You can copy prompts directly from the page. If you want to save images automatically, extend the code later or right-click and save them from the browser.

## Troubleshooting (most common issues)
- **Auth errors**: the path is wrong or the service account lacks **Vertex AI User**. Recheck the path you typed and confirm the role in Google Cloud Console.
- **Python not found**: reinstall Python 3.10+ and ensure “Add Python to PATH” is checked (Windows) or restart your terminal after installing (Mac/Linux).
- **Package install errors**: confirm you activated the virtual environment before running `pip install -r requirements.txt`.
- **Browser did not open**: copy the `http://localhost:8501` link printed in the terminal and paste it into your browser.

## Optional: run tests (for curiosity)
You do not need this to use the app, but you can verify things locally:
```bash
pytest
```

## Deployment notes (later, if you host it)
- Any host that can run Streamlit works. On managed hosts, set environment variables `GOOGLE_APPLICATION_CREDENTIALS`, `PROJECT_ID`, and `LOCATION` to match your setup.
- Never commit your JSON key. Keep it outside the repo or list it in `.gitignore` (already included).
