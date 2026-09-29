# SplitEasy - Smart Expense Splitter

A Python-based expense splitting application for groups (friends, hostels, roommates). Automatically calculates who owes whom and generates a minimal settlement plan to clear all debts with the fewest transfers.

## Key Features

✨ **Group Management** - Create groups and add members
💰 **Expense Tracking** - Log expenses with flexible split configurations
🧮 **Fair Splitting** - Handles uneven splits with fair remainder distribution
📊 **Balance Calculation** - Shows each member's net balance (who's owed money, who owes)
🔄 **Minimal Settlement** - Generates an optimized payment plan using minimal transfers
💵 **Integer Precision** - All amounts stored as paise (₹0.01) to avoid float rounding errors

## Tech Stack

- **Backend**: Python 3.11+
- **UI**: Streamlit
- **Database**: SQLite
- **Testing**: pytest + Hypothesis
- **All Money**: Integer paise (never floats)

## Project Structure

```
spliteasys/
├── app.py                 # Streamlit UI (no business logic)
├── splitter/
│   ├── core.py           # Pure functions: balances & settlement
│   └── db.py             # SQLite database access
├── tests/
│   └── test_core.py      # pytest tests with Hypothesis
├── demo.py               # Example usage
├── requirements.txt      # Dependencies
└── spliteasys.db         # SQLite database (created at runtime)
```

## Installation

```bash
# Clone or download the project
cd vnd-kiro-pro

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

## Usage

### Running the Streamlit App

```bash
streamlit run app.py
```

Then open `http://localhost:8501` in your browser.

### Running the Demo

```bash
python3 demo.py
```

Shows a complete example with 4 people and 4 expenses.

### Running Tests

```bash
pytest tests/test_core.py -v
```

## How It Works

### 1. Core Concepts

**Balances**: Each member has a balance:
- **Positive** = they are owed money
- **Negative** = they owe money
- **Zero** = settled

**Settlement**: A list of transfers that clears all debts with minimal transactions.

### 2. Balance Calculation

When you add an expense:
1. The payer's balance increases by the full amount (they paid)
2. The expense is split equally among participants
3. Each participant's balance decreases by their share

**Example**: Alice pays ₹300 for dinner (4 people)
- Each person's share: ₹75
- Alice: +₹300 (paid) - ₹75 (her share) = +₹225 owed
- Others: -₹75 each (they owe)

### 3. Uneven Split Handling

When an amount doesn't divide evenly, the remainder paise are distributed fairly:

**Example**: ₹100.01 split 3 ways
- Base share: ₹100.01 ÷ 3 = ₹33.33 remainder ₹0.01
- Distribution: ₹33.34, ₹33.33, ₹33.33 (first person gets the remainder)

### 4. Settlement Algorithm

The settlement algorithm uses a greedy approach:
1. List all debtors (owe money) and creditors (owed money)
2. Repeatedly match the largest debtor with the largest creditor
3. Transfer the minimum needed to partially or fully settle one of them
4. Remove settled parties and repeat

**Result**: Minimal transfers needed (often N-1 transfers for N people)

## API Reference

### Core Functions (`splitter/core.py`)

```python
def calculate_balances(transactions: List[Dict]) -> Dict[str, int]
```
Calculates net balance for each member.

**Parameters:**
- `transactions`: List of dicts with:
  - `'payer'`: member name (str)
  - `'amount_paise'`: total amount in paise (int)
  - `'participants'`: list of member names sharing (list[str])

**Returns**: Dict mapping member name to balance in paise

```python
def settle_up(balances: Dict[str, int]) -> List[Settlement]
```
Generates minimal settlement plan.

**Parameters:**
- `balances`: Dict of member balances in paise

**Returns**: List of Settlement objects (from_member, to_member, amount_paise)

### Database Functions (`splitter/db.py`)

```python
db = Database("spliteasys.db")

# Groups
group_id = db.create_group("Trip Name")
group = db.get_group(group_id)
groups = db.list_groups()

# Members
member_id = db.add_member(group_id, "Alice")
members = db.get_members(group_id)

# Expenses
expense_id = db.add_expense(
    group_id,
    payer_id,
    amount_paise,
    participant_ids,
    description="optional"
)
expenses = db.get_expenses(group_id)
```

## Example Usage

```python
from splitter.db import Database
from splitter.core import calculate_balances, settle_up, format_rupees

# Create database and group
db = Database()
group_id = db.create_group("Hostel Trip")

# Add members
alice = db.add_member(group_id, "Alice")
bob = db.add_member(group_id, "Bob")
charlie = db.add_member(group_id, "Charlie")

# Add expenses
db.add_expense(
    group_id,
    alice,
    30000,  # ₹300
    [alice, bob, charlie],
    "Dinner"
)

db.add_expense(
    group_id,
    bob,
    10500,  # ₹105
    [bob, charlie],
    "Drinks"
)

# Calculate balances
expenses = db.get_expenses(group_id)
transactions = [{
    'payer': exp['payer_name'],
    'amount_paise': exp['amount_paise'],
    'participants': [p['name'] for p in exp['participants']]
} for exp in expenses]

balances = calculate_balances(transactions)
# Output: {'Alice': 22500, 'Bob': -25500, 'Charlie': 3000}

# Generate settlement plan
settlements = settle_up(balances)
for s in settlements:
    print(f"{s.from_member} pays {s.to_member}: {format_rupees(s.amount_paise)}")
# Output:
# Bob pays Alice: ₹225.00
# Bob pays Charlie: ₹30.00
```

## Testing

The test suite covers:

- ✓ Simple equal splits
- ✓ Uneven splits with remainder handling
- ✓ Multiple expenses and running balances
- ✓ Settlement algorithm correctness
- ✓ Minimal transfer generation
- ✓ Edge cases (single member, zero balances)

Run tests:
```bash
pytest tests/test_core.py -v
```

## Features in Detail

### Fair Remainder Distribution

When amounts don't divide evenly, SplitEasy distributes remainder paise fairly:
- Calculates base share and remainder
- Gives the remainder to the first participant(s)
- Ensures total always equals the original amount

### Minimal Settlement Algorithm

Instead of N×M payments (everyone paying everyone), generates N-1 transfers:
- Greedy matching of largest debtors and creditors
- Minimizes total number of transfers
- Fast O(N log N) complexity

### Integer-Only Arithmetic

- All amounts stored as paise (₹0.01 units)
- No floating-point rounding errors
- Example: ₹100.50 = 10050 paise

## Roadmap / Future Features

- [ ] Expense categories (food, transport, lodging, etc.)
- [ ] Payment history and audit trail
- [ ] Member profiles and statistics
- [ ] Export reports (PDF, CSV)
- [ ] Recurring expenses
- [ ] Mobile app (React Native)
- [ ] Multi-currency support
- [ ] Group statistics and charts

## Troubleshooting

**Issue**: Database errors on startup
- **Solution**: Delete `spliteasys.db` and restart

**Issue**: Streamlit app not loading
- **Solution**: Ensure Streamlit is installed: `pip install streamlit`

**Issue**: Tests failing
- **Solution**: Ensure pytest is installed: `pip install pytest hypothesis`

## Contributing

Contributions welcome! Areas for improvement:
- Additional settlement algorithms
- Performance optimization for large groups
- Edge case handling
- More comprehensive tests

## License

MIT License - feel free to use and modify

## Questions?

For issues or questions, check the code comments or run the demo to see how it works.
