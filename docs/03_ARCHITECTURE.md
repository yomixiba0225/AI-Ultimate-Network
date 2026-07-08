# AI-Ultimate-Shadowrocket

Version: 1.0.0

Document Type:
System Architecture

Status:
Draft

---

# 1. Purpose

本文档定义整个 AI-Ultimate 项目的系统架构。

Claude Code 在开始任何编码之前，必须首先理解本架构。

任何设计不得违反本文档。

---

# 2. Architecture Philosophy

整个项目遵循：

Configuration as Code

Documentation First

AI First

Low Coupling

High Cohesion

Backward Compatible

---

# 3. System Layers

整个项目划分为七层。

Layer 1

Documentation

↓

Layer 2

Configuration

↓

Layer 3

Strategy Groups

↓

Layer 4

Rule Providers

↓

Layer 5

Rules

↓

Layer 6

Validation

↓

Layer 7

Build

每一层职责单一。

不得跨层。

---

# 4. Directory Layout

AI-Ultimate-Shadowrocket/

README.md

CHANGELOG.md

LICENSE

config/

docs/

rules/

scripts/

tests/

.github/

assets/

---

config/

保存：

Shadowrocket

Clash Meta

Surge

配置。

不得保存脚本。

---

docs/

保存：

所有设计文档。

PRD

Architecture

Roadmap

Design

Decision

ADR

全部位于 docs。

---

rules/

保存：

Rule Provider。

每一个 Provider

一个文件。

禁止：

一个超大 Rule 文件。

推荐：

anthropic.list

openai.list

github.list

google.list

apple.list

proxy.list

china.list

---

scripts/

保存：

自动化工具。

例如：

Build

Merge

Validation

Generate

Export

全部放入 scripts。

---

tests/

保存：

自动测试。

例如：

Rule Test

Regex Test

Syntax Test

Duplicate Test

---

.github/

保存：

GitHub Workflow。

Issue Template

PR Template

Release

Actions

未来扩展。

---

# 5. Configuration Layer

配置文件：

不得手工维护。

必须：

Build

自动生成。

例如：

AI-Ultimate.conf

由：

config template

+

rules

+

providers

自动生成。

避免：

维护多个版本。

---

# 6. Rule Provider Layer

Rule Provider

必须：

模块化。

禁止：

一个 Provider

管理所有网站。

推荐：

Anthropic

OpenAI

Google

GitHub

Apple

China

Proxy

Future

每个 Provider

职责唯一。

---

# 7. Strategy Group Layer

整个项目：

最多：

10 个。

推荐：

Claude

ChatGPT

GitHub

Google

Apple

Proxy

DIRECT

Reject

No Resolve

禁止：

二十多个策略。

降低维护成本。

---

# 8. Regex Layer

节点：

不得：

写死。

例如：

禁止：

台湾101

台湾102

台湾103

全部写入配置。

推荐：

Regex。

例如：

Claude

↓

(TW|Taiwan|台湾)

ChatGPT

↓

(US|USA|美国)

+

(SG|Singapore|新加坡)

Google

↓

(JP|Japan|日本)

Proxy

↓

.*

未来：

新增：

台湾108。

无需修改配置。

---

# 9. Airport Layer

机场：

不是：

第一层概念。

策略：

才是。

例如：

Berry

ToLink

只是：

Provider。

真正暴露给用户：

Claude

ChatGPT

Google

GitHub

而不是：

Berry

ToLink。

---

# 10. Build Pipeline

Claude Code

执行顺序：

Step 1

分析：

lazy.conf

↓

Step 2

Reverse Engineering

↓

Step 3

生成：

CONFIG_ANALYSIS.md

↓

Step 4

设计：

Proxy Group

↓

Step 5

生成：

Rule Providers

↓

Step 6

Regex

↓

Step 7

Build

↓

Step 8

Validation

↓

Step 9

Documentation

↓

Step 10

Release

任何阶段失败：

立即停止。

---

# 11. Validation Pipeline

必须：

自动检查。

包括：

Duplicate Rules

Duplicate Providers

Duplicate Proxy Groups

Regex Errors

Shadowrocket Syntax

Rule Order

Missing Provider

Missing Group

FINAL Position

全部自动。

任何失败：

Build Fail。

---

# 12. Rule Order

Rule

必须：

严格排序。

推荐：

Anthropic

↓

OpenAI

↓

GitHub

↓

Google

↓

Apple

↓

China

↓

Proxy

↓

FINAL

不得：

改变。

除非：

Documentation

同步更新。

---

# 13. Node Strategy

AI

永远：

Select。

禁止：

url-test

禁止：

fallback

禁止：

load-balance

普通网站：

允许：

url-test。

---

# 14. Version Strategy

Semantic Version。

例如：

v1.0.0

新增功能：

v1.1.0

重构：

v2.0.0

Bug：

v1.0.1

Documentation：

v1.0.2

---

# 15. Backward Compatibility

Lazy

必须：

保持：

95%

以上兼容。

推荐：

新增。

避免：

删除。

---

# 16. Decision Record

任何重大设计：

必须：

ADR。

Architecture Decision Record。

例如：

为什么：

Claude

使用台湾。

为什么：

ChatGPT

使用美国。

为什么：

Apple

DIRECT。

全部记录。

---

# 17. Scalability

未来：

新增：

Perplexity

Cursor

Windsurf

Grok

DeepSeek

OpenRouter

不得：

修改架构。

仅：

新增：

Rule Provider。

---

# 18. Release Architecture

每次 Release

必须：

README

CHANGELOG

Release Note

Version

Configuration

Validation Report

Documentation

全部更新。

---

# 19. Quality Gates

Release 前：

必须：

Validation

100%

Documentation

100%

Shadowrocket

Import Success

Regex

Pass

Provider

Pass

Rule

Pass

否则：

不得：

Release。

---

# 20. Architecture Summary

Documentation

决定：

设计。

PRD

决定：

功能。

Architecture

决定：

实现。

Code

只是：

Architecture

的实现。

不得：

脱离文档。