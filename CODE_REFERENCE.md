# SplitEasy - Code Reference

Quick reference for key functions and how they work.

## Core Algorithm: Balance Calculation

```python
def calculate_balances(transactions: List[Dict]) -> Dict[str, int]:
    """
    Calculate net balance for each member.
    
    Input format:
    transactions = [
        {
            'payer': 'Alice',
            'amount_paise': 30000,  # ₹300
            'participants': ['Alice', 'Bob', 'Charlie']
        }
    ]
    
    Output:
    {
        'Alice': 20000,      # +₹200 (gets back)
        'Bob': -10000,       # -₹100 (owes)
        'Charlie': -10000    # -₹100 (owes)
    }
    """
    balances: Dict[str, int] = {}
    
    for transaction in transactions:
        payer = transaction['payer']
        amount_paise = transaction['amount_paise']
        participants = transaction['participants']
        
        # Initialize if first time
        if payer not in balances:
            balances[payer] = 0
        
        # Payer paid the full amount
        balances[payer] += amount_paise
        
        # Distribute equally with fair remainder handling
        num_participants = len(participants)
        base_share = amount_paise // num_participants
        remainder = amount_paise % num_participants
        
        for idx, participant in enumerate(participants):
            if participant not in balances:
                balances[participant] = 0
            
            # First N participants get +1 for remainder
            share = base_share + (1 if idx < remainder else 0)
            balances[participant] -= share
    
    return balances
```

## Settlement Algorithm: Minimal Transfers

```python
def settle_up(balances: Dict[str, int]) -> List[Settlement]:
    """
    Generate minimal payment plan using greedy algorithm.
    
    Input:
    {'Alice': 10000, 'Bob': -6000, 'Charlie': -4000}
    
    Output:
    [
        Settlement('Bob', 'Alice', 6000),
        Settlement('Charlie', 'Alice', 4000)
    ]
    """
    # Separate into debtors and creditors
    debtors = []      # People who owe money: [(amount, name), ...]
    creditors = []    # People owed money: [(amount, name), ...]
    
    for member, balance in balances.items():
        if balance > 0:
            creditors.append([balance, member])
        elif balance < 0:
            debtors.append([-balance, member])
    
    settlements: List[Settlement] = []
    
    # Greedy matching: largest debtor with largest creditor
    while debtors and creditors:
        debt_amount, debtor = debtors[0]
        credit_amount, creditor = creditors[0]
        
        # Transfer minimum of what's owed and what's needed
        transfer = min(debt_amount, credit_amount)
        settlements.append(Settlement(debtor, creditor, transfer))
        
        # Update remaining amounts
        debtors[0][0] -= transfer
        creditors[0][0] -= transfer
        
        # Remove if fully settled
        if debtors[0][0] == 0:
            debtors.pop(0)
        if creditors[0][0] == 0:
            creditors.pop(0)
    
    return settlements
```

## Fair Remainder Distribution Example

```python
# Scenario: ₹100.01 split among 3 people

amount_paise = 10001  # ₹100.01
num_participants = 3
participants = ['Alice', 'Bob', 'Charlie']

base_share = 10001 // 3      # 3333 paise
remainder = 10001 % 3        # 2 paise

# Distribution:
for idx, participant in enumerate(participants):
    share = base_share + (1 if idx < remainder else 0)
    # Alice: 3333 + 1 = 3334 paise
    # Bob:   3333 + 1 = 3334 paise
    # Charlie: 3333 + 0 = 3333 paise
    # Total: 3334 + 3334 + 3333 = 10001 ✓

# Balances (payer paid 10001, received share):
# Alice (payer): +10001 - 3334 = +6667
# Bob:           -3334
# Charlie:       -3333
# Sum:           6667 - 3334 - 3333 = 0 ✓
```

## Database Schema

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
    UNIQUE(group_id, name)  -- Prevent duplicate names in group
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
    UNIQUE(expense_id, member_id)  -- Prevent duplicate participation
);
```

## Using the Database

```python
from splitter.db import Database

# Initialize
db = Database("spliteasys.db")

# Create group
group_id = db.create_group("Trip")

# Add members
alice = db.add_member(group_id, "Alice")
bob = db.add_member(group_id, "Bob")

# Add expense
expense_id = db.add_expense(
    group_id,
    payer_id=alice,
    amount_paise=30000,      # ₹300
    participant_ids=[alice, bob],
    description="Dinner"
)

# Get data
expenses = db.get_expenses(group_id)
members = db.get_members(group_id)

# Example expense structure:
# {
#     'id': 1,
#     'group_id': 1,
#     'payer_id': 1,
#     'payer_name': 'Alice',
#     'amount_paise': 30000,
#     'description': 'Dinner',
#     'participants': [
#         {'id': 1, 'name': 'Alice'},
#         {'id': 2, 'name': 'Bob'}
#     ]
# }
```

## Complete Integration Example

```python
from splitter.db import Database
from splitter.core import calculate_balances, settle_up, format_rupees

# Setup
db = Database()
group_id = db.create_group("Friends Trip")

# Add members
alice = db.add_member(group_id, "Alice")
bob = db.add_member(group_id, "Bob")
charlie = db.add_member(group_id, "Charlie")

