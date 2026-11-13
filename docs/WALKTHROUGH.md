# Legacy AI: A Beginner's Walkthrough

This guide explains what every piece of the code does, in plain English, and how to run it in VS Code. Read it top to bottom once. After that, use it as a reference.

---

## Part 1: The big picture

Think of Legacy AI like a **restaurant**:

| Restaurant | Legacy AI | File |
|---|---|---|
| Front door and host | **API**: takes requests and sends each one to the right place | `main.py` |
| Order form | **Schemas**: make sure every request is filled out correctly | `schemas.py` |
| Security guard | **Guardrails**: stop unsafe requests before they reach the kitchen | `guardrails.py` |
| Recipe book | **Knowledge base**: the trusted facts we're allowed to use | `knowledge/sources.json` |
| Person who finds the right recipe | **Retriever**: searches the recipe book | `retriever.py` |
| Chef | **AI model**: turns the recipe into a friendly answer | `llm.py` |
| Calculator at the register | **Calculators**: exact math, never guessed | `calculators.py` |
| Manager who must sign off | **Actions**: nothing happens until the user approves | `actions.py` |
| Head waiter coordinating it all | **Coach**: runs the steps in order for each question | `coach.py` |
| Food inspector | **Tests**: prove everything works | `backend/tests/` |

Your research questions map straight onto the code:
- **Sub-question 1** (Is grounded AI more accurate?) → `llm.grounded_answer()` vs `llm.baseline_answer()`
- **Sub-question 2** (Does literacy improve?) → the pilot study, using the whole app
- **Sub-question 3** (Do approve-first actions build trust?) → the `history` log in `actions.py`

---

## Part 2: Set up VS Code (one time)

