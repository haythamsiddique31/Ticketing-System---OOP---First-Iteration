🎫 OOP Ticketing System
A clean, single-file ticketing system demonstrating:
- Inheritance (BaseUser → Customer/Agent/Admin)
- Factory pattern (Admin.create_user)
- Encapsulation (private methods, properties)
- State management (ticket lifecycle)
- Type hints throughout
"""

from datetime import datetime
from enum import Enum, auto
from typing import Optional, List, Dict


# ============================================================
# ENUMS - "pick from these options only"
# ============================================================

class Status(Enum):
    """Ticket states. OPEN → IN_PROGRESS → RESOLVED/CLOSED."""
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    ON_HOLD = "on_hold"
    RESOLVED = "resolved"
    CLOSED = "closed"


class Priority(Enum):
    """Priority levels with numeric values for sorting."""
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4
    NATIONAL = 5


class Category(Enum):
    """What type of problem is this?"""
    IT = "IT Support"
    BILLING = "Billing"
    GENERAL = "General"


# ============================================================
# USER HIERARCHY (Inheritance)
# ============================================================

class BaseUser:
    """
    Parent class - all users share these basics.

    _next_id is a CLASS variable (shared by ALL users).
    It auto-increments so every user gets a unique ID.
    """
    _next_id = 1

    def __init__(self, name: str, email: str, role: str):
        self.id = BaseUser._next_id
        BaseUser._next_id += 1
        self.name = name
        self.email = email
        self.role = role
        self.created_at = datetime.now()

    def __str__(self) -> str:
        return f"{self.name} ({self.role})"

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(id={self.id}, name={self.name!r})"


class Customer(BaseUser):
    """
    A customer who can create tickets and view their own.

    Factory method: create_ticket() makes a new Ticket and
    automatically links it to this customer.
    """

    def __init__(self, name: str, email: str):
        super().__init__(name, email, "customer")
        self._tickets: List[Ticket] = []

    @property
    def tickets(self) -> List["Ticket"]:
        """Read-only access to this customer's tickets."""
        return self._tickets.copy()

    def create_ticket(
        self,
        title: str,
        description: str,
        priority: Priority = Priority.MEDIUM,
        category: Category = Category.GENERAL
    ) -> "Ticket":
        """Factory: create a ticket linked to this customer."""
        ticket = Ticket(title, description, self, priority, category)
        self._tickets.append(ticket)
        print(f"✅ {self.name} created ticket #{ticket.id}: {title}")
        return ticket

    def view_my_tickets(self) -> None:
        """Display all tickets this customer created."""
        if not self._tickets:
            print(f"\n📭 {self.name} has no tickets.")
            return

        print(f"\n📋 Tickets for {self.name}:")
        for ticket in self._tickets:
            emoji = {
                Status.OPEN: "red_circle",
                Status.IN_PROGRESS: "yellow_circle",
                Status.RESOLVED: "green_circle",
                Status.CLOSED: "black_circle"
            }.get(ticket.status, "white_circle")
            print(f"   {emoji} #{ticket.id}: {ticket.title} [{ticket.status.value}]")


class Agent(BaseUser):
    """
    Support agent who can claim and resolve tickets.

    Tracks their own workload and resolution stats.
    """

    def __init__(self, name: str, email: str, department: str = "General"):
        super().__init__(name, email, "agent")
        self.department = department
        self._assigned: List[Ticket] = []
        self._resolved_count = 0

    @property
    def assigned_tickets(self) -> List["Ticket"]:
        """Currently active tickets assigned to this agent."""
        return [t for t in self._assigned if t.status == Status.IN_PROGRESS]

    @property
    def resolved_count(self) -> int:
        """Total tickets this agent has resolved."""
        return self._resolved_count

    def claim_ticket(self, ticket: "Ticket") -> bool:
        """Take ownership of an OPEN ticket."""
        if ticket.status != Status.OPEN:
            print(f"❌ Ticket #{ticket.id} is not available (status: {ticket.status.value})")
            return False

        ticket._set_agent(self)
        self._assigned.append(ticket)
        ticket._add_comment(f"Claimed by {self.name}", self)
        print(f"✅ {self.name} claimed ticket #{ticket.id}")
        return True

    def resolve_ticket(self, ticket: "Ticket", solution: str) -> bool:
        """Mark a ticket as resolved with solution notes."""
        if ticket not in self._assigned:
            print(f"❌ {self.name} cannot resolve ticket #{ticket.id} — not assigned")
            return False

        if ticket.status != Status.IN_PROGRESS:
            print(f"❌ Ticket #{ticket.id} is not in progress")
            return False

        ticket._resolve(solution)
        self._resolved_count += 1
        ticket._add_comment(f"Resolved: {solution}", self)
        print(f"✅ {self.name} resolved ticket #{ticket.id}")
        return True

    def get_workload(self) -> str:
        """Quick summary of current workload."""
        active = len(self.assigned_tickets)
        return f"{self.name}: {active} active, {self._resolved_count} resolved"


