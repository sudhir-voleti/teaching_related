# Marketing Agent OS (`marketing-agent-os`)

A modular, multi-tenant agent operating system framework for quantitative marketing course workflows. This architecture coordinates in-class student milestones, local LLM evaluation routing, and asynchronous feedback distribution via email triggers.

## 🗂️ Core Repository Architecture

*   **`config/`**: Contains environment configurations and structural access maps (e.g., Role-Based Access Control JSONs).
*   **`gateway/`**: Inbound communication managers (e.g., webhook intercepts and polling daemons).
*   **`skills/`**: Hybrid executable workflows linking evaluation prompts with programmatic logic.
*   **`tools/`**: Narrow, deterministic python utility modules (database queries, network clients, security filters).
*   **`tests/`**: Unit tests designed to verify component operations before live deployment execution loops.

## 🛡️ Security & Tenant Verification Design

System execution enforces strict identity validation. Senders must exist on the course roster database to trigger permitted student-facing skills, while administrative commands require multi-tenant clearance rules defined in the permissions hierarchy.