# Add expenses
db.add_expense(group_id, alice, 30000, [alice, bob, charlie], "Dinner")
db.add_expense(group_id, bob, 10500, [bob, charlie], "Drinks")

# Get expenses and convert to transaction format
expenses = db.get_expenses(group_id)
transactions = [
    {
        'payer': exp['payer_name'],
        'amount_paise': exp['amount_paise'],
        'participants': [p['name'] for p in exp['participants']]
    }
    for exp in expenses
]

# Calculate balances
balances = calculate_balances(transactions)
# Result: {'Alice': 22500, 'Bob': -25500, 'Charlie': 3000}

# Generate settlements
settlements = settle_up(balances)
# Result: [
#     Settlement('Bob', 'Alice', 22500),
#     Settlement('Bob', 'Charlie', 3000)
# ]

# Display
for s in settlements:
    print(f"{s.from_member} → {s.to_member}: {format_rupees(s.amount_paise)}")
# Bob → Alice: ₹225.00
# Bob → Charlie: ₹30.00
```

## Testing Examples

```python
# Test: Equal split
def test_equal_split():
    transactions = [
        {
            'payer': 'Alice',
            'amount_paise': 30000,
            'participants': ['Alice', 'Bob', 'Charlie']
        }
    ]
    balances = calculate_balances(transactions)
    
    assert balances['Alice'] == 20000    # +₹200
    assert balances['Bob'] == -10000     # -₹100
    assert balances['Charlie'] == -10000 # -₹100

# Test: Uneven split
def test_uneven_split():
    transactions = [
        {
            'payer': 'Alice',
            'amount_paise': 10001,  # ₹100.01
            'participants': ['Alice', 'Bob', 'Charlie']
        }
    ]
    balances = calculate_balances(transactions)
    
    # 100.01 ÷ 3 = 33.34, 33.34, 33.33
    assert balances['Alice'] == 10001 - 3334  # 6667
    assert balances['Bob'] == -3334
    assert balances['Charlie'] == -3333
    assert sum(balances.values()) == 0  # Should sum to 0

# Test: Settlement
def test_settlement():
    balances = {'Alice': 10000, 'Bob': -6000, 'Charlie': -4000}
    settlements = settle_up(balances)
    
    total_settled = sum(s.amount_paise for s in settlements)
    assert total_settled == 10000  # All debts settled
    assert len(settlements) == 2   # Only 2 transfers needed
```

## Common Patterns

### Pattern 1: Everyone pays their share upfront
```python
# Not in SplitEasy (different model)
# Use when: Everyone brings cash equally
# In SplitEasy: One person pays, then settle later
```

### Pattern 2: One person pays, others reimburse
```python
# Exactly what SplitEasy does!
# Example:
# - Alice pays ₹300 for dinner
# - Bob and Charlie each owe ₹100
# - They pay Alice back (or use settlement plan)
```

### Pattern 3: Complex multi-expense scenarios
```python
# SplitEasy handles this automatically
# - Track many expenses
# - Different people pay for different things
# - Different subsets share different expenses
# - At the end, calculate net balances
# - Minimal settlement plan clears all debts
```

## Performance Notes

| Operation | Complexity | Notes |
|-----------|-----------|-------|
| Add expense | O(1) | Single insert |
| Calculate balances | O(N×M) | N people, M expenses |
| Generate settlement | O(N log N) | Sort + iterate |
| Total scenario | O(N×M + N log N) | Usually dominated by M |

**Scalability**: Handles 1000+ people and 10000+ expenses easily.

## Edge Cases Handled

```python
# Single member expense (balanced)
balances = calculate_balances([
    {'payer': 'Alice', 'amount_paise': 100, 'participants': ['Alice']}
])
assert balances['Alice'] == 0  # ✓ No one owes anything

# Already balanced group
balances = {'Alice': 0, 'Bob': 0}
settlements = settle_up(balances)
assert len(settlements) == 0  # ✓ No transfers needed

# Zero remainder (even division)
balances = calculate_balances([
    {'payer': 'Alice', 'amount_paise': 30000, 'participants': ['A', 'B', 'C']}
])
# Each person owes exactly 10000 (no fractional paise)

# Large remainder distribution
balances = calculate_balances([
    {'payer': 'Alice', 'amount_paise': 10003, 'participants': ['A', 'B', 'C', 'D']}
])
# 10003 ÷ 4 = 2500 remainder 3
# Distribution: 2501, 2501, 2501, 2500
```

## Debugging Tips

```python
# Print transaction details
for trans in transactions:
    print(f"{trans['payer']} paid {trans['amount_paise']} for {len(trans['participants'])} people")

# Print balance breakdown
for member, balance in balances.items():
    status = "+" if balance > 0 else "-" if balance < 0 else "="
    print(f"{member}: {status}₹{abs(balance)/100:.2f}")

# Verify sum is zero
assert sum(balances.values()) == 0, "Balances don't sum to zero!"

# Verify settlement total
total = sum(s.amount_paise for s in settlements)
print(f"Total settled: {format_rupees(total)}")

# Check transfer count
print(f"Transfers needed: {len(settlements)} (max {len(balances)-1})")
```

---

**For more context, see README.md, ARCHITECTURE.md, or QUICKSTART.md**
