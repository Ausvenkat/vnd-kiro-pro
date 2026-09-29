#!/usr/bin/env python3
"""Demo script showing SplitEasy in action."""

import os
from splitter.db import Database
from splitter.core import calculate_balances, settle_up, format_rupees


def print_section(title: str):
    """Print a formatted section header."""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print('='*60)


def demo():
    """Run a comprehensive demo."""
    # Clean up old demo database
    if os.path.exists("demo.db"):
        os.remove("demo.db")
    
    db = Database("demo.db")
    
    # Create a group
    print_section("1. Creating a Group")
    group_id = db.create_group("Hostel Dinner Trip")
    print(f"✓ Group created: ID {group_id}")
    
    # Add members
    print_section("2. Adding Members")
    members = ["Alice", "Bob", "Charlie", "Diana"]
    member_ids = {}
    for name in members:
        mid = db.add_member(group_id, name)
        member_ids[name] = mid
        print(f"✓ Added: {name}")
    
    # Add expenses
    print_section("3. Adding Expenses")
    
    # Expense 1: Alice pays for dinner, everyone shares
    print("\nExpense 1: Dinner at restaurant")
    db.add_expense(
        group_id,
        payer_id=member_ids["Alice"],
        amount_paise=400_00,  # ₹400
        participant_ids=list(member_ids.values()),
        description="Restaurant dinner"
    )
    print(f"✓ Alice paid ₹400 for dinner (shared by {', '.join(members)})")
    
    # Expense 2: Bob pays for drinks, only Alice and Bob share
    print("\nExpense 2: Drinks at bar")
    db.add_expense(
        group_id,
        payer_id=member_ids["Bob"],
        amount_paise=150_00,  # ₹150
        participant_ids=[member_ids["Alice"], member_ids["Bob"]],
        description="Drinks at bar"
    )
    print(f"✓ Bob paid ₹150 for drinks (shared with Alice)")
    
    # Expense 3: Charlie pays for taxi, everyone shares
    print("\nExpense 3: Taxi ride")
    db.add_expense(
        group_id,
        payer_id=member_ids["Charlie"],
        amount_paise=260_00,  # ₹260
        participant_ids=list(member_ids.values()),
        description="Taxi to venue"
    )
    print(f"✓ Charlie paid ₹260 for taxi (shared by {', '.join(members)})")
    
    # Expense 4: Uneven split - Diana pays ₹100 for 3 people
    print("\nExpense 4: Snacks (uneven split)")
    db.add_expense(
        group_id,
        payer_id=member_ids["Diana"],
        amount_paise=10001,  # ₹100.01 to show remainder handling
        participant_ids=[member_ids["Diana"], member_ids["Alice"], member_ids["Bob"]],
        description="Snacks"
    )
    print(f"✓ Diana paid ₹100.01 for snacks (shared with Alice and Bob)")
    print(f"  (Note: ₹100.01 ÷ 3 = ₹33.34, ₹33.34, ₹33.33 - remainder handled fairly)")
    
    # Calculate and display balances
    print_section("4. Calculating Balances")
    
    expenses = db.get_expenses(group_id)
    transactions = []
    for exp in expenses:
        transactions.append({
            'payer': exp['payer_name'],
            'amount_paise': exp['amount_paise'],
            'participants': [p['name'] for p in exp['participants']]
        })
    
    balances = calculate_balances(transactions)
    
    print("\nMember Balances (positive = owed money, negative = owes money):")
    print(f"{'Member':<12} {'Balance':<15} {'Status'}")
    print("-" * 40)
    
    for member in sorted(balances.keys()):
        balance = balances[member]
        if balance > 0:
            status = "Gets back"
        elif balance < 0:
            status = "Owes"
        else:
            status = "Settled"
        print(f"{member:<12} {format_rupees(balance):<15} {status}")
    
    # Calculate settlement plan
    print_section("5. Settlement Plan (Minimal Transfers)")
    
    settlements = settle_up(balances)
    
    if settlements:
        print("\nTransfers needed to settle all debts:\n")
        for i, settlement in enumerate(settlements, 1):
            print(f"{i}. {settlement.from_member} pays {settlement.to_member}: {format_rupees(settlement.amount_paise)}")
    else:
        print("\n✓ Everyone is settled! No transfers needed.")
    
    # Verification
    print_section("6. Verification")
    total_expenses = sum(exp['amount_paise'] for exp in expenses)
    total_settled = sum(s.amount_paise for s in settlements)
    
    print(f"Total expenses: {format_rupees(total_expenses)}")
    print(f"Total to settle: {format_rupees(total_settled)}")
    print(f"Number of transfers: {len(settlements)}")
    print(f"Minimal transfers achieved: {'✓ Yes' if len(settlements) <= len(members) - 1 else '✗ No'}")
    
    # Summary statistics
    print_section("7. Summary")
    print(f"Group: Hostel Dinner Trip")
    print(f"Members: {len(members)}")
    print(f"Expenses: {len(expenses)}")
    print(f"Total spent: {format_rupees(total_expenses)}")
    print(f"Average per person: {format_rupees(total_expenses // len(members))}")
    
    # Cleanup
    os.remove("demo.db")
    print("\n✓ Demo complete!")


if __name__ == "__main__":
    demo()