class Admin(BaseUser):
    """
    System administrator with full control, admin privileges, etc.

    Can create any type of user (Factory pattern) and
    force-close any ticket.
    """

    def __init__(self, name: str, email: str):
        super().__init__(name, email, "admin")
        self._users_created = 0
        self._tickets_closed = 0

    def create_user(self, user_type: str, name: str, email: str, **kwargs) -> BaseUser:
        """
        Factory: create any type of user, like a customer, agent, or admin.

        Args:
            user_type: "customer", "agent", or "admin"
            name: user's name
            email: user's email
            **kwargs: extra args (e.g., department="IT" for agents)

        Returns:
            The newly created user object
        """
        self._users_created += 1

        if user_type == "customer":
            return Customer(name, email)
        elif user_type == "agent":
            dept = kwargs.get("department", "General")
            return Agent(name, email, dept)
        elif user_type == "admin":
            return Admin(name, email)
        else:
            raise ValueError(f"Unknown user type: {user_type}")

    def close_any_ticket(self, ticket: "Ticket") -> None:
        """Force-close any ticket regardless of state or useee."""
        ticket._close()
        self._tickets_closed += 1
        ticket._add_comment("Closed by admin", self)
        print(f"🔒 Admin {self.name} closed ticket #{ticket.id}")

    def get_system_report(self, tickets: List["Ticket"]) -> Dict:
        """Generate system-wide analytics."""
        total = len(tickets)
        if total == 0:
            return {"message": "No tickets in system"}

        counts = {status: 0 for status in Status}
        for t in tickets:
            counts[t.status] += 1

        resolved_or_closed = counts[Status.RESOLVED] + counts[Status.CLOSED]

        return {
            "total_tickets": total,
            "open": counts[Status.OPEN],
            "in_progress": counts[Status.IN_PROGRESS],
            "resolved": counts[Status.RESOLVED],
            "closed": counts[Status.CLOSED],
            "resolution_rate": f"{(resolved_or_closed / total * 100):.1f}%",
            "users_created": self._users_created,
            "tickets_force_closed": self._tickets_closed
        }


# ============================================================
# TICKET CLASS (The Core Entity)
# ============================================================

class Ticket:
    """
    A support ticket tracking a problem from creation to resolution.

    Lifecycle: OPEN → IN_PROGRESS (claimed) → RESOLVED/CLOSED

    Methods starting with _ are "private?" — meant for internal use.
    The User classes call these to change state safely but surely.
    """
    _ticket_counter = 0

    def __init__(
        self,
        title: str,
        description: str,
        customer: Customer,
        priority: Priority,
        category: Category
    ):
        Ticket._ticket_counter += 1
        self.id = Ticket._ticket_counter
        self.title = title
        self.description = description
        self.customer = customer
        self.priority = priority
        self.category = category
        self.status = Status.OPEN
        self._agent: Optional[Agent] = None
        self._solution: Optional[str] = None
        self.created_at = datetime.now()
        self.resolved_at: Optional[datetime] = None
        self.closed_at: Optional[datetime] = None
        self._comments: List[Dict] = []
        self._add_comment("Ticket created", "System")

    # --- Properties (read-only access to private attrs) ---

    @property
    def assigned_agent(self) -> Optional[Agent]:
        """The agent currently working this ticket, if any tbh
        ."""
        return self._agent

    @property
    def solution(self) -> Optional[str]:
        """The resolution notes, if resolved."""
        return self._solution

    @property
    def comments(self) -> List[Dict]:
        """Copy of all comments (prevents external modification)."""
        return self._comments.copy()

    # --- State transition methods (called by User classes) ---

    def _set_agent(self, agent: Agent) -> None:
        """Internal: assign an agent and move to IN_PROGRESS."""
        self._agent = agent
        self.status = Status.IN_PROGRESS

    def _resolve(self, solution: str) -> None:
        """Internal: mark as resolved."""
        self.status = Status.RESOLVED
        self._solution = solution
        self.resolved_at = datetime.now()

    def _close(self) -> None:
        """Internal: force-close the ticket."""
        self.status = Status.CLOSED
        self.closed_at = datetime.now()

    # --- Comment system ---

    def _add_comment(self, text: str, author) -> None:
        """Internal: append a comment with timestamp."""
        self._comments.append({
            "text": text,
            "author": author.name if isinstance(author, BaseUser) else author,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M")
        })

    def add_comment(self, text: str, user: BaseUser) -> None:
        """Public: anyone can add a comment to a ticket."""
        self._add_comment(text, user)
        print(f"💬 Comment added to #{self.id}")

    # --- Display ---

    def get_details(self) -> str:
        """Pretty-print full ticket info."""
        lines = [
            f"\n{'='*50}",
            f"📋 TICKET #{self.id}",
            f"{'='*50}",
            f"Title:       {self.title}",
            f"Description: {self.description}",
            f"Category:    {self.category.value}",
            f"Priority:    {'🔴' * self.priority.value} {self.priority.name}",
            f"Status:      {self.status.value.upper()}",
            f"Created:     {self.created_at.strftime('%Y-%m-%d %H:%M')}",
            f"Customer:    {self.customer.name}",
        ]

        if self._agent:
            lines.append(f"Agent:       {self._agent.name}")
        if self._solution:
            lines.append(f"Solution:    {self._solution}")
        if self.resolved_at:
            lines.append(f"Resolved:    {self.resolved_at.strftime('%Y-%m-%d %H:%M')}")
        if self.closed_at:
            lines.append(f"Closed:      {self.closed_at.strftime('%Y-%m-%d %H:%M')}")

        lines.append(f"\nComments ({len(self._comments)}):")
        for c in self._comments:
            lines.append(f"  [{c['timestamp']}] {c['author']}: {c['text']}")

        lines.append(f"{'='*50}")
        return "\n".join(lines)

    def __str__(self) -> str:
        agent = self._agent.name if self._agent else "Unassigned"
        return f"[#{self.id}] {self.title} | {self.status.value} | {agent}"

    def __repr__(self) -> str:
        return f"Ticket(id={self.id}, title={self.title!r}, status={self.status.name})"


