# SplitEasy Design Specification

## Architecture Overview

```
┌─────────────────────────────────────────────────────┐
│              Streamlit Web UI (app.py)              │
│          Create Groups | Manage Group | Settlements │
│                  (No business logic)                │
└──────────────────────┬──────────────────────────────┘
                       │
        ┌──────────────┴──────────────┐
        │                             │
┌───────▼────────────┐     ┌─────────▼─────────┐
│  Core Logic        │     │    Database       │
│  (splitter/core.py)│     │  (splitter/db.py) │
│                    │     │                   │
│ - Balances         │     │ - Groups table    │
│ - Settlement       │     │ - Members table   │
│ - Formatting       │     │ - Expenses table  │
│ (Pure functions)   │     │ - Participants    │
└────────────────────┘     │   table           │
                           │ (SQLite)          │
                           └───────────────────┘
```

## Layer Responsibilities

### UI Layer (app.py)
**Responsibility**: Present interface, handle user input, display results

**Does**:
- Render Streamlit pages
- Handle form inputs (create group, add member, log expense)
- Call database and core functions
- Display results to user
- Navigation between pages

**Doesn't**:
- Calculate balances
- Generate settlement plans
- Access database directly for calculations
- Store state (except session_state for current selections)

**Key Components**:
- `create_group_page()` - New group creation
- `manage_group_page()` - Members and expenses
- `view_settlements_page()` - Balances and settlement plan

### Core Logic Layer (splitter/core.py)
**Responsibility**: All business logic calculations

**Does**:
- Calculate member balances from transactions
- Generate minimal settlement plan
- Format monetary values
- Pure functions (no side effects)

**Doesn't**:
- Access database
- Present to UI
- Store state
- Handle I/O

**Key Functions**:
```python
def calculate_balances(transactions: List[Dict]) -> Dict[str, int]
    # Input: [{'payer': str, 'amount_paise': int, 'participants': List[str]}]
    # Output: {member_name: balance_paise}
    # Complexity: O(N × M)

def settle_up(balances: Dict[str, int]) -> List[Settlement]
    # Input: {member: balance}
    # Output: [Settlement(from, to, amount)]
    # Complexity: O(N log N)

def format_rupees(paise: int) -> str
    # Input: paise (int)
    # Output: "₹XX.XX" format
```

### Database Layer (splitter/db.py)
**Responsibility**: All data persistence

**Does**:
- CRUD operations for groups, members, expenses
- Schema management
- Data validation via constraints
- Transaction management

**Doesn't**:
- Business logic calculations
- Present data (returns dicts)
- Handle UI interactions

**Key Methods**:
- `create_group(name)` → group_id
- `add_member(group_id, name)` → member_id
- `add_expense(group_id, payer_id, amount_paise, participant_ids, description)` → expense_id
- `get_expenses(group_id)` → List[Dict]
- `get_members(group_id)` → List[Dict]

## Data Model

### Database Schema

```sql
-- Groups
CREATE TABLE groups (
    id INTEGER PRIMARY KEY,
    name TEXT UNIQUE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Members of groups
CREATE TABLE members (
    id INTEGER PRIMARY KEY,
    group_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (group_id) REFERENCES groups(id),
    UNIQUE(group_id, name)  -- No duplicate names in group
);

-- Expenses (who paid and how much)
CREATE TABLE expenses (
    id INTEGER PRIMARY KEY,
    group_id INTEGER NOT NULL,
    payer_id INTEGER NOT NULL,
    amount_paise INTEGER NOT NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (group_id) REFERENCES groups(id),
    FOREIGN KEY (payer_id) REFERENCES members(id)
);

-- Many-to-many: which members share each expense
CREATE TABLE expense_participants (
    id INTEGER PRIMARY KEY,
    expense_id INTEGER NOT NULL,
    member_id INTEGER NOT NULL,
    FOREIGN KEY (expense_id) REFERENCES expenses(id),
    FOREIGN KEY (member_id) REFERENCES members(id),
    UNIQUE(expense_id, member_id)  -- No duplicate participation
);
```

### Core Data Structures

