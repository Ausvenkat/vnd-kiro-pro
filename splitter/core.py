"""Pure functions for balance calculation and settlement."""

from typing import Dict, List, Tuple
from dataclasses import dataclass


@dataclass
class Settlement:
    """A single payment to settle debts."""
    from_member: str
    to_member: str
    amount_paise: int


def calculate_balances(transactions: List[Dict]) -> Dict[str, int]:
    """
    Calculate net balance for each member in paise.
    Positive balance = they are owed money. Negative = they owe money.
    
    Args:
        transactions: List of dicts with keys:
            - 'payer': member who paid (str)
            - 'amount_paise': total amount in paise (int)
            - 'participants': list of members who share (list[str])
    
    Returns:
        Dict mapping member name to balance in paise
    """
    balances: Dict[str, int] = {}
    
    for transaction in transactions:
        payer = transaction['payer']
        amount_paise = transaction['amount_paise']
        participants = transaction['participants']
        
        if payer not in balances:
            balances[payer] = 0
        
        # Distribute amount equally among participants, handling remainder
        num_participants = len(participants)
        base_share = amount_paise // num_participants
        remainder = amount_paise % num_participants
        
        # Track how much the payer paid
        balances[payer] += amount_paise
        
        # Distribute shares fairly (first N members get base_share + 1)
        for idx, participant in enumerate(participants):
            if participant not in balances:
                balances[participant] = 0
            
            share = base_share + (1 if idx < remainder else 0)
            balances[participant] -= share
    
    return balances


def settle_up(balances: Dict[str, int]) -> List[Settlement]:
    """
    Calculate minimal transfers to settle all debts.
    Uses a greedy algorithm: match largest debtors with largest creditors.
    
    Args:
        balances: Dict mapping member name to balance in paise
                 (positive = owed money, negative = owes money)
    
    Returns:
        List of Settlement objects representing transfers
    """
    # Create working copies with only non-zero balances
    debtors = []  # (amount, name) - people who owe money
    creditors = []  # (amount, name) - people owed money
    
    for member, balance in balances.items():
        if balance > 0:
            creditors.append([balance, member])
        elif balance < 0:
            debtors.append([-balance, member])
    
    settlements: List[Settlement] = []
    
    # Match debtors with creditors greedily
    while debtors and creditors:
        debt_amount, debtor = debtors[0]
        credit_amount, creditor = creditors[0]
        
        # Settle as much as possible
        transfer = min(debt_amount, credit_amount)
        settlements.append(Settlement(
            from_member=debtor,
            to_member=creditor,
            amount_paise=transfer
        ))
        
        # Update remaining amounts
        debtors[0][0] -= transfer
        creditors[0][0] -= transfer
        
        # Remove if fully settled
        if debtors[0][0] == 0:
            debtors.pop(0)
        if creditors[0][0] == 0:
            creditors.pop(0)
    
    return settlements


def format_rupees(paise: int) -> str:
    """Format paise as rupees with 2 decimal places."""
    rupees = paise / 100
    return f"₹{rupees:.2f}"
