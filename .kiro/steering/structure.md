# Structure
- app.py: Streamlit UI only, no business logic
- splitter/core.py: pure functions (balances, settlement)
- splitter/db.py: SQLite access
- tests/: pytest + Hypothesis tests