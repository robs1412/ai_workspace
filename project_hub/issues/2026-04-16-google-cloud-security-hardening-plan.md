# Incident / Project Slice Log

Last Updated: 2026-04-16 17:56 CDT (Machine: Macmini.lan)

- Master Incident ID: AI-INC-20260416-GOOGLE-CLOUD-SECURITY-HARDENING-01
- Date Opened: 2026-04-16
- Date Completed: 2026-04-16
- Owner: Codex / Security Guard planning
- Priority: High
- Status: Completed for local no-credential planning

## Scope

Prepare a no-credential Google Cloud security hardening plan for:

- key inventory
- dormant-key cleanup
- API restrictions
- least privilege
- key rotation and expiry policy
- Essential Contacts
- billing anomaly and budget alerts

This slice is local documentation only. It does not authorize Google Cloud console access, credential access, billing access, IAM inspection, live admin work, email, deploys, runtime changes, or any external-system mutation.

## Symptoms

- The AI Workspace backlog includes a Google Cloud security hardening item without a concrete no-write audit plan.
- Future hardening work touches high-risk surfaces: IAM, keys, API access, Essential Contacts, billing alerts, and potentially production integrations.
- A first pass must define approval gates and a read-only audit shape before any Cloud access or mutation is considered.

## Root Cause

Baseline planning exists as a backlog item, but the Cloud-specific hardening scope has not yet been converted into a Security Guard-led checklist with non-secret inventory fields, read-only audit sequencing, and explicit human approval gates.

## No-Credential Hardening Checklist

### Key Inventory

- Build a non-secret inventory table before any live access.
- Track project name, project ID if approved for audit notes, service account or API key label, key type, purpose, owner, environment, creation date, last-used signal, restriction state, rotation owner, and exception status.
- Separate service-account keys, API keys, OAuth clients, workload identity or keyless patterns, and break-glass credentials.
- Do not record private key material, OAuth client secrets, refresh/access tokens, secret-manager payloads, `.env` values, or screenshots containing secrets.

### Dormant-Key Cleanup

- Classify keys as active, unknown, dormant, legacy, break-glass, or candidate for retirement.
- For each candidate, record last-used evidence, dependency owner, proposed disable date, observation window, rollback path, and final deletion date.
- Prefer disable-before-delete for unknown or production-adjacent keys.
- Require explicit human approval before disable, delete, rotate, or recreate actions.

### API Restrictions

- Inventory API keys by restriction posture: unrestricted, application-restricted, API-allowlisted, environment-specific, or unknown.
- Target state: no unrestricted production keys; separate browser/server keys; API allowlists where feasible; referrer/IP/package restrictions where appropriate.
- Record integrations that cannot accept restrictions yet as named exceptions with owner and review date.
- Require explicit approval before changing key restrictions, enabled APIs, quotas, OAuth clients, or app-verification settings.

### Least Privilege

- Review broad IAM grants first: Owner, Editor, basic Viewer, service-account token creator, service-account user, project IAM admin, billing admin, organization admin, and broad group grants.
- Map each broad grant to owner, purpose, expiry/review date, and replacement role if known.
- Prefer group-based access, named owners, and time-bounded exceptions over direct user grants.
- Require explicit approval before adding, removing, narrowing, or expanding any IAM binding.

### Key Rotation / Expiry Policy

- Define maximum age for user-managed service-account keys and API keys.
- Use owner reminders and review dates for exceptions.
- Prefer keyless options where practical: workload identity, service-account impersonation with constrained roles, or managed runtime identity.
- Document emergency rotation steps without storing replacement secrets in git, chat, synced folders, broad docs, or normal manifests.

### Essential Contacts

- Inventory configured contacts by category: security, billing, legal, technical, product updates, suspension, and all contacts.
- Prefer durable group aliases or role inboxes over single-person contacts.
- Confirm at least one accountable human owner for each critical contact category.
- Require explicit approval before changing recipients or categories.

### Billing Anomaly / Budget Alerts

- Inventory budgets, thresholds, alert recipients, anomaly detection settings, and escalation path.
- Target state: alerts for all production projects or billing-account groups, with thresholds appropriate to normal spend.
- Record owners for review and response.
- Require explicit approval before changing budgets, billing contacts, anomaly alerts, billing account links, or payment-related settings.

## First Read-Only Audit Plan

1. Confirm audit authority and approved identity without printing or storing credentials.
2. Confirm which Google Cloud organization, folders, projects, and billing accounts are in scope.
3. Confirm approved output location for non-secret findings.
4. Collect metadata only, after explicit read-only approval:
   - projects and owners
   - IAM bindings and group/user/service-account principals
   - service accounts and user-managed key metadata
   - API key metadata and restriction state
   - OAuth client metadata, if approved
   - enabled APIs and high-risk API surfaces
   - Essential Contacts categories and non-secret recipient labels, if approved
   - budgets, threshold rules, and alert recipient labels, if approved
5. Produce a findings table with severity, affected project, non-secret identifier, risk, proposed remediation, approval needed, rollback/recovery note, and owner.
6. Review findings with Robert or the delegated owner before any mutation.
7. Convert approved remediations into separate implementation tasks with Code and Git Manager / Security Guard coordination where local tooling, scripts, or docs are touched.

## Human Approval Gates

Explicit human approval is required before:

- accessing Google Cloud console, Cloud Shell, gcloud-authenticated surfaces, IAM, billing accounts, Essential Contacts, or live admin surfaces
- reading or using credentials, keychain items, OAuth files, secret-manager payloads, private keys, `.env` values, token caches, or app passwords
- creating, disabling, deleting, rotating, downloading, or replacing service-account keys
- creating, deleting, restricting, or changing API keys, OAuth clients, enabled APIs, quotas, or app-verification settings
- adding, removing, narrowing, expanding, or time-bounding IAM roles, groups, service accounts, impersonation grants, or access policies
- changing Essential Contacts recipients or contact categories
- changing billing budgets, anomaly alerts, notification recipients, payment settings, billing account links, or spend controls
- sending emails, notifications, external alerts, or task updates that disclose security posture beyond the approved internal audience
- deploying automation, scheduled jobs, runtime services, Cloud Functions, Pub/Sub triggers, alert hooks, or background processes
- committing or publishing any findings that contain sensitive identifiers beyond the approved non-secret level

## Repo Logs

### ai_workspace

- Repo Log ID: RL-20260416-GCP-HARDENING-01
- Commit SHA: pending
- Commit Date: pending
- Change Summary: Added local no-credential Google Cloud security hardening plan and audit gates.

## Verification Notes

- Local-only planning.
- Read local AI Workspace TODO and handoff context.
- Read local Security Guard and project-hub security docs.
- Checked git status and Workspaceboard status before editing; AI Workspace was clean and board-reported git dirty state was false.
- Did not access Google Cloud console, credentials, keychain, OAuth files, secrets, billing accounts, IAM, live admin surfaces, email, deploys, or runtime services.

## Rollback Plan

- Revert this documentation file and associated AI Workspace closeout/index notes if the planning record needs to be withdrawn.
- No live Google Cloud, billing, IAM, credential, email, deploy, runtime, or production rollback is needed because none was touched.

## Follow-Ups

- If Robert approves a first read-only audit, create a separate task with explicit scope, identity, output path, and non-secret reporting rules.
- If any mutation is approved later, split remediations into small tasks by surface: keys, API restrictions, IAM least privilege, Essential Contacts, and billing alerts.
- Route future credential/auth/admin work through Security Guard before execution.
