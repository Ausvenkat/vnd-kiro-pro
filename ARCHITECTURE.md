# SplitEasy Architecture

## Overview

SplitEasy uses a clean layered architecture:

```
┌─────────────────────────────┐
│   Streamlit UI (app.py)     │  ← User Interface
│  (No business logic)        │
└──────────────┬──────────────┘
               │
       ┌───────┴───────┐
       │               │
┌──────▼──────┐ ┌──────▼──────┐
│ Core Logic  │ │  Database   │
│(core.py)    │ │  (db.py)    │
│Pure funcs   │ │ SQLite ops  │
└─────────────┘ └─────────────┘
```

## Layer Responsibilities

### 1. UI Layer (app.py)

**Only handles**: Page rendering, form inputs, navigation, data display

**Does NOT handle**: Business logic calculations

```python
# ✓ OK - Pure UI concern
st.write(f"Balance: {format_rupees(balance)}")

# ✗ NOT OK - Business logic
balances = {member: member.total_paid - member.total_owed}
```

### 2. Core Layer (splitter/core.py)

**Pure functions** - no side effects, no I/O

- `calculate_balances()` - computes who owes whom
- `settle_up()` - generates minimal payment plan
- `format_rupees()` - formatting utility

```python
# Always deterministic - same input = same output
balances = calculate_balances(transactions)

# No database calls, no file I/O
settlements = settle_up(balances)
```

### 3. Database Layer (splitter/db.py)

**Encapsulates all SQLite operations**

- CRUD operations for groups, members, expenses
- Transparent row_factory conversion to dicts
- Connection pooling via thread-local storage

```python
db = Database()
expenses = db.get_expenses(group_id)  # Returns list of dicts
```

## Data Flow

### Adding an Expense

```
User submits form in Streamlit
        ↓
app.py validates inputs
        ↓
app.py calls db.add_expense()
        ↓
db.py inserts into SQLite
        ↓
db.py returns expense_id
        ↓
app.py shows success message
        ↓
User sees updated UI (st.rerun())
```

### Viewing Settlements

```
User navigates to Settlements page
        ↓
app.py retrieves expenses from db.get_expenses()
        ↓
app.py converts to transaction dicts
        ↓
app.py calls core.calculate_balances(transactions)
        ↓
core.py returns balances dict
        ↓
app.py calls core.settle_up(balances)
        ↓
core.py returns settlements list
        ↓
app.py renders settlements in Streamlit
```

## Key Design Decisions

### 1. Integer-Only Money

**Why**: Avoid floating-point precision errors

```python
# ✓ Correct - 1 paise minimum unit
amount_paise = 10050  # ₹100.50

# ✗ Wrong - float precision issues
amount_rupees = 100.50
```

### 2. Pure Functions in Core

**Why**: Easier to test, reason about, and parallelize

```python
# ✓ Pure - same input always gives same output
def calculate_balances(transactions):
    # No database access
    # No side effects
    # Deterministic

# ✗ Impure - depends on external state
def calculate_balances(group_id):
    expenses = database.query(...)  # Depends on DB
    return compute(expenses)
```

### 3. Database as Single Source of Truth

**Why**: Data consistency, durability, queryability

- All persistent data lives in SQLite
- UI is stateless (no session variables for calculations)
- Can safely reload page without losing data

### 4. Many-to-Many Expense Participants

**Why**: Flexible split configurations

```sql
CREATE TABLE expense_participants (
    id PRIMARY KEY,
    expense_id,       -- Which expense
    member_id,        -- Which member shares
    UNIQUE(expense_id, member_id)
);
```

This allows:
- Same expense shared by different subsets of members
- Easy queries for "which expenses does Alice share?"
- Scalable to large groups

## Settlement Algorithm

### Greedy Approach

1. **Extract** debtors (negative balance) and creditors (positive balance)
2. **Sort** by absolute value (largest first)
3. **Iterate**:
   - Pair largest debtor with largest creditor
   - Transfer min(debt, credit)
   - Remove fully settled party
   - Repeat

### Complexity

- **Time**: O(N log N) for sorting + O(N) for matching = O(N log N)
- **Space**: O(N) for storing balances
- **Transfers**: At most N-1 (optimal for trees)

### Why It Works

By always settling the largest amounts first, we minimize transfers. With N people, you need at least N-1 transfers (tree structure), and this algorithm achieves that.

## Testing Strategy

### Unit Tests (Pure Functions)

- Test `calculate_balances()` with various scenarios
- Test `settle_up()` correctness
- Test remainder distribution fairness

### Integration Tests (Database)

- Test group creation and member management
- Test expense recording and retrieval
- Test data consistency

### Property-Based Tests (Hypothesis)

- Generate random transactions
- Verify invariants:
  - Sum of balances = 0
  - Sum of settlements = total expenses
  - All balances settled after transfers

## Scalability Considerations

### Current Limits

- Single SQLite file (suitable for groups up to ~1000 people)
- In-memory settlement calculation (works for ~10k people)

### Future Improvements

- **Sharding**: Multiple database replicas for large groups
- **Caching**: Memoize balance calculations
- **Async**: Background settlement generation
- **API**: REST endpoints for mobile/web clients

## Error Handling

### Validation

- **UI**: Streamlit form validation (required fields, positive amounts)
- **DB**: SQLite constraints (UNIQUE, FOREIGN KEY)
- **Core**: Assertions on transaction data

### Edge Cases

- Empty group (handled)
- Single member (handled)
- Zero balances (handled)
- Negative amounts (prevented at UI level)
- Duplicate members (prevented by DB constraint)

## Configuration

No configuration files needed. The app auto-creates:
- `spliteasys.db` on first run
- Tables on first connection

## Future Architectures

### If Moving to Production

```
Frontend (React)
    ↓
API (FastAPI)
    ↓
Business Logic (Python)
    ↓
Database (PostgreSQL)
```

### Key Changes

1. Separate API layer for data access
2. Authentication & authorization
3. Multi-tenant support (groups)
4. Caching layer (Redis)
5. Logging & monitoring
