"""Streamlit UI for SplitEasy - all UI logic, no business logic."""

import streamlit as st
from splitter.db import Database
from splitter.core import calculate_balances, settle_up, format_rupees


def init_db():
    """Initialize database in session state."""
    if 'db' not in st.session_state:
        st.session_state.db = Database()


def main():
    """Main Streamlit app."""
    st.set_page_config(page_title="SplitEasy", layout="wide")
    st.title("💰 SplitEasy")
    st.markdown("_Split expenses fairly among friends_")
    
    init_db()
    db = st.session_state.db
    
    # Sidebar for navigation
    page = st.sidebar.radio(
        "Navigation",
        ["Create Group", "Manage Group", "View Settlements"]
    )
    
    if page == "Create Group":
        create_group_page(db)
    elif page == "Manage Group":
        manage_group_page(db)
    elif page == "View Settlements":
        view_settlements_page(db)


def create_group_page(db: Database):
    """Page to create a new group."""
    st.header("Create a New Group")
    
    col1, col2 = st.columns([3, 1])
    with col1:
        group_name = st.text_input("Group Name", placeholder="e.g., Hostel Trip")
    with col2:
        if st.button("Create", use_container_width=True):
            if group_name.strip():
                group_id = db.create_group(group_name)
                st.success(f"✅ Group '{group_name}' created!")
                st.balloons()
                st.session_state.current_group_id = group_id
            else:
                st.error("Please enter a group name")
    
    # List existing groups
    st.subheader("Existing Groups")
    groups = db.list_groups()
    if groups:
        for group in groups:
            if st.button(group['name'], key=f"select_{group['id']}", use_container_width=True):
                st.session_state.current_group_id = group['id']
                st.rerun()
    else:
        st.info("No groups yet. Create one above!")


def manage_group_page(db: Database):
    """Page to manage a group's members and expenses."""
    groups = db.list_groups()
    if not groups:
        st.warning("No groups exist. Create one first!")
        return
    
    # Select group
    group_id = st.selectbox(
        "Select Group",
        options=[g['id'] for g in groups],
        format_func=lambda gid: next(g['name'] for g in groups if g['id'] == gid)
    )
    
    group = db.get_group(group_id)
    st.header(f"📝 {group['name']}")
    
    # Tabs for different operations
    tab1, tab2, tab3 = st.tabs(["Members", "Add Expense", "Expenses"])
    
    with tab1:
        manage_members_tab(db, group_id)
    
    with tab2:
        add_expense_tab(db, group_id)
    
    with tab3:
        view_expenses_tab(db, group_id)


def manage_members_tab(db: Database, group_id: int):
    """Tab to view and add members."""
    st.subheader("Members")
    
    col1, col2 = st.columns([3, 1])
    with col1:
        member_name = st.text_input("Add Member", placeholder="Enter member name", key="new_member")
    with col2:
        if st.button("Add", use_container_width=True):
            if member_name.strip():
                db.add_member(group_id, member_name)
                st.success(f"✅ Added {member_name}")
                st.rerun()
            else:
                st.error("Please enter a name")
    
    members = db.get_members(group_id)
    if members:
        st.write("Current members:")
        for member in members:
            st.write(f"• {member['name']}")
    else:
        st.info("No members yet. Add one above!")


def add_expense_tab(db: Database, group_id: int):
    """Tab to add a new expense."""
    st.subheader("Add Expense")
    
    members = db.get_members(group_id)
    if not members:
        st.warning("Add members to the group first!")
        return
    
    col1, col2 = st.columns(2)
    with col1:
        payer = st.selectbox(
            "Who paid?",
            options=[m['id'] for m in members],
            format_func=lambda mid: next(m['name'] for m in members if m['id'] == mid)
        )
    with col2:
        amount_rupees = st.number_input("Amount (₹)", min_value=0.01, step=0.01, value=100.00)
    
    description = st.text_input("Description", placeholder="e.g., Dinner")
    
    # Select participants
    participant_ids = st.multiselect(
        "Who shares this expense?",
        options=[m['id'] for m in members],
        format_func=lambda mid: next(m['name'] for m in members if m['id'] == mid),
        default=[m['id'] for m in members]
    )
    
    if st.button("Add Expense", type="primary", use_container_width=True):
        if not participant_ids:
            st.error("Select at least one participant")
        else:
            amount_paise = int(amount_rupees * 100)
            db.add_expense(group_id, payer, amount_paise, participant_ids, description)
            st.success("✅ Expense added!")
            st.rerun()


def view_expenses_tab(db: Database, group_id: int):
    """Tab to view all expenses."""
    st.subheader("Expenses")
    
    expenses = db.get_expenses(group_id)
    if not expenses:
        st.info("No expenses yet.")
        return
    
    for expense in expenses:
        col1, col2, col3 = st.columns([2, 1, 2])
        with col1:
            st.write(f"**{expense['description'] or 'Expense'}**")
            st.write(f"Paid by: {expense['payer_name']}")
        with col2:
            st.write(f"Amount: {format_rupees(expense['amount_paise'])}")
        with col3:
            participants = ", ".join(p['name'] for p in expense['participants'])
            st.write(f"Shared by: {participants}")
        st.divider()


def view_settlements_page(db: Database):
    """Page to view balances and settlement plan."""
    groups = db.list_groups()
    if not groups:
        st.warning("No groups exist. Create one first!")
        return
    
    group_id = st.selectbox(
        "Select Group",
        options=[g['id'] for g in groups],
        format_func=lambda gid: next(g['name'] for g in groups if g['id'] == gid)
    )
    
    group = db.get_group(group_id)
    st.header(f"💳 Settlements - {group['name']}")
    
    expenses = db.get_expenses(group_id)
    members = db.get_members(group_id)
    
    if not expenses:
        st.info("No expenses yet. Add some to see settlements.")
        return
    
    # Convert DB format to core.py format
    transactions = []
    for exp in expenses:
        transactions.append({
            'payer': exp['payer_name'],
            'amount_paise': exp['amount_paise'],
            'participants': [p['name'] for p in exp['participants']]
        })
    
    # Calculate balances
    balances = calculate_balances(transactions)
    
    # Show balances
    st.subheader("Member Balances")
    col1, col2, col3 = st.columns(3)
    
    owed_money = []  # (name, amount)
    owes_money = []  # (name, amount)
    
    for member_name in sorted(balances.keys()):
        balance = balances[member_name]
        if balance > 0:
            owed_money.append((member_name, balance))
        elif balance < 0:
            owes_money.append((member_name, -balance))
    
    with col1:
        st.write("**Gets Money Back:**")
        if owed_money:
            for name, amount in owed_money:
                st.write(f"• {name}: {format_rupees(amount)}")
        else:
            st.info("None")
    
    with col2:
        st.write("**Owes Money:**")
        if owes_money:
            for name, amount in owes_money:
                st.write(f"• {name}: {format_rupees(amount)}")
        else:
            st.info("None")
    
    with col3:
        st.write("**Settled Up:**")
        settled = [m for m in balances if balances[m] == 0]
        if settled:
            for name in settled:
                st.write(f"• {name}")
        else:
            st.info("None")
    
    # Show settlement plan
    st.subheader("Settlement Plan")
    settlements = settle_up(balances)
    
    if settlements:
        st.markdown("**Make these transfers to settle all debts:**")
        for i, settlement in enumerate(settlements, 1):
            st.write(
                f"{i}. **{settlement.from_member}** → **{settlement.to_member}**: "
                f"{format_rupees(settlement.amount_paise)}"
            )
    else:
        st.success("✅ All settled up! No transfers needed.")


if __name__ == "__main__":
    main()
