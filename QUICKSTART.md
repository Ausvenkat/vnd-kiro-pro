# SplitEasy Quick Start Guide

## 5-Minute Setup

### 1. Install Dependencies
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Try the Demo
```bash
python3 demo.py
```
See a complete 4-person expense split scenario with settlement plan.

### 3. Run the App
```bash
streamlit run app.py
```
Opens at `http://localhost:8501`

## Using the App

### Creating a Group
1. Click **"Create Group"** in sidebar
2. Enter group name (e.g., "Hostel Trip")
3. Click **Create**
4. App shows your new group

### Adding Members
1. Go to **"Manage Group"**
2. Select your group
3. Click **Members** tab
4. Enter name and click **Add**
5. Repeat for each friend

### Adding an Expense
1. Click **Add Expense** tab
2. Select who paid
3. Enter amount (in rupees)
4. Enter description
5. Select who shares the expense
6. Click **Add Expense**

**Example**: Alice paid ₹300 for dinner shared by Alice, Bob, and Charlie
- Each person's share: ₹100
- Alice paid ₹300, owes ₹100 → balance ₹200 ✓
- Bob and Charlie owe ₹100 each

### Viewing Settlements
1. Click **"View Settlements"** in sidebar
2. Select your group
3. See:
   - **Who gets money back** (positive balance)
   - **Who owes money** (negative balance)
   - **Settlement plan** (exact transfers needed)

## Understanding Balances

### Example: 3 friends, ₹330 total

| Event | Alice | Bob | Charlie |
|-------|-------|-----|---------|
| Start | 0 | 0 | 0 |
| Alice pays ₹300 for all | +₹200 | -₹100 | -₹100 |
| Bob pays ₹30 for himself | +₹200 | -₹80 | -₹100 |

### Settlement
- Bob pays Alice ₹80
- Charlie pays Alice ₹100
- Result: Everyone settled ✓

## Fair Split Example

**Scenario**: ₹100.01 split between 3 people

Normal division: 100.01 ÷ 3 = 33.33... (not exact)

**SplitEasy handles it fairly**:
- Person 1: ₹33.34 (gets the extra paise)
- Person 2: ₹33.33
- Person 3: ₹33.33
- Total: ₹100.01 ✓

## Common Scenarios

### Scenario 1: Equal Split
Everyone goes to dinner, Alice pays ₹900 for 3 people.
- Each person's share: ₹300
- Alice: +₹600 (gets back)
- Bob, Charlie: -₹300 each (owe)

**Settlement**:
- Bob → Alice: ₹300
- Charlie → Alice: ₹300

### Scenario 2: Partial Participation
Trip expenses:
- Hotel (₹5000, all 4 people)
- Breakfast (₹800, only 2 people)
- Transport (₹1200, all 4)

SplitEasy calculates each person's share based on which expenses they participated in.

### Scenario 3: Multiple Payers
- Alice pays for hotel
- Bob pays for food
- Charlie pays for transport
- Diana pays for entertainment

SplitEasy tracks who paid what and who should pay whom at the end.

## Tips

💡 **Tip 1**: Add all members first, then add expenses
💡 **Tip 2**: You can add expenses in any order
💡 **Tip 3**: Settlement shows minimal transfers (not everyone-to-everyone)
💡 **Tip 4**: Refresh app anytime to see latest data
💡 **Tip 5**: All amounts are in ₹ (rupees), stored as paise internally

## Troubleshooting

**App won't start?**
- Ensure Python 3.11+ installed: `python3 --version`
- Ensure Streamlit installed: `pip install streamlit`

**Database errors?**
- Delete `spliteasys.db` and restart the app

**Settlement doesn't look right?**
- Make sure all members and expenses are added
- Refresh the page
- Run the demo to verify system works

**Uneven split not fair?**
- SplitEasy distributes remainder paise to first participants
- Total always equals the expense amount

## Running Tests

```bash
# Install test dependencies
pip install pytest hypothesis

# Run core logic tests
pytest tests/test_core.py -v
```

**Expected output**: All tests passing ✓

## Architecture (Advanced)

- **UI** (`app.py`): Pure Streamlit display, no calculations
- **Logic** (`splitter/core.py`): All balance and settlement calculations
- **Database** (`splitter/db.py`): SQLite persistence

See `ARCHITECTURE.md` for deep dive.

## Need Help?

- See `README.md` for complete documentation
- See `ARCHITECTURE.md` for technical details
- Run `python3 demo.py` to see a working example
- Check `IMPLEMENTATION_SUMMARY.md` for what's implemented

## Next Steps

1. ✓ Create a group
2. ✓ Add your friends as members
3. ✓ Add your expenses
4. ✓ View settlements and settle up!

**That's it! You're ready to split expenses fairly.** 🎉