```python
# Transaction (for calculations)
Transaction = {
    'payer': str,                    # Member who paid
    'amount_paise': int,             # Total amount in paise
    'participants': List[str]        # Members who share
}

# Settlement (output of settle_up)
Settlement = {
    'from_member': str,              # Who pays
    'to_member': str,                # Who receives
    'amount_paise': int              # How much
}

# Expense (retrieved from DB)
Expense = {
    'id': int,
    'payer_id': int,
    'payer_name': str,
    'amount_paise': int,
    'description': str,
    'participants': [
        {'id': int, 'name': str},
        ...
    ]
}
```

## Algorithms

### Balance Calculation Algorithm

```
Input: transactions = [
    {
        'payer': 'Alice',
        'amount_paise': 30000,
        'participants': ['Alice', 'Bob', 'Charlie']
    },
    ...
]

Algorithm:
1. Initialize: balances = {}

2. For each transaction:
   a. Add full amount to payer's balance
      balances[payer] += amount_paise
   
   b. Calculate share per participant:
      - base_share = amount_paise // num_participants
      - remainder = amount_paise % num_participants
      - For first 'remainder' participants: share = base_share + 1
      - For others: share = base_share
   
   c. Subtract each participant's share:
      balances[participant] -= share

3. Return balances

Output: {
    'Alice': 20000,      # +₹200 owed to Alice
    'Bob': -10000,       # -₹100 Bob owes
    'Charlie': -10000    # -₹100 Charlie owes
}

Complexity: O(N × M) where N = people, M = expenses
Space: O(N)
```

### Settlement Generation Algorithm (Greedy)

```
Input: balances = {
    'Alice': 10000,
    'Bob': -6000,
    'Charlie': -4000
}

Algorithm:
1. Separate into debtors and creditors
   debtors = [[-balance, name], ...]      # People who owe
   creditors = [[balance, name], ...]     # People owed to

2. While debtors and creditors exist:
   a. Get largest debtor and largest creditor
   b. Transfer min(debt, credit) amount
      settlements.append(Settlement(debtor, creditor, transfer))
   c. Update remaining amounts
   d. Remove fully settled parties

3. Return settlements

Output: [
    Settlement('Bob', 'Alice', 6000),
    Settlement('Charlie', 'Alice', 4000)
]

Guarantee: At most N-1 transfers (tree structure optimal)
Complexity: O(N log N) for sorting + O(N) for matching = O(N log N)
Space: O(N)
```

### Remainder Distribution

```
Problem: ₹100.01 split among 3 people

Solution:
amount_paise = 10001
num_participants = 3

base_share = 10001 // 3 = 3333 paise
remainder = 10001 % 3 = 2 paise

Distribution:
- First 2 participants get 3333 + 1 = 3334 paise
- Last participant gets 3333 paise
- Total: 3334 + 3334 + 3333 = 10001 ✓

Why first participants?
- Simple and fair
- Ensures exact paise total
- Deterministic (same input = same distribution)
```

## Data Flow

### Workflow 1: Create Group and Add Members

```
User Input (Streamlit)
    ↓
app.create_group_page()
    ↓
db.create_group(name)
    ↓
SQLite INSERT groups
    ↓
User sees success message
```

### Workflow 2: Log Expense

```
User Input (Streamlit)
    ↓
app.add_expense_tab()
    ├─ Get payer ID
    ├─ Get amount_rupees
    ├─ Get participant IDs
    └─ Get description
    ↓
Convert rupees to paise: amount_paise = int(rupees * 100)
    ↓
db.add_expense(group_id, payer_id, amount_paise, participant_ids, description)
    ↓
SQLite:
    ├─ INSERT expenses
    └─ INSERT expense_participants (for each participant)
    ↓
User sees expense added
```

### Workflow 3: View Settlements

```
User Input (Streamlit - Select Group)
    ↓
app.view_settlements_page(group_id)
    ↓
db.get_expenses(group_id)
    ↓
SQLite SELECT expenses + expense_participants
    ↓
Convert to transaction format
    ↓
core.calculate_balances(transactions)
    ↓
Display balance sheet
    ↓
core.settle_up(balances)
    ↓
Display settlement plan (who pays whom)
```

## Key Design Decisions

### D1: Integer Paise for Money
**Decision**: Store all amounts as integer paise (₹0.01 minimum)
**Rationale**: Eliminates floating-point precision errors
**Trade-off**: User inputs in rupees, converted to paise internally

