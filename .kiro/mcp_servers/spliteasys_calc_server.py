#!/usr/bin/env python3
"""
MCP Server for SplitEasy Expense Calculations
Provides tools for balance calculation and settlement planning
"""

import json
from typing import Dict, List, Any


class SplitEasyCalcServer:
    """MCP Server for SplitEasy calculations"""
    
    @staticmethod
    def calculate_balances(transactions: List[Dict]) -> dict:
        """
        Calculate net balance for each member
        
        Args:
            transactions: List of dicts with payer, amount_paise, participants
        
        Returns:
            Dict mapping member name to balance in paise
        """
        try:
            balances: Dict[str, int] = {}
            
            for transaction in transactions:
                payer = transaction['payer']
                amount_paise = transaction['amount_paise']
                participants = transaction['participants']
                
                if payer not in balances:
                    balances[payer] = 0
                
                # Payer paid the full amount
                balances[payer] += amount_paise
                
                # Distribute equal shares with fair remainder
                num_participants = len(participants)
                base_share = amount_paise // num_participants
                remainder = amount_paise % num_participants
                
                for idx, participant in enumerate(participants):
                    if participant not in balances:
                        balances[participant] = 0
                    
                    share = base_share + (1 if idx < remainder else 0)
                    balances[participant] -= share
            
            # Convert to rupees for display
            balances_rupees = {k: v / 100 for k, v in balances.items()}
            
            return {
                "status": "success",
                "balances_paise": balances,
                "balances_rupees": balances_rupees
            }
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    @staticmethod
    def settle_up(balances: Dict[str, int]) -> dict:
        """
        Generate minimal settlement plan
        
        Args:
            balances: Dict mapping member name to balance in paise
        
        Returns:
            List of settlements (from_member, to_member, amount_paise)
        """
        try:
            # Separate into debtors and creditors
            debtors = []  # [amount, name]
            creditors = []  # [amount, name]
            
            for member, balance in balances.items():
                if balance > 0:
                    creditors.append([balance, member])
                elif balance < 0:
                    debtors.append([-balance, member])
            
            settlements = []
            
            # Greedy matching
            while debtors and creditors:
                debt_amount, debtor = debtors[0]
                credit_amount, creditor = creditors[0]
                
                transfer = min(debt_amount, credit_amount)
                settlements.append({
                    "from_member": debtor,
                    "to_member": creditor,
                    "amount_paise": transfer,
                    "amount_rupees": transfer / 100
                })
                
                debtors[0][0] -= transfer
                creditors[0][0] -= transfer
                
                if debtors[0][0] == 0:
                    debtors.pop(0)
                if creditors[0][0] == 0:
                    creditors.pop(0)
            
            return {
                "status": "success",
                "settlements": settlements,
                "transfer_count": len(settlements),
                "total_amount_paise": sum(s["amount_paise"] for s in settlements),
                "total_amount_rupees": sum(s["amount_rupees"] for s in settlements)
            }
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    @staticmethod
    def analyze_split(amount_paise: int, num_participants: int) -> dict:
        """
        Analyze how an amount would be split
        
        Args:
            amount_paise: Amount to split in paise
            num_participants: Number of people sharing
        
        Returns:
            Detailed split breakdown
        """
        try:
            if num_participants <= 0:
                return {"status": "error", "message": "Invalid number of participants"}
            
            base_share = amount_paise // num_participants
            remainder = amount_paise % num_participants
            
            shares = []
            for i in range(num_participants):
                share = base_share + (1 if i < remainder else 0)
                shares.append({
                    "participant": i + 1,
                    "share_paise": share,
                    "share_rupees": share / 100
                })
            
            return {
                "status": "success",
                "total_amount_paise": amount_paise,
                "total_amount_rupees": amount_paise / 100,
                "num_participants": num_participants,
                "base_share_paise": base_share,
                "base_share_rupees": base_share / 100,
                "remainder_paise": remainder,
                "shares": shares,
                "fair_distribution": {
                    "explanation": f"First {remainder} participant(s) get +1 paise",
                    "ensures_total": f"Sum of shares = {sum(s['share_paise'] for s in shares)} paise"
                }
            }
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    @staticmethod
    def calculate_who_owes_whom(transactions: List[Dict]) -> dict:
        """
        Calculate detailed breakdown of who owes whom
        
        Args:
            transactions: List of transactions
        
        Returns:
            Detailed breakdown of debts
        """
        try:
            # Get balances
            balances_result = SplitEasyCalcServer.calculate_balances(transactions)
            if balances_result["status"] != "success":
                return balances_result
            
            balances = balances_result["balances_paise"]
            
            # Categorize members
            creditors = {k: v for k, v in balances.items() if v > 0}
            debtors = {k: -v for k, v in balances.items() if v < 0}
            settled = {k: v for k, v in balances.items() if v == 0}
            
            return {
                "status": "success",
                "gets_money_back": {
                    "members": [
                        {"name": k, "amount_paise": v, "amount_rupees": v/100}
                        for k, v in sorted(creditors.items(), key=lambda x: -x[1])
                    ],
                    "total_paise": sum(creditors.values()),
                    "total_rupees": sum(creditors.values()) / 100
                },
                "owes_money": {
                    "members": [
                        {"name": k, "amount_paise": v, "amount_rupees": v/100}
                        for k, v in sorted(debtors.items(), key=lambda x: -x[1])
                    ],
                    "total_paise": sum(debtors.values()),
                    "total_rupees": sum(debtors.values()) / 100
                },
                "settled_up": {
                    "members": list(settled.keys()),
                    "count": len(settled)
                }
            }
        except Exception as e:
            return {"status": "error", "message": str(e)}


# Tool definitions for MCP
TOOLS = {
    "calculate_balances": {
        "description": "Calculate net balance for each member from transactions",
        "parameters": {
            "transactions": {
                "type": "array",
                "description": "List of transactions with payer, amount_paise, and participants"
            }
        }
    },
    "settle_up": {
        "description": "Generate minimal settlement plan from balances",
        "parameters": {
            "balances": {
                "type": "object",
                "description": "Dict mapping member name to balance in paise"
            }
        }
    },
    "analyze_split": {
        "description": "Analyze how an amount would be split among participants",
        "parameters": {
            "amount_paise": {
                "type": "integer",
                "description": "Amount to split in paise"
            },
            "num_participants": {
                "type": "integer",
                "description": "Number of people sharing"
            }
        }
    },
    "calculate_who_owes_whom": {
        "description": "Get detailed breakdown of who owes whom",
        "parameters": {
            "transactions": {
                "type": "array",
                "description": "List of transactions"
            }
        }
    }
}


def main():
    """Run as standalone MCP server"""
    server = SplitEasyCalcServer()
    print("SplitEasy Calculation MCP Server")
    print("Available tools:", list(TOOLS.keys()))
    
    # Example usage
    print("\nExample 1: Analyze split of ₹100.01 among 3 people")
    result = server.analyze_split(10001, 3)
    print(json.dumps(result, indent=2))
    
    print("\nExample 2: Calculate balances from transactions")
    transactions = [
        {
            "payer": "Alice",
            "amount_paise": 30000,
            "participants": ["Alice", "Bob", "Charlie"]
        }
    ]
    result = server.calculate_balances(transactions)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
