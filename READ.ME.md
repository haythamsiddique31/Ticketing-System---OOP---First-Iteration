# OOP Ticketing System ----- What does it even mean?

A fully-featured, object-oriented ticketing system built in Python. Designed as a portfolio piece to demonstrate clean architecture, design patterns, and professional coding practices.

## Features -----

- **Full ticket lifecycle**: Create → Assign → Comment → Resolve → Close → Reopen again ,etc.
- **Role-based access control**: Admin, Agent, Reporter, Viewer roles with the granular permissions
- **Priority & categorization**: LOW/MEDIUM/HIGH/CRITICAL + BUG/FEATURE/SUPPORT/INCIDENT/GENERAL
- **Search & filtering**: Search by text, filter by the status, assignee, priority, tags
- **Audit logging**: Every action is ALWAYS tracked with timestamps
- **Notification system**: Observer pattern for email/Slack-style notifications
- **Statistics dashboard**: System-wide metrics everytime - it has to be scalable otherwise what is the point generalising

## Architecture & Design Patterns  -----

| **Repositories** | `repositories/` | Decouples any type of data access from business logic. Swap SQLite/PostgreSQL without touching other code, etc. |
| **Facades** | `TicketService` | Single entry point for all operations. CLI/API only talk to the service |
| **Observers** | `NotificationService` | Notifiers subscribe to ticket events. Easy to add new notification channels |
| **Strategists** | `User.role` + `Permission` | Different roles have different permission strategies. No if-else chains |
| **States** | `TicketStatus` | ANY Ticket behaviour changes based on its state (can't assign closed tickets) |
| **Commands** | `TicketService` methods | Each operation is entirely self-containd, auditable, and could support undo |
| **Builders** | `Ticket` dataclass | Flexible object creation with sensible defaults ofc |

**End of Documentation** - For now ~