### D2: Remainder Distribution to First Participants
**Decision**: First N participants get +1 paise if remainder exists
**Rationale**: Simple, fair, deterministic
**Trade-off**: Not random, but predictable

### D3: Greedy Settlement Algorithm
**Decision**: Match largest debtor with largest creditor repeatedly
**Rationale**: Achieves N-1 transfers (optimal), O(N log N) complexity
**Trade-off**: Not unique solution, but guaranteed minimal

### D4: Pure Functions in Core
**Decision**: No state, no I/O in core.py
**Rationale**: Easy to test, parallelize, reason about
**Trade-off**: Must convert data to/from dicts at boundaries

### D5: Database Constraints for Consistency
**Decision**: Use UNIQUE and FOREIGN KEY constraints
**Rationale**: Prevent invalid data at DB level
**Trade-off**: Some operations fail at DB level (must handle gracefully)

### D6: Single SQLite File
**Decision**: All data in one .db file
**Rationale**: Simple, no network, works offline, suitable for group size
**Trade-off**: Not suitable for 1000s of groups (would need sharding)

## UI Flow

```
┌─ Create Group
│  ├─ Enter group name
│  ├─ Click Create
│  └─ Show success
│
├─ Manage Group
│  ├─ Select group from dropdown
│  └─ Three tabs:
│     ├─ Members
│     │  ├─ Enter member name
│     │  ├─ Click Add
│     │  └─ Show member list
│     │
│     ├─ Add Expense
│     │  ├─ Select payer
│     │  ├─ Enter amount (₹)
│     │  ├─ Enter description
│     │  ├─ Select participants (multi-select)
│     │  ├─ Click Add Expense
│     │  └─ Show success
│     │
│     └─ Expenses
│        └─ List all expenses with details
│
└─ View Settlements
   ├─ Select group from dropdown
   ├─ Show balance sheet
   │  ├─ Who gets money back
   │  ├─ Who owes money
   │  └─ Who's settled up
   │
   └─ Show settlement plan
      ├─ List of payments
      └─ All settled indicator
```

## Error Handling Strategy

### Input Validation
- UI validates before sending (Streamlit form constraints)
- Database validates via constraints (UNIQUE, FOREIGN KEY)
- Core functions assume valid input (assert statements)

### Error Messages
- Database errors caught and displayed to user
- Invalid inputs rejected with clear message
- Empty groups handled gracefully
- Single-member expenses handled correctly

### Edge Cases Handled
- Empty group (no members) → can't add expenses
- Single member expense → balanced (no one owes)
- Zero balance → settled up (no action needed)
- Already settled group → settlement plan empty

## Performance Considerations

### Balance Calculation
- O(N × M): iterate over M expenses, N people per expense
- For typical group (10 people, 100 expenses): ~1000 operations → <100ms
- Memory: O(N) for balance dict

### Settlement Generation
- O(N log N): sort + iterate
- For typical group (10 people): ~60 operations → <50ms
- Memory: O(N) for debtors/creditors arrays

### Database Queries
- Indexed on: group_id, member names
- Queries: get_expenses(), get_members() → <100ms typical
- Transactions used for atomicity

## Testing Strategy

### Unit Tests
- Balance calculation: various split scenarios
- Settlement generation: simple and complex cases
- Remainder distribution: fairness verification
- Edge cases: single member, zero balance, etc.

### Integration Tests
- Complete workflow: create group → add members → log expenses → view settlements
- Data consistency: verify DB integrity after operations
- Large scenarios: 1000+ people, 10000+ expenses (performance check)

### Demo
- 4 people, 4 expenses
- Shows complete workflow
- Demonstrates fair remainder handling
- Verifies optimal settlement

## Extensibility

### Future Enhancements
- REST API layer above core
- Mobile app (React Native)
- User authentication
- Expense categories
- Recurring expenses
- Payment reminders

### Extension Points
- Settlement algorithm can be replaced (currently greedy)
- Money format can be changed (currently paise)
- Database backend can change (currently SQLite → PostgreSQL)
- UI framework can change (currently Streamlit → React)

## Deployment Considerations

### Development
- Single machine, SQLite
- Virtual environment with pip
- Command: `streamlit run app.py`

### Production (Future)
- Would need: PostgreSQL, authentication, API, React frontend
- Current design supports this transition (pure functions, clean layers)
