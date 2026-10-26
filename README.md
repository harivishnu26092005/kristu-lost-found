# JAYAN FIND — Kristu Jayanti University

Python + Streamlit + SQLite prototype for a college Lost & Found portal. Includes the supplied emblem, Apple-inspired styling, reporting, search/filtering, four campus blocks, local match suggestions, claims, moderation demo, and live dashboard.

## Run on Windows
1. Install Python 3.10+ from https://www.python.org/downloads/ (3.11+ recommended).
2. Extract this ZIP and open the `JayanFind` folder in VS Code.
3. Open Terminal → New Terminal and run one line at a time:

```powershell
py -m venv .venv
.venv\Scripts\activate
py -m pip install -r requirements.txt
py -m streamlit run app.py
```

Open the local URL printed in the terminal, usually http://localhost:8501. If `py` is not recognised, install Python and enable “Add Python to PATH”.

## College emblem
The supplied image is included at `assets/college_logo.png`.

## Testing
Install pytest with `py -m pip install pytest`, then run `py -m pytest -q`.

## Important limitations
- SQLite and uploaded images are stored locally on the computer running the app; it is not shared across devices.
- The Admin Demo page has no real authentication. Do not deploy publicly as-is.
- Use fictional sample data during presentation. Never publish real student ID numbers, phone numbers, passwords, or sensitive claim details.
- Production use requires university login, access controls, secure claim review, moderation, backups, rate limiting, and shared hosted storage.

## Five-minute demo
1. Introduce the problem and Jayan Find (30 sec).
2. Show live counters and four blocks (45 sec).
3. Search/filter a sample item (60 sec).
4. Submit a fictional report (60 sec).
5. Show possible matches (45 sec).
6. Demonstrate claim/recovery workflow (45 sec).
7. Close with privacy-first design and next steps (15 sec).

## Judge questions
**How does matching work?** A local Python function compares item names, descriptions, categories and campus locations. It does not use a paid AI API.

**Is this production ready?** It is a working prototype. Real deployment requires verified university accounts, secure admin permissions, moderation and a shared database.

**What happens to reports?** They persist in the local SQLite database on the machine running the app.