# ============================================================
# DEMO
# ============================================================

def run_demo():
    """Run a full workflow demonstration."""
    print("=" * 60)
    print("🎫  OOP TICKETING SYSTEM - DEMO")
    print("=" * 60)

    # --- Setup ---
    print("\n🔧 SETUP: Admin creates users")
    admin = Admin("Sarah", "sarah@company.com")

    alice = admin.create_user("customer", "Alice", "alice@client.com")
    bob = admin.create_user("agent", "Bob", "bob@support.com", department="IT")
    charlie = admin.create_user("agent", "Charlie", "charlie@support.com", department="Billing")

    print(f"   Created: {alice}")
    print(f"   Created: {bob} (Dept: {bob.department})")
    print(f"   Created: {charlie} (Dept: {charlie.department})")

    # --- Scenario 1: IT Emergency ---
    print("\n" + "=" * 60)
    print("📝 SCENARIO 1: IT Emergency")
    print("=" * 60)

    ticket1 = alice.create_ticket(
        "Server Down!",
        "Production server not responding, urgent!",
        Priority.CRITICAL,
        Category.IT
    )

    bob.claim_ticket(ticket1)
    ticket1.add_comment("Checking server logs...", bob)
    bob.resolve_ticket(ticket1, "Restarted Apache service, server back online")

    print(ticket1.get_details())

    # --- Scenario 2: Billing Issue ---
    print("\n" + "=" * 60)
    print("📝 SCENARIO 2: Billing Question")
    print("=" * 60)

    ticket2 = alice.create_ticket(
        "Wrong charge on invoice",
        "I was charged twice for last month",
        Priority.MEDIUM,
        Category.BILLING
    )

    charlie.claim_ticket(ticket2)
    charlie.resolve_ticket(ticket2, "Refunded duplicate charge, $50 credited")

    # --- Alice checks her tickets ---
    print("\n")
    alice.view_my_tickets()

    # --- Scenario 3: Admin force-close ---
    print("\n" + "=" * 60)
    print("📝 SCENARIO 3: Admin Force-Close")
    print("=" * 60)

    ticket3 = alice.create_ticket("Old issue", "This is from last year", Priority.LOW)
    admin.close_any_ticket(ticket3)

    # --- Final Report ---
    print("\n" + "=" * 60)
    print("📊 FINAL SYSTEM REPORT")
    print("=" * 60)

    all_tickets = alice.tickets
    report = admin.get_system_report(all_tickets)

    for key, value in report.items():
        label = key.replace("_", " ").title()
        print(f"   {label}: {value}")

    print(f"\n   {bob.get_workload()}")
    print(f"   {charlie.get_workload()}")

    print("\n" + "=" * 60)
    print("✅ DEMO COMPLETE")
    print("=" * 60)
    print(f"\nTotal tickets created: {Ticket._ticket_counter}")
    print(f"Total users in system: {BaseUser._next_id - 1}")


if __name__ == "__main__":
    run_demo()  #DONEEEEEEEEEEEEEEEEEEEEEE!
