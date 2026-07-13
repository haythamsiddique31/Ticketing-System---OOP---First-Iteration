from typing import List


created_ticket_ids: List[str] = field(default_factory=list)
assigned_ticket_ids: List[str] = field(default_factory=list)
    
def has_permission(self, permission: Permission) -> bool:
        """Check if user has a specific permission."""
        return permission in ROLE_PERMISSIONS.get(self.role, set())
    
def can_modify_ticket(self, ticket_reporter: str) -> bool:
        """Check if user can modify a specific ticket."""
        if self.role == Role.ADMIN:
            return True
        if self.role == Role.AGENT:
            return True
        return self.username == ticket_reporter
    
def __str__(self) -> str:
        return f"{self.username} ({self.role.name})"
    
def __repr__(self) -> str:
        return f"User(username={self.username!r}, role={self.role.name})"