#!/usr/bin/env python3
"""
MCP Server for SplitEasy Database Access
Provides tools to inspect and query the SQLite database
"""

import json
import sqlite3
from pathlib import Path
from typing import Any


class SplitEasyDBServer:
    """MCP Server for SplitEasy database operations"""
    
    def __init__(self, db_path: str = "spliteasys.db"):
        self.db_path = db_path
    
    def get_connection(self) -> sqlite3.Connection:
        """Get database connection"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    def list_groups(self) -> dict:
        """List all groups in the database"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute('SELECT id, name, created_at FROM groups ORDER BY created_at DESC')
            groups = [dict(row) for row in cursor.fetchall()]
            conn.close()
            return {"status": "success", "groups": groups}
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    def get_group_details(self, group_id: int) -> dict:
        """Get details of a specific group"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # Get group info
            cursor.execute('SELECT * FROM groups WHERE id = ?', (group_id,))
            group = dict(cursor.fetchone()) if cursor.fetchone() else None
            
            if not group:
                conn.close()
                return {"status": "error", "message": f"Group {group_id} not found"}
            
            # Get members count
            cursor.execute('SELECT COUNT(*) as count FROM members WHERE group_id = ?', (group_id,))
            member_count = cursor.fetchone()['count']
            
            # Get expenses count
            cursor.execute('SELECT COUNT(*) as count FROM expenses WHERE group_id = ?', (group_id,))
            expense_count = cursor.fetchone()['count']
            
            # Get total spent
            cursor.execute('SELECT SUM(amount_paise) as total FROM expenses WHERE group_id = ?', (group_id,))
            total_paise = cursor.fetchone()['total'] or 0
            
            conn.close()
            
            return {
                "status": "success",
                "group": group,
                "member_count": member_count,
                "expense_count": expense_count,
                "total_spent_paise": total_paise,
                "total_spent_rupees": total_paise / 100
            }
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    def get_group_members(self, group_id: int) -> dict:
        """Get all members of a group"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute(
                'SELECT id, name, created_at FROM members WHERE group_id = ? ORDER BY name',
                (group_id,)
            )
            members = [dict(row) for row in cursor.fetchall()]
            conn.close()
            return {"status": "success", "members": members, "count": len(members)}
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    def get_group_expenses(self, group_id: int) -> dict:
        """Get all expenses of a group"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute(
                '''SELECT e.id, e.payer_id, m.name as payer_name, e.amount_paise,
                   e.description, e.created_at
                   FROM expenses e
                   JOIN members m ON e.payer_id = m.id
                   WHERE e.group_id = ?
                   ORDER BY e.created_at DESC''',
                (group_id,)
            )
            expenses = [dict(row) for row in cursor.fetchall()]
            
            # Convert paise to rupees
            for exp in expenses:
                exp['amount_rupees'] = exp['amount_paise'] / 100
            
            conn.close()
            return {"status": "success", "expenses": expenses, "count": len(expenses)}
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    def database_stats(self) -> dict:
        """Get overall database statistics"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # Count totals
            cursor.execute('SELECT COUNT(*) as count FROM groups')
            group_count = cursor.fetchone()['count']
            
            cursor.execute('SELECT COUNT(*) as count FROM members')
            member_count = cursor.fetchone()['count']
            
            cursor.execute('SELECT COUNT(*) as count FROM expenses')
            expense_count = cursor.fetchone()['count']
            
            cursor.execute('SELECT SUM(amount_paise) as total FROM expenses')
            total_paise = cursor.fetchone()['total'] or 0
            
            conn.close()
            
            return {
                "status": "success",
                "groups": group_count,
                "members": member_count,
                "expenses": expense_count,
                "total_amount_paise": total_paise,
                "total_amount_rupees": total_paise / 100
            }
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    def export_group_json(self, group_id: int) -> dict:
        """Export complete group data as JSON"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # Get group
            cursor.execute('SELECT * FROM groups WHERE id = ?', (group_id,))
            group = dict(cursor.fetchone()) if cursor.fetchone() else None
            
            if not group:
                conn.close()
                return {"status": "error", "message": f"Group {group_id} not found"}
            
            # Get members
            cursor.execute('SELECT * FROM members WHERE group_id = ? ORDER BY name', (group_id,))
            members = [dict(row) for row in cursor.fetchall()]
            
            # Get expenses with participants
            cursor.execute(
                '''SELECT e.*, m.name as payer_name
                   FROM expenses e
                   JOIN members m ON e.payer_id = m.id
                   WHERE e.group_id = ?
                   ORDER BY e.created_at''',
                (group_id,)
            )
            expenses = [dict(row) for row in cursor.fetchall()]
            
            # Get participants for each expense
            for exp in expenses:
                cursor.execute(
                    '''SELECT m.id, m.name FROM expense_participants ep
                       JOIN members m ON ep.member_id = m.id
                       WHERE ep.expense_id = ?''',
                    (exp['id'],)
                )
                exp['participants'] = [dict(row) for row in cursor.fetchall()]
                exp['amount_rupees'] = exp['amount_paise'] / 100
            
            conn.close()
            
            export_data = {
                "group": group,
                "members": members,
                "expenses": expenses
            }
            
            return {"status": "success", "data": export_data}
        except Exception as e:
            return {"status": "error", "message": str(e)}


# Tool definitions for MCP
TOOLS = {
    "list_groups": {
        "description": "List all groups in SplitEasy",
        "parameters": {}
    },
    "get_group_details": {
        "description": "Get detailed information about a specific group",
        "parameters": {
            "group_id": {
                "type": "integer",
                "description": "ID of the group"
            }
        }
    },
    "get_group_members": {
        "description": "Get all members in a group",
        "parameters": {
            "group_id": {
                "type": "integer",
                "description": "ID of the group"
            }
        }
    },
    "get_group_expenses": {
        "description": "Get all expenses for a group",
        "parameters": {
            "group_id": {
                "type": "integer",
                "description": "ID of the group"
            }
        }
    },
    "database_stats": {
        "description": "Get overall database statistics",
        "parameters": {}
    },
    "export_group_json": {
        "description": "Export complete group data as JSON",
        "parameters": {
            "group_id": {
                "type": "integer",
                "description": "ID of the group to export"
            }
        }
    }
}


def main():
    """Run as standalone MCP server"""
    server = SplitEasyDBServer()
    print("SplitEasy Database MCP Server")
    print("Available tools:", list(TOOLS.keys()))
    print("\nExample usage:")
    print("  python3 spliteasys_db_server.py")
    print("\nDatabase stats:")
    print(json.dumps(server.database_stats(), indent=2))


if __name__ == "__main__":
    main()
