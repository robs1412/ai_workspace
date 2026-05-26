## Contact Add Skill

Updated: 2026-05-23 CDT

When Robert or Sonat says to add a contact and the target is otherwise clear, Avignon should start from these approved internal paths before escalating the item as a generic contact blocker:

1. Use the Portal contact-create surface: `https://portal.koval-distillery.com/#/relationship-management/contact/create`
2. If Portal entry needs supporting record context, use `/contactreport` DB information to confirm the target account/contact context through the normal approved workspace route.

Operating rule:
- Treat this as a concrete Avignon execution skill, not as a request to invent a new workflow.
- Keep the normal guardrails: no credential disclosure, no OAuth/token work, no external reply, and no CRM mutation when duplicate/target handling is still unclear.
- For owner-facing updates, state the exact next action plainly: use the Portal contact-create path or Contactreport-backed record context, then report what was created or what exact duplicate/target question remains.
