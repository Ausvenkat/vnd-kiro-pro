# SplitEasy Requirements Specification

## Overview

SplitEasy is a Python-based expense splitting application that helps groups (friends, hostels, roommates) track shared expenses and automatically calculate who owes whom, with an optimized settlement plan to clear all debts using the fewest transfers possible.

## User Stories

### Story 1: Group Management
**As a** user  
**I want to** create groups and manage members  
**So that** I can organize expenses by trip, house, or event

**Acceptance Criteria:**
- User can create a named group
- User can add members to a group
- User can view all members in a group
- Multiple independent groups can exist
- Groups persist in SQLite database

### Story 2: Expense Tracking
**As a** user  
**I want to** log expenses and specify who paid and who shares  
**So that** the app can track who owes what

**Acceptance Criteria:**
- User can log an expense with: payer, amount, description
- User can select which members share the expense (subset of group)
- Expenses support any decimal amount (₹ currency)
- Multiple expenses can be logged per group
- All expenses persist in database
- One person paying + others sharing is the model (no split-payment)

### Story 3: Fair Splitting
**As a** user  
**I want to** split expenses equally and fairly, even when amounts don't divide evenly  
**So that** no one loses money due to rounding

**Acceptance Criteria:**
- Expenses are divided equally among participants
- When amount doesn't divide evenly, remainder paise are distributed fairly
- Example: ₹100.01 ÷ 3 people = ₹33.34 + ₹33.34 + ₹33.33 (first get remainder)
- Total of all shares always equals original amount (no rounding loss)
- All calculations use integer paise (₹0.01 unit), never floats

### Story 4: Balance Calculation
**As a** user  
**I want to** see each member's net balance  
**So that** I understand who's owed money and who owes

**Acceptance Criteria:**
- Balance shown per member (positive = owed to them, negative = they owe)
- Balance is net (accounts for all expenses they participated in)
- Balance calculation is accurate for any number of members and expenses
- Display format: member name with rupee amount (₹XX.XX)
- Shows breakdown: who gets money back, who owes money, who's settled up

### Story 5: Settlement Plan
**As a** user  
**I want to** see a minimal list of payments that clears all debts  
**So that** we can settle up with the fewest transfers possible

**Acceptance Criteria:**
- Settlement plan shows who pays whom and how much
- Achieves minimal transfers (N-1 transfers for N people, tree structure)
- Algorithm uses greedy matching (largest debtor ↔ largest creditor)
- Plan is deterministic (same input always produces same output)
- All debts are fully cleared after following the plan
- Display shows clear, actionable payment instructions

### Story 6: User Interface
**As a** user  
**I want to** use a web-based interface to manage expenses  
**So that** I don't need to learn command line tools

**Acceptance Criteria:**
- Web interface built with Streamlit
- Easy navigation between pages (create group, manage group, view settlements)
- Forms for creating groups, adding members, logging expenses
- Clear display of balances and settlement plan
- Responsive layout
- No errors when using typical workflows

### Story 7: Data Persistence
**As a** user  
**I want to** have my data saved and available when I return  
**So that** I don't lose expense history

**Acceptance Criteria:**
- All data stored in SQLite database
- Groups, members, expenses all persist
- Database created automatically on first run
- No manual setup required for database
- Data survives app restarts

## Functional Requirements

### F1: Group Operations
- Create group with unique name
- List all groups
- Retrieve group details
- Delete group (cascades to members and expenses)

### F2: Member Operations
- Add member to group
- List members in group
- Prevent duplicate member names within group
- Member tied to group (can't exist without group)

### F3: Expense Operations
- Log expense: payer, amount_paise, participant list, optional description
- Retrieve all expenses for group
- Retrieve expense with full participant details
- Amount stored as integer paise (₹0.01 minimum)

### F4: Balance Calculation
- Input: List of transactions (payer, amount, participants)
- Output: Member balances in paise
- Algorithm: For each transaction, add to payer, subtract share from participants
- Fair remainder: First N participants get +1 paise if remainder exists
- Complexity: O(N × M) where N = people, M = expenses

### F5: Settlement Generation
- Input: Member balances
- Output: Minimal payment list
- Algorithm: Greedy matching of largest debtor with largest creditor
- Guarantee: N-1 transfers for N people
- Complexity: O(N log N)

### F6: Data Validation
- Amounts must be positive integers (paise)
- Names must be non-empty strings
- Participant list must be non-empty
- Payer must be one of the participants
- Prevent duplicate group names
- Prevent duplicate member names in group

### F7: Error Handling
- Handle empty groups gracefully
- Handle single-member expenses (balanced)
- Handle already-settled groups
- Handle database connection errors
- Display meaningful error messages to user

## Non-Functional Requirements

### NF1: Performance
- Balance calculation: <100ms for typical group (10 people, 100 expenses)
- Settlement generation: <50ms
- Database operations: <200ms
- UI response: <500ms

### NF2: Scalability
- Support 1000+ people per group
- Support 10,000+ expenses per group
- Single SQLite file (no sharding needed at this scale)

### NF3: Reliability
- All database writes use transactions
- ACID compliance (no partial updates)
- Referential integrity enforced via foreign keys
- Data never lost mid-operation

### NF4: Maintainability
- Clean separation of concerns (UI, logic, data)
- Type hints on all functions
- Comprehensive documentation
- Modular code structure
- Easy to extend

### NF5: Usability
- No installation complexity beyond `pip install`
- Single command to run (`streamlit run app.py`)
- Intuitive UI with clear navigation
- Helpful error messages
- Example scenarios in demo

## Technical Constraints

### T1: Technology Stack
- Language: Python 3.11+ (not 3.14 due to package compatibility)
- UI Framework: Streamlit
- Database: SQLite
- Money Format: Integer paise (₹0.01 minimum unit)
- No floating-point for money

### T2: Architecture
- Layered: UI (app.py) → Core Logic (core.py) → Database (db.py)
- No business logic in UI
- Pure functions in core (no side effects)
- Database layer handles all persistence

### T3: Code Quality
- Type hints required on all functions
- Comprehensive docstrings
- Clean code principles
- No hardcoded values except defaults
- DRY (Don't Repeat Yourself)

### T4: Testing
- Unit tests for core functions
- Integration tests for workflows
- All tests passing before release
- Test coverage: 100% of core logic

## Out of Scope

- User authentication/login
- Multi-currency support
- Recurring expenses
- Expense categories
- Mobile app (web-only via Streamlit)
- Payment reminders
- Email notifications
- Export/import features
- Multiple databases or sharding

## Success Criteria

1. ✅ All user stories implemented and working
2. ✅ All functional requirements met
3. ✅ All non-functional requirements met
4. ✅ All tests passing (unit + integration)
5. ✅ Complete documentation provided
6. ✅ Demo scenario runs successfully
7. ✅ Code quality high (type hints, docstrings, clean architecture)
8. ✅ No critical bugs or data loss scenarios

## Glossary

- **Paise**: Smallest unit of Indian Rupee (₹0.01 = 100 paise)
- **Balance**: Net amount owed to or by a person (sum of all transactions)
- **Settlement**: Payment(s) needed to clear all debts
- **Participant**: Member who shares an expense
- **Payer**: Member who paid for an expense
- **Minimal Settlement**: Fewest number of transfers to clear all debts

## Revision History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2026-09-29 | Initial specification |
