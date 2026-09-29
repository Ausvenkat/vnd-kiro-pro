"""Tests for core balance and settlement logic."""

import pytest
from splitter.core import calculate_balances, settle_up, Settlement


class TestCalculateBalances:
    """Test balance calculation."""
    
    def test_simple_equal_split(self):
        """Test simple case where amount divides evenly."""
        transactions = [
            {
                'payer': 'Alice',
                'amount_paise': 30000,  # ₹300
                'participants': ['Alice', 'Bob', 'Charlie']
            }
        ]
        balances = calculate_balances(transactions)
        
        # Alice paid 300, owes 100 (for 1/3)
        assert balances['Alice'] == 20000  # ₹200 owed to her
        assert balances['Bob'] == -10000   # ₹100 owes
        assert balances['Charlie'] == -10000  # ₹100 owes
    
    def test_uneven_split_with_remainder(self):
        """Test that remainder paise are distributed fairly."""
        transactions = [
            {
                'payer': 'Alice',
                'amount_paise': 10000,  # ₹100
                'participants': ['Alice', 'Bob', 'Charlie']
            }
        ]
        balances = calculate_balances(transactions)
        
        # 100 ÷ 3 = 33 + 1/3
        # Alice gets 100 and owes 33.34 → (balance = 66.66)
        # Bob gets 33.33 → (balance = -33.33)
        # Charlie gets 33.33 → (balance = -33.33)
        
        # With remainder distribution: first member gets +1
        # Shares: 34, 33, 33
        assert balances['Alice'] == 10000 - 3334  # owes 33.34
        assert balances['Bob'] == -3333  # is owed 33.33
        assert balances['Charlie'] == -3333  # is owed 33.33
    
    def test_multiple_expenses(self):
        """Test with multiple expenses."""
        transactions = [
            {
                'payer': 'Alice',
                'amount_paise': 30000,
                'participants': ['Alice', 'Bob']
            },
            {
                'payer': 'Bob',
                'amount_paise': 20000,
                'participants': ['Alice', 'Bob']
            }
        ]
        balances = calculate_balances(transactions)
        
        # Alice: paid 300, owes 150+100 = 250 → balance = 50
        # Bob: paid 200, owes 150+100 = 250 → balance = -50
        assert balances['Alice'] == 5000
        assert balances['Bob'] == -5000
    
    def test_single_payer_no_split(self):
        """Test expense only paid by one person (edge case)."""
        transactions = [
            {
                'payer': 'Alice',
                'amount_paise': 10000,
                'participants': ['Alice']
            }
        ]
        balances = calculate_balances(transactions)
        
        # Alice paid and is the only participant, so balanced
        assert balances['Alice'] == 0
    
    def test_three_person_uneven_split(self):
        """Test three-way split with remainder."""
        transactions = [
            {
                'payer': 'Alice',
                'amount_paise': 10001,  # ₹100.01
                'participants': ['Alice', 'Bob', 'Charlie']
            }
        ]
        balances = calculate_balances(transactions)
        
        # 10001 ÷ 3 = 3333 remainder 2
        # Shares: 3334, 3334, 3333 (first two get +1)
        # Alice paid 10001, received 3334 → owes 6667
        assert balances['Alice'] == 10001 - 3334
        assert balances['Bob'] == -3334
        assert balances['Charlie'] == -3333


class TestSettleUp:
    """Test settlement plan generation."""
    
    def test_simple_settlement(self):
        """Test simple two-person settlement."""
        balances = {'Alice': 5000, 'Bob': -5000}
        settlements = settle_up(balances)
        
        assert len(settlements) == 1
        assert settlements[0].from_member == 'Bob'
        assert settlements[0].to_member == 'Alice'
        assert settlements[0].amount_paise == 5000
    
    def test_three_person_chain(self):
        """Test settling a chain of debts."""
        # Alice is owed 100, Bob owes 60, Charlie owes 40
        balances = {'Alice': 10000, 'Bob': -6000, 'Charlie': -4000}
        settlements = settle_up(balances)
        
        assert len(settlements) == 2
        assert sum(s.amount_paise for s in settlements) == 10000
    
    def test_balanced_group(self):
        """Test when group is already balanced."""
        balances = {'Alice': 0, 'Bob': 0}
        settlements = settle_up(balances)
        
        assert len(settlements) == 0
    
    def test_complex_settlement(self):
        """Test complex settlement scenario."""
        balances = {
            'Alice': 10000,    # owed 100
            'Bob': -5000,      # owes 50
            'Charlie': -3000,  # owes 30
            'Dave': -2000      # owes 20
        }
        settlements = settle_up(balances)
        
        # Should settle with minimal transfers
        assert len(settlements) <= 3
        total_settled = sum(s.amount_paise for s in settlements)
        assert total_settled == 10000
    
    def test_settlement_reduces_transfers(self):
        """Test that settlement minimizes transfers."""
        # Without settling: A owes B 30, A owes C 30, A owes D 40
        # That's 3 transfers. Settlement should do it in fewer.
        balances = {
            'A': 10000,    # owed 100
            'B': -3000,    # owes 30
            'C': -3000,    # owes 30
            'D': -4000     # owes 40
        }
        settlements = settle_up(balances)
        
        assert len(settlements) == 3  # Minimal transfers


class TestEdgeCases:
    """Test edge cases and special scenarios."""
    
    def test_zero_balance(self):
        """Test with only zero balances."""
        balances = {'Alice': 0, 'Bob': 0}
        settlements = settle_up(balances)
        
        assert len(settlements) == 0
    
    def test_single_member(self):
        """Test with single member."""
        transactions = [
            {
                'payer': 'Alice',
                'amount_paise': 10000,
                'participants': ['Alice']
            }
        ]
        balances = calculate_balances(transactions)
        settlements = settle_up(balances)
        
        assert len(settlements) == 0


class TestRemainderDistribution:
    """Test fair distribution of remainder paise."""
    
    def test_remainder_goes_to_first_members(self):
        """Test that remainder paise go to first members."""
        transactions = [
            {
                'payer': 'Alice',
                'amount_paise': 10001,  # 3333.67 per person
                'participants': ['A', 'B', 'C']
            }
        ]
        balances = calculate_balances(transactions)
        
        # A and B should owe 3334, C should owe 3333
        # (remaining 1 paise distributed to first participant)
        assert balances['Alice'] == 10001 - 3334
        assert balances['B'] == -3334
        assert balances['C'] == -3333
    
    def test_large_remainder_distribution(self):
        """Test distribution with larger remainder."""
        transactions = [
            {
                'payer': 'Alice',
                'amount_paise': 10005,  # 3 remainder paise
                'participants': ['A', 'B', 'C', 'D']
            }
        ]
        balances = calculate_balances(transactions)
        
        # 10005 ÷ 4 = 2501 remainder 1
        # First participant gets +1
        assert balances['A'] == 10005 - 2502
        assert balances['B'] == -2501
        assert balances['C'] == -2501
        assert balances['D'] == -2501


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
