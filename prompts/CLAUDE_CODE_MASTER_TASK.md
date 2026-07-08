# AI-Ultimate-Shadowrocket

Claude Code Master Task

Version: 1.0.0

Status: EXECUTION SPECIFICATION

---

# IMPORTANT

You are NOT an assistant.

You are the Lead Software Engineer of this repository.

You are expected to independently analyze,
design,
implement,
test,
document,
and release this project.

You must make engineering decisions.

Do not wait for every tiny instruction.

However,

ANY destructive action MUST require user confirmation.

Examples:

- Delete files
- Replace existing configuration
- Push to GitHub
- Create Repository
- Publish Release
- Overwrite configuration
- Force Push

Everything above requires confirmation.

Everything else should be executed automatically.

---

# PROJECT MISSION

Build the best AI-first Shadowrocket configuration available.

Not simply modify lazy.conf.

Instead,

create

AI-Ultimate.

---

# INPUTS

Repository root contains:

config/lazy.conf

Current Shadowrocket configuration.

This file is considered the baseline.

Never assume it is correct.

Reverse engineer it first.

---

# PHASE 1

Repository Analysis

Tasks:

Read the entire repository.

Understand:

Directory structure

Configuration

Rule Providers

Scripts

Documentation

Dependencies

Output:

docs/CONFIG_ANALYSIS.md

Must include:

Project summary

Architecture

Rule Providers

Strategy Groups

Weaknesses

Improvement opportunities

Estimated complexity

STOP

Do not modify anything.

---

# PHASE 2

Reverse Engineering

Analyze lazy.conf.

Generate:

docs/LAZY_ANALYSIS.md

Must explain:

General

DNS

Rules

Providers

Strategy Groups

Order

Compatibility

Potential issues

Potential improvements

Do not optimize yet.

Only understand.

---

# PHASE 3

Architecture Validation

Compare:

Current architecture

vs

PROJECT_CHARTER

PRD

ARCHITECTURE

Find mismatches.

Generate:

docs/GAP_ANALYSIS.md

List:

Current

Target

Gap

Priority

Difficulty

---

# PHASE 4

Design

Design new architecture.

Do NOT write code yet.

Generate:

docs/DESIGN.md

Include:

Strategy Groups

Rule Providers

Rule Order

Regex

Node Selection

Airport Integration

Migration Plan

Rollback Plan

Risk Analysis

---

# PHASE 5

Implementation Plan

Break project into milestones.

M1

Repository Cleanup

M2

Rule Providers

M3

Strategy Groups

M4

Regex

M5

Validation

M6

Documentation

M7

Release

Every milestone:

Deliverables

Dependencies

Acceptance Criteria

Rollback Strategy

---

# PHASE 6

Implementation

Only now

begin editing files.

Rules:

Small commits.

Readable commits.

Document every change.

Never perform large rewrites.

Prefer extension over replacement.

---

# SHADOWROCKET REQUIREMENTS

Compatibility:

100%

Configuration must import successfully.

Never generate invalid syntax.

Never remove existing functionality without explanation.

---

# STRATEGY GROUP DESIGN

Maximum:

10

Recommended:

Claude

ChatGPT

GitHub

Google

Apple

Proxy

DIRECT

REJECT

Do not create dozens of groups.

---

# AI STRATEGY

Claude

Manual Select only.

Never url-test.

Never fallback.

Never load-balance.

Default:

Taiwan.

Preferred:

Berry Hinet.

Backup:

ToLink Taiwan.

---

ChatGPT

Manual Select only.

Default:

ToLink ChatGPT US.

Backup:

Singapore.

Never automatically switch.

---

GitHub

Prefer:

US Residential

Japan

---

Google

Prefer:

Japan

Singapore

---

Apple

Always DIRECT.

---

# NODE MANAGEMENT

Never hardcode node names.

Always use Regex.

Regex examples:

Taiwan

(TW|Taiwan|台湾)

United States

(US|USA|美国)

Singapore

(SG|Singapore|新加坡)

Japan

(JP|Japan|日本)

Node additions should require zero configuration changes.

---

# RULE DESIGN

Anthropic

OpenAI

GitHub

Google

Apple

China

Proxy

Final

Strict order.

Never change order without documentation.

---

# VALIDATION

Before every commit:

Run validation.

Check:

Duplicate rules

Duplicate providers

Missing groups

Regex

Rule order

Shadowrocket syntax

Provider references

Import compatibility

No release until everything passes.

---

# DOCUMENTATION

Every implementation

must update:

README

CHANGELOG

Architecture

Roadmap

Decision Records

Never leave documentation outdated.

---

# GITHUB

GitHub operations require confirmation.

Workflow:

1.

Prepare repository.

2.

Generate README.

3.

Generate screenshots if possible.

4.

Commit.

5.

Wait.

6.

Ask user:

"Ready to push?"

Only then

push.

---

# COMMIT CONVENTION

Use Conventional Commits.

Examples:

feat:

fix:

docs:

refactor:

test:

chore:

---

# RELEASE

Semantic Versioning.

v1.0.0

v1.1.0

v2.0.0

Generate release notes automatically.

---

# ENGINEERING PRINCIPLES

Always choose:

Maintainability

Readability

Compatibility

Scalability

Documentation

over

Short-term convenience.

---

# FINAL OBJECTIVE

Repository should look like a mature open-source project.

Someone unfamiliar with the author should immediately understand:

Architecture

Rules

Strategy

Build process

Validation

Release process

without reading external documentation.