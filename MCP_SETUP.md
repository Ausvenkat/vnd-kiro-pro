# SplitEasy MCP Server Setup Guide

## Overview

Two custom MCP servers have been created for SplitEasy to provide database access and calculation tools through Kiro:

1. **spliteasys-database** - Database inspection and querying
2. **spliteasys-calculations** - Balance calculation and settlement planning

---

## MCP Servers Created

### 1. Database MCP Server (`.kiro/mcp_servers/spliteasys_db_server.py`)

**Purpose:** Inspect and query the SplitEasy SQLite database

**Available Tools:**

- `list_groups` - List all groups
- `get_group_details` - Get details of a specific group
- `get_group_members` - Get all members in a group
- `get_group_expenses` - Get all expenses for a group
- `database_stats` - Get overall database statistics
- `export_group_json` - Export complete group data as JSON

**Example Usage:**
```python
from .kiro.mcp_servers.spliteasys_db_server import SplitEasyDBServer

server = SplitEasyDBServer("spliteasys.db")
groups = server.list_groups()
print(groups)
```

### 2. Calculations MCP Server (`.kiro/mcp_servers/spliteasys_calc_server.py`)

**Purpose:** Calculate balances and settlement plans

**Available Tools:**

- `calculate_balances` - Calculate net balance for each member
- `settle_up` - Generate minimal settlement plan
- `analyze_split` - Analyze how an amount would be split
- `calculate_who_owes_whom` - Detailed breakdown of debts

**Example Usage:**
```python
from .kiro.mcp_servers.spliteasys_calc_server import SplitEasyCalcServer

server = SplitEasyCalcServer()
transactions = [
    {
        "payer": "Alice",
        "amount_paise": 30000,
        "participants": ["Alice", "Bob", "Charlie"]
    }
]
balances = server.calculate_balances(transactions)
print(balances)
```

---

## How to Configure MCP in Kiro

### Step 1: Create `.kiro/settings/mcp.json`

**File Location:** `.kiro/settings/mcp.json` (in workspace root)

**Note:** You may need to create the `.kiro/settings/` directory first if it doesn't exist.

### Step 2: Add Server Configuration

Copy this configuration into `.kiro/settings/mcp.json`:

```json
{
  "mcpServers": {
    "spliteasys-database": {
      "command": "python3",
      "args": [".kiro/mcp_servers/spliteasys_db_server.py"],
      "env": {
        "PYTHONPATH": "."
      },
      "disabled": false,
      "description": "Database access and inspection tools for SplitEasy"
    },
    "spliteasys-calculations": {
      "command": "python3",
      "args": [".kiro/mcp_servers/spliteasys_calc_server.py"],
      "env": {
        "PYTHONPATH": "."
      },
      "disabled": false,
      "description": "Balance calculation and settlement planning tools for SplitEasy"
    }
  }
}
```

### Step 3: Restart Kiro

- Close current Kiro session
- Restart Kiro
- Servers should connect automatically

### Step 4: Verify MCP Servers

Check the MCP Server view in Kiro to see:
- ✅ spliteasys-database (connected)
- ✅ spliteasys-calculations (connected)

---

## MCP Server Details

### Database Server: `spliteasys-database`

**Configuration:**
```json
{
  "command": "python3",
  "args": [".kiro/mcp_servers/spliteasys_db_server.py"],
  "env": {
    "PYTHONPATH": "."
  },
  "disabled": false
}
```

**Tools Provided:**

1. **list_groups**
   - Lists all groups in database
   - Returns: Array of group objects

2. **get_group_details(group_id)**
   - Get details of specific group
   - Returns: Group info, member count, expense count, total spent

3. **get_group_members(group_id)**
   - Get all members in group
   - Returns: Array of member objects

4. **get_group_expenses(group_id)**
   - Get all expenses for group
   - Returns: Array of expense objects (with amounts in both paise and rupees)

5. **database_stats**
   - Overall database statistics
   - Returns: Total groups, members, expenses, total amount

6. **export_group_json(group_id)**
   - Export complete group data
   - Returns: JSON with group, members, and expenses

---

### Calculations Server: `spliteasys-calculations`

**Configuration:**
```json
{
  "command": "python3",
  "args": [".kiro/mcp_servers/spliteasys_calc_server.py"],
  "env": {
    "PYTHONPATH": "."
  },
  "disabled": false
}
```

**Tools Provided:**

1. **calculate_balances(transactions)**
   - Calculate net balance for each member
   - Input: Array of transactions
   - Returns: Balances in both paise and rupees

2. **settle_up(balances)**
   - Generate minimal settlement plan
   - Input: Balance dict
   - Returns: Array of settlements with transfer count

3. **analyze_split(amount_paise, num_participants)**
   - Analyze how amount splits
   - Shows fair remainder distribution
   - Returns: Detailed split breakdown

4. **calculate_who_owes_whom(transactions)**
   - Detailed breakdown of debts
   - Returns: Creditors, debtors, settled members

---

## Files Created

```
.kiro/mcp_servers/
├── spliteasys_db_server.py         Database access server
└── spliteasys_calc_server.py       Calculation server

.kiro/settings/
└── mcp.json                        MCP configuration (create manually)
```

---

## Manual MCP Configuration

### Option 1: Using Kiro Settings UI

1. Open Kiro
2. Go to Settings → MCP Servers
3. Add two new servers:
   - **spliteasys-database**
   - **spliteasys-calculations**
4. Configure as shown above

### Option 2: Using mcp.json File

1. Create `.kiro/settings/mcp.json` in workspace
2. Add the configuration shown above
3. Restart Kiro

### Option 3: User-Level Configuration

For user-level MCP config (shared across workspaces):

1. Create `~/.kiro/settings/mcp.json` in home directory
2. Add configuration
3. Restart Kiro

**Note:** Workspace config overrides user config

---

## Testing MCP Servers

### Test Database Server

```bash
# From project root
python3 .kiro/mcp_servers/spliteasys_db_server.py
```

Expected output:
```
SplitEasy Database MCP Server
Available tools: ['list_groups', 'get_group_details', 'get_group_members', 'get_group_expenses', 'database_stats', 'export_group_json']

Database stats:
{
  "status": "success",
  "groups": 0,
  "members": 0,
  "expenses": 0,
  "total_amount_paise": 0,
  "total_amount_rupees": 0.0
}
```

### Test Calculations Server

```bash
# From project root
python3 .kiro/mcp_servers/spliteasys_calc_server.py
```

Expected output:
```
SplitEasy Calculation MCP Server
Available tools: ['calculate_balances', 'settle_up', 'analyze_split', 'calculate_who_owes_whom']

Example 1: Analyze split of ₹100.01 among 3 people
{
  "status": "success",
  "total_amount_paise": 10001,
  ...
}
```

---

## Using MCP Tools from Kiro

Once configured, you can use MCP tools in Kiro:

### Example 1: Query Database

```
Kiro Prompt: "Get database statistics"
→ Kiro calls: spliteasys-database.database_stats()
→ Returns: Total groups, members, expenses, amounts
```

### Example 2: Calculate Settlement

```
Kiro Prompt: "Calculate settlement plan for these balances..."
→ Kiro calls: spliteasys-calculations.settle_up()
→ Returns: Minimal transfers needed
```

### Example 3: Analyze Expense Split

```
Kiro Prompt: "How would ₹1500 split among 4 people?"
→ Kiro calls: spliteasys-calculations.analyze_split(150000, 4)
→ Returns: Fair split breakdown
```

---

## MCP Server Architecture

```
Kiro IDE
   ↓
MCP Client (built-in)
   ↓
┌─────────────────────────────────┐
│  MCP Servers                    │
├─────────────────────────────────┤
│ spliteasys-database             │
│  ├─ list_groups()               │
│  ├─ get_group_details()         │
│  ├─ get_group_members()         │
│  ├─ get_group_expenses()        │
│  ├─ database_stats()            │
│  └─ export_group_json()         │
├─────────────────────────────────┤
│ spliteasys-calculations         │
│  ├─ calculate_balances()        │
│  ├─ settle_up()                 │
│  ├─ analyze_split()             │
│  └─ calculate_who_owes_whom()   │
└─────────────────────────────────┘
   ↓
SplitEasy Application
   ├─ Database (SQLite)
   ├─ Core Logic (Python)
   └─ UI (Streamlit)
```

---

## Configuration Summary

### Database Server

**What it does:** Inspects and queries the SplitEasy database

**Commands:** 6 tools for database access

**Use cases:**
- List all groups
- View group details
- Export group data
- Get database statistics

### Calculations Server

**What it does:** Calculates balances and settlement plans

**Commands:** 4 tools for calculations

**Use cases:**
- Calculate member balances
- Generate settlement plans
- Analyze expense splits
- Breakdown debts

---

## Next Steps

1. ✅ MCP server files created (.kiro/mcp_servers/)
2. Create `.kiro/settings/mcp.json` with configuration
3. Restart Kiro to activate servers
4. Test MCP tools
5. Commit to Git

---

## Troubleshooting

### MCP Servers Not Connecting

1. Check `.kiro/settings/mcp.json` exists
2. Verify file syntax is valid JSON
3. Restart Kiro
4. Check MCP Server view

### Python Import Errors

1. Ensure PYTHONPATH is set to "."
2. Check Python version is 3.11+
3. Verify splitter package exists

### Server Commands Not Working

1. Test server directly: `python3 .kiro/mcp_servers/spliteasys_db_server.py`
2. Check database file exists: `spliteasys.db`
3. Verify permissions on .kiro/mcp_servers/ directory

---

## References

- [Kiro MCP Documentation](https://kiro.dev)
- [Model Context Protocol](https://modelcontextprotocol.io)
- [SplitEasy Documentation](README.md)

---

**MCP Servers ready to configure and use!** 🚀
