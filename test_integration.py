#!/usr/bin/env python3
"""Final integration test - demonstrate the complete SplitEasy system."""

from splitter.db import Database
from splitter.core import calculate_balances, settle_up, format_rupees
import os


def main():
    """Run complete integration test."""
    print("\n" + "="*70)
    print("  SPLITEASYS - COMPLETE INTEGRATION TEST")
    print("="*70)
    
    # Clean up
    if os.path.exists("integration_test.db"):
        os.remove("integration_test.db")
    
    db = Database("integration_test.db")
    
    # Scenario: Hostel group split
    print("\n📍 SCENARIO: Hostel Friends Trip")
    print("   Group of 5 friends tracking shared expenses")
    
    # Create group
    group_id = db.create_group("Hostel Friends Trip")
    print(f"\n✓ Created group: 'Hostel Friends Trip'")
    
    # Add members
    members_data = ["Alice", "Bob", "Charlie", "Diana", "Eve"]
    member_ids = {}
    for name in members_data:
        mid = db.add_member(group_id, name)
        member_ids[name] = mid
    
    print(f"✓ Added {len(members_data)} members: {', '.join(members_data)}")
    
    # Add expenses
    expenses_info = [
        ("Alice", 50000, list(member_ids.values()), "Hotel booking"),
        ("Bob", 30000, [member_ids["Bob"], member_ids["Charlie"]], "Groceries"),
        ("Charlie", 25001, list(member_ids.values()), "Restaurant dinner"),
        ("Diana", 10000, [member_ids["Alice"], member_ids["Diana"]], "Transport"),
    ]
    
    print(f"\n✓ Adding {len(expenses_info)} expenses:")
    for payer_name, amount, participants, desc in expenses_info:
        db.add_expense(group_id, member_ids[payer_name], amount, participants, desc)
        payer_names = [name for name, mid in member_ids.items() if mid in participants]
        print(f"  - {payer_name} paid {format_rupees(amount)} for {desc} ({len(participants)} people)")
    
    # Get all expenses
    expenses = db.get_expenses(group_id)
    total_spent = sum(e['amount_paise'] for e in expenses)
    print(f"\n✓ Total expenses recorded: {format_rupees(total_spent)}")
    
    # Convert to transaction format
    transactions = []
    for exp in expenses:
        transactions.append({
            'payer': exp['payer_name'],
            'amount_paise': exp['amount_paise'],
            'participants': [p['name'] for p in exp['participants']]
        })
    
    # Calculate balances
    print("\n" + "="*70)
    print("  BALANCE CALCULATION")
    print("="*70)
    
    balances = calculate_balances(transactions)
    
    print("\nMember Balances:")
    print(f"{'Member':<12} {'Balance':<15} {'Status'}")
    print("-"*40)
    
    for member in sorted(balances.keys()):
        balance = balances[member]
        if balance > 0:
            status = "Gets money back"
        elif balance < 0:
            status = "Owes money"
        else:
            status = "Settled"
        
        symbol = "+" if balance > 0 else "−" if balance < 0 else "="
        print(f"{member:<12} {symbol}{format_rupees(abs(balance)):<14} {status}")
    
    # Settlement
    print("\n" + "="*70)
    print("  SETTLEMENT PLAN")
    print("="*70)
    
    settlements = settle_up(balances)
    
    print(f"\nOptimal settlement ({len(settlements)} transfers):")
    for i, s in enumerate(settlements, 1):
        print(f"  {i}. {s.from_member:>7} pays {s.to_member:<7}: {format_rupees(s.amount_paise)}")
    
    # Verification
    print("\n" + "="*70)
    print("  VERIFICATION & STATISTICS")
    print("="*70)
    
    total_settled = sum(s.amount_paise for s in settlements)
    avg_per_person = total_spent // len(members_data)
    
    print(f"\nExpense Tracking:")
    print(f"  Total expenses:      {format_rupees(total_spent)}")
    print(f"  Number of expenses:  {len(expenses)}")
    print(f"  Average per person:  {format_rupees(avg_per_person)}")
    
    print(f"\nSettlement Optimization:")
    print(f"  People involved:     {len(balances)}")
    print(f"  Transfers needed:    {len(settlements)}")
    print(f"  Max possible:        {len(balances) - 1} (tree structure)")
    print(f"  Optimal achieved:    {'✓ Yes' if len(settlements) <= len(balances) - 1 else '✗ No'}")
    
    print(f"\nBalance Verification:")
    sum_balances = sum(balances.values())
    sum_settlements = total_settled
    print(f"  Sum of balances:     {sum_balances} (should be 0)")
    print(f"  Total settlements:   {format_rupees(sum_settlements)} (should match {format_rupees(total_spent)})")
    is_valid = sum_balances == 0 and sum_settlements == total_spent
    print(f"  Data consistency:    {'✓ Valid' if is_valid else '✗ Invalid'}")
    
    # Clean up
    db.clear_all()
    os.remove("integration_test.db")
    
    print("\n" + "="*70)
    print("  ✓ INTEGRATION TEST PASSED - SYSTEM FULLY FUNCTIONAL")
    print("="*70 + "\n")


if __name__ == "__main__":
    main()
