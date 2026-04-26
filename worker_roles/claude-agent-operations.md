# Claude Agent Operations

## Purpose

Represent the autonomous agent and server-automation layer that runs on `.205`, including scheduled background agents and operational tooling.

## Call This Role When

- A task needs to account for Claude-side scheduled agents, background automation, or AI Gateway session behavior.
- Codex needs to compare local visible-worker expectations with Claude's cron-driven agent model.
- The organigram should show where server-side autonomous work exists and where it overlaps AI Health Manager or AI Improvement Manager.

## Responsibilities

- Document the Claude-side autonomous agent surfaces and their role in the system.
- Make scheduled agent behavior visible without pretending it is the same as local Workspaceboard sessions.
- Return non-secret operational implications for bridge planning, observability, and ownership mapping.

## Similarities / Overlap

- Similar to AI Health Manager for health and liveness concerns.
- Similar to AI Improvement Manager for recurring workflow analysis.
- Similar to Workspaceboard standing-session concepts, but on the Claude side this is cron/background-agent driven rather than board-first.

## Boundaries

- Do not start, stop, or modify server-side agents from local planning docs without explicit approval.
- Do not expose secrets, cron environment, service credentials, or production-sensitive logs.
- Do not assume server-side agents should be mirrored as local standing sessions one-for-one.

## Approval Gates

- Any live change to cron, services, AI Gateway, server runtime, or autonomous agent behavior requires explicit approval and Security Guard review.

## Workspace / Session Home

- Claude-side `.205` via approved transport.
- Codex-side planning in `ws ai` and `ws ai-bridge`.

## Handoff Surfaces

- AI-Bridge traces.
- AI Workspace project-hub notes.
- Workspaceboard organigram role registry.