1. **Install the tools.**
   - [Python 3.11 or newer](https://www.python.org/downloads/). On Windows, check **"Add Python to PATH"** during install.
   - [Git](https://git-scm.com/downloads).
   - [VS Code](https://code.visualstudio.com/).

2. **Get the code onto your computer.**
   In VS Code: press `Ctrl+Shift+P` (Mac: `Cmd+Shift+P`), type **Git: Clone**, paste `https://github.com/javariusyoumans/thesis`, and pick a folder. Click **Open** when it asks.

3. **Install the recommended extensions.**
   VS Code will pop up: *"This workspace has extension recommendations."* Click **Install All**. You get Python, Pylance (smart autocomplete), the Debugger, and REST Client (for testing the API).

4. **Create a virtual environment.**
   A virtual environment (`.venv`) is a private box of Python packages just for this project, so it doesn't mess with anything else on your computer.
   `Ctrl+Shift+P` → **Python: Create Environment** → **Venv** → pick your Python → check `requirements.txt` when asked. VS Code creates `.venv` and installs everything.

   *(Terminal alternative: open the terminal with `` Ctrl+` `` and run:)*
   ```bash
   python -m venv .venv
   .venv\Scripts\activate          # Windows
   source .venv/bin/activate       # Mac
   pip install -r requirements.txt
   ```
   When it's active, your terminal prompt starts with `(.venv)`.

---

## Part 3: Run it

### Run the tests first
Click the **beaker icon** (Testing) in the left sidebar → click ▶ **Run All Tests**. You should see 19 green checkmarks.
*(Or in the terminal: `pytest`.)*

**Why tests first?** Tests are small programs that check your real program. If you change something and a test turns red, you broke something, and you find out right away instead of during your defense.

### Start the server
Click the **Run and Debug** icon (play button with a bug) → choose **Run Legacy AI API** → press the green ▶.
The terminal will say `Uvicorn running on http://127.0.0.1:8000`.

### Play with it
- **Option A:** open http://127.0.0.1:8000/docs in your browser. This page is generated automatically. Click any endpoint → **Try it out** → **Execute**.
- **Option B:** open `docs/try-it.http` in VS Code and click **Send Request** above any block.

Try asking: *"What is a Roth IRA?"*, then *"Which stock should I buy?"* (watch the guardrail block it), then run the debt payoff calculator with `avalanche` and then `snowball` and compare the total interest.

---

## Part 4: Each file, explained

### `calculators.py`: the math engine
**The rule: the AI never does math.** AI models sometimes get arithmetic wrong, and with money that's unacceptable. Every number comes from these functions:

- `compound_growth()` loops month by month: add growth, then add the deposit. Example: $50/month for 40 years at 7%.
- `months_to_goal()` counts months until you hit a goal, like your first $1,000.
- `emergency_fund_plan()` sets three milestones: $1,000, then 3 months, then 6 months of expenses.
- `credit_utilization()` divides total balances by total limits and labels the result excellent/good/fair/high.
- `debt_payoff()` simulates every month: add interest, pay minimums, send extra money to the target debt. *Avalanche* targets the highest rate first. *Snowball* targets the smallest balance first.

**Concepts to learn here:** functions, loops (`for`), `if/elif/else`, raising errors (`raise ValueError`), and `@dataclass` (a quick way to make a "record" like a `Debt`).

### `guardrails.py`: the safety check
It uses **regular expressions** (search patterns) to spot risky messages:
- crisis language → the 988 Lifeline (checked first, because safety comes before everything)
- SSN or card numbers → "please don't share that"
- "which stock should I buy" → explains why it can't, then offers to teach instead
- illegal requests (tax evasion, fake pay stubs, CPN scams) → refuses

**Why it matters for your defense:** it shows the committee you thought about legal limits, since only licensed advisors can make personalized stock recommendations, and about user safety.

### `knowledge/sources.json`: the trusted library
Twelve short passages, each with a `source` and `url` (CFPB, FDIC, IRS, SEC, FTC). The AI is only allowed to answer from these.
**📌 Your first task:** open each URL and confirm the passage matches what the site says today. Fix anything that doesn't. Then add more passages, such as secured cards, 401(k) matching, student loans, and FAFSA. Write each in your own words. This is real research work for your methodology.

### `retriever.py`: the search engine
Uses **BM25**, the classic search formula: a passage scores higher when it contains the question's words, especially rare words like "utilization" (stronger clues than "money"). It returns the top 3 passages.
**Concepts:** classes (`class Retriever`), dictionaries, `Counter`, sorting with `key=`.

### `llm.py`: talking to the AI
The only file that calls the AI. It has two functions on purpose:
- `grounded_answer()`: sources plus strict rules (cite sources, no stock picks, no math).
- `baseline_answer()`: a plain chatbot with no sources or rules.

Comparing these two on the same questions **is your Sub-question 1 experiment.**

### `config.py`: settings and secrets
Reads your API key from a `.env` file. **Never put keys in code. This repo is public.** `.gitignore` stops `.env` from ever being uploaded. No key? The app runs in **offline mode** and returns the best source passage directly, so demos always work.

### `coach.py`: putting it together
Runs the four steps for every question: **guardrails → retrieve → generate → add citations + disclaimer.** If you can explain this file, you can explain your whole system architecture.

### `actions.py`: approve-first
Every suggested action has a **status**: `proposed → approved → completed`, or `proposed → rejected`. Every change is saved in `history` with a timestamp. You can't approve something that was rejected; that's a rule, and a test proves it. No real money ever moves.

### `schemas.py` and `main.py`: the API
`schemas.py` defines what a valid request looks like. For example, `years` must be a whole number from 0 to 80. FastAPI checks every request automatically and rejects bad ones with a clear error.
`main.py` connects URLs to code. `@app.post("/calc/debt-payoff")` means "when someone sends data to this URL, run the function below."

### `backend/tests/`
- `test_calculators.py` checks the math against known answers.
- `test_guardrails.py` checks that the right messages get blocked.
- `test_actions.py` checks the approval rules.
- `test_api.py` calls the real API like a website would.

---

## Part 5: Saving your work to GitHub (in VS Code)

1. Make a change and save the file.
2. Click the **Source Control** icon (branch symbol) in the sidebar.
3. Type a short message describing what you did, like `Add student loan passage to knowledge base`.
4. Click **Commit**, then **Sync Changes** (or **Push**).

**Good habit:** run the tests before every commit.

---

## Part 6: Glossary

- **API**: a set of URLs that programs use to talk to each other.
- **Endpoint**: one specific URL in the API, like `/coach/ask`.
- **JSON**: the text format used to send data, like `{"question": "..."}`.
- **RAG (Retrieval-Augmented Generation)**: search trusted documents first, then have the AI answer using them.
- **Virtual environment**: a private set of Python packages for one project.
- **Pure function**: same input always gives the same output, with no side effects. Easy to test.
- **Guardrail**: a rule that stops unsafe input or output.
- **Offline mode**: running without the AI model; answers come straight from the sources.
