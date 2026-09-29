"""SQLite database access for SplitEasy."""

import sqlite3
from typing import List, Dict, Optional, Tuple
from pathlib import Path


class Database:
    """SQLite database manager for SplitEasy."""
    
    def __init__(self, db_path: str = "spliteasys.db"):
        """Initialize database connection."""
        self.db_path = db_path
        self._ensure_tables()
    
    def _get_connection(self) -> sqlite3.Connection:
        """Get database connection."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    def _ensure_tables(self) -> None:
        """Create tables if they don't exist."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        # Groups table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS groups (
                id INTEGER PRIMARY KEY,
                name TEXT UNIQUE NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Members table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS members (
                id INTEGER PRIMARY KEY,
                group_id INTEGER NOT NULL,
                name TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (group_id) REFERENCES groups(id),
                UNIQUE(group_id, name)
            )
        ''')
        
        # Expenses table (stores who paid, amount, and which members share)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS expenses (
                id INTEGER PRIMARY KEY,
                group_id INTEGER NOT NULL,
                payer_id INTEGER NOT NULL,
                amount_paise INTEGER NOT NULL,
                description TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (group_id) REFERENCES groups(id),
                FOREIGN KEY (payer_id) REFERENCES members(id)
            )
        ''')
        
        # Expense participants (many-to-many: which members share an expense)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS expense_participants (
                id INTEGER PRIMARY KEY,
                expense_id INTEGER NOT NULL,
                member_id INTEGER NOT NULL,
                FOREIGN KEY (expense_id) REFERENCES expenses(id),
                FOREIGN KEY (member_id) REFERENCES members(id),
                UNIQUE(expense_id, member_id)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    # Group operations
    def create_group(self, name: str) -> int:
        """Create a new group. Returns group_id."""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute('INSERT INTO groups (name) VALUES (?)', (name,))
        conn.commit()
        group_id = cursor.lastrowid
        conn.close()
        return group_id
    
    def get_group(self, group_id: int) -> Optional[Dict]:
        """Get group by ID."""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM groups WHERE id = ?', (group_id,))
        row = cursor.fetchone()
        conn.close()
        return dict(row) if row else None
    
    def get_group_by_name(self, name: str) -> Optional[Dict]:
        """Get group by name."""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM groups WHERE name = ?', (name,))
        row = cursor.fetchone()
        conn.close()
        return dict(row) if row else None
    
    def list_groups(self) -> List[Dict]:
        """List all groups."""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM groups ORDER BY created_at DESC')
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]
    
    # Member operations
    def add_member(self, group_id: int, name: str) -> int:
        """Add member to group. Returns member_id."""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute(
            'INSERT INTO members (group_id, name) VALUES (?, ?)',
            (group_id, name)
        )
        conn.commit()
        member_id = cursor.lastrowid
        conn.close()
        return member_id
    
    def get_members(self, group_id: int) -> List[Dict]:
        """Get all members of a group."""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute(
            'SELECT * FROM members WHERE group_id = ? ORDER BY name',
            (group_id,)
        )
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]
    
    def get_member(self, member_id: int) -> Optional[Dict]:
        """Get member by ID."""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM members WHERE id = ?', (member_id,))
        row = cursor.fetchone()
        conn.close()
        return dict(row) if row else None
    
    # Expense operations
    def add_expense(
        self,
        group_id: int,
        payer_id: int,
        amount_paise: int,
        participant_ids: List[int],
        description: str = ""
    ) -> int:
        """Add expense and participant splits. Returns expense_id."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        # Insert expense
        cursor.execute(
            '''INSERT INTO expenses (group_id, payer_id, amount_paise, description)
               VALUES (?, ?, ?, ?)''',
            (group_id, payer_id, amount_paise, description)
        )
        expense_id = cursor.lastrowid
        
        # Insert participants
        for member_id in participant_ids:
            cursor.execute(
                '''INSERT INTO expense_participants (expense_id, member_id)
                   VALUES (?, ?)''',
                (expense_id, member_id)
            )
        
        conn.commit()
        conn.close()
        return expense_id
    
    def get_expenses(self, group_id: int) -> List[Dict]:
        """Get all expenses for a group with participant details."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        # Get expenses
        cursor.execute(
            '''SELECT e.*, m.name as payer_name
               FROM expenses e
               JOIN members m ON e.payer_id = m.id
               WHERE e.group_id = ?
               ORDER BY e.created_at DESC''',
            (group_id,)
        )
        expenses = [dict(row) for row in cursor.fetchall()]
        
        # Get participants for each expense
        for expense in expenses:
            cursor.execute(
                '''SELECT m.id, m.name
                   FROM expense_participants ep
                   JOIN members m ON ep.member_id = m.id
                   WHERE ep.expense_id = ?''',
                (expense['id'],)
            )
            expense['participants'] = [
                {'id': row['id'], 'name': row['name']}
                for row in cursor.fetchall()
            ]
        
        conn.close()
        return expenses
    
    def clear_all(self) -> None:
        """Clear all data (for testing)."""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM expense_participants')
        cursor.execute('DELETE FROM expenses')
        cursor.execute('DELETE FROM members')
        cursor.execute('DELETE FROM groups')
        conn.commit()
        conn.close()
