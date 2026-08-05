## Setup & Run

Use a Python 3 virtual environment (recommended):

```bash
cd LibrarySystem

# 1. Create and activate a virtual environment
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run (installs NLTK data, seeds the DB, starts the server)
python run.py
This prints progress, then starts the server:
Starting server at http://127.0.0.1:5000
Open http://127.0.0.1:5000 in your browser.
Alternative: run parts separately
pip install -r requirements.txt          # deps only
python seed.py                           # seed the database only
python app.py                            # run the server only
run.py flags
- --no-install – skip dependency install.
- --no-seed – skip database seeding.
python run.py --no-install --no-seed     # just launch
Configuration
- DAYS_PER_LOAN = 14 — loan period (days) in models.py.
- FINE_PER_DAY = 5.0 — overdue fine per day in models.py.
- SECRET_KEY — Flask session key in app.py.
Reset / Reseed
To start fresh, stop the server, delete the database, then relaunch:
rm lms.db
python run.py --no-install
Notes
- The first run auto-downloads the required NLTK corpora (punkt,
stopwords, vader_lexicon).
- All NLTK logic is kept in nlp.py; app.py only wires routes to it.
