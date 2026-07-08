# AI-Ultimate-Shadowrocket

Version: 1.0.0

Document Type:
Product Requirement Document (PRD)

Status:
Draft

---

# 1. Product Overview

AI-Ultimate-Shadowrocket 是一套专门针对 AI Developer 的网络策略配置。

项目目标不是构建新的代理工具。

而是在 Shadowrocket（未来支持 Clash Meta / Surge）之上构建：

稳定

长期维护

AI First

的网络策略。

---

# 2. Product Positioning

不是：

通用机场配置。

不是：

普通翻墙配置。

不是：

测速最快配置。

而是：

AI Workflow Network Configuration。

---

# 3. Target Users

第一阶段：

AI Developer

第二阶段：

AI Product Manager

第三阶段：

AI Content Creator

第四阶段：

Enterprise AI Team

---

# 4. User Problems

当前配置普遍存在以下问题：

## Problem 1

Claude

ChatGPT

Gemini

全部共用一个 Proxy。

无法独立控制。

---

## Problem 2

自动测速。

自动切换。

导致：

IP 经常变化。

---

## Problem 3

GitHub

Cursor

Claude Code

使用不同节点。

导致：

连接不稳定。

---

## Problem 4

机场升级。

节点增加。

配置必须修改。

维护成本极高。

---

## Problem 5

Rule Provider

越来越多。

维护困难。

---

# 5. Product Objectives

项目必须：

AI First

Stable IP

Human Friendly

Long-term Maintainable

GitHub Ready

---

# 6. Functional Requirements

项目应支持：

## FR-001

Claude 独立策略。

包括：

Anthropic

Claude

Claude Code

Claude API（预留）

Claude Assets

Claude Static

Claude CDN

---

## FR-002

OpenAI 独立策略。

包括：

ChatGPT

Codex

OpenAI API

Platform

Static

Image

Future APIs

---

## FR-003

Google 独立策略。

包括：

Google

YouTube

Translate

Fonts

Maps

Gemini

AI Studio

---

## FR-004

GitHub 独立策略。

包括：

GitHub

Raw

Assets

Container Registry

Codespaces（预留）

Copilot

---

## FR-005

Apple 独立策略。

包括：

App Store

Apple Music

Apple CDN

Push

Software Update

iCloud

Find My

全部 DIRECT。

---

## FR-006

普通国外网站。

统一：

Proxy。

---

## FR-007

国内网站。

全部：

DIRECT。

---

# 7. Non-functional Requirements

配置必须：

容易阅读。

容易修改。

容易维护。

容易升级。

---

Regex：

必须支持。

---

新增节点：

不得修改配置。

---

新增机场：

仅修改 Provider。

---

# 8. Strategy Group Design

策略组数量：

控制在：

6~10 个。

禁止：

20+

避免复杂。

推荐：

Claude

ChatGPT

GitHub

Google

Proxy

Apple

DIRECT

---

# 9. Claude Strategy

目标：

保持台湾 IP。

默认：

Berry

台湾-Hinet线路。

备用：

ToLink

台湾101

台湾102

台湾103

……

原则：

全部：

Select。

禁止：

url-test。

禁止：

fallback。

禁止：

load-balance。

---

# 10. ChatGPT Strategy

目标：

美国。

备用：

新加坡。

默认：

ToLink

ChatGPT 专线。

原则：

Select。

固定 IP。

用户手动切换。

---

# 11. GitHub Strategy

目标：

稳定。

推荐：

美国

日本。

优先：

家宽。

其次：

IEPL。

最后：

普通线路。

---

# 12. Google Strategy

目标：

稳定。

推荐：

日本。

新加坡。

Google 不建议：

香港。

---

# 13. Apple Strategy

必须：

DIRECT。

除非：

用户主动修改。

---

# 14. Proxy Strategy

Proxy

负责：

普通国外网站。

例如：

Reddit

X

Wikipedia

Medium

V2EX

等等。

AI 网站：

不得进入 Proxy。

---

# 15. Rule Priority

优先级：

Claude

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

Final

任何 Rule：

不得破坏：

以上顺序。

---

# 16. Node Classification

节点：

不得：

手写。

必须：

Regex。

例如：

台湾：

(TW|Taiwan|台湾)

美国：

(US|USA|美国)

新加坡：

(SG|Singapore|新加坡)

日本：

(JP|Japan|日本)

以后：

新增：

台湾107。

自动进入：

Claude。

无需修改配置。

---

# 17. Airport Strategy

支持：

多个机场。

禁止：

按机场分类。

推荐：

按用途分类。

例如：

Claude

↓

Berry

+

ToLink

台湾。

ChatGPT

↓

ToLink

+

Berry

美国。

---

# 18. Compatibility

必须：

兼容：

Lazy.conf。

禁止：

大规模删除。

推荐：

最小侵入。

---

# 19. Extensibility

未来：

新增：

Perplexity

Grok

Mistral

DeepSeek

OpenRouter

无需：

重构。

---

# 20. Acceptance Criteria

Claude：

稳定。

ChatGPT：

稳定。

Regex：

自动识别。

GitHub：

独立。

Google：

独立。

Apple：

DIRECT。

配置：

无语法错误。

Shadowrocket：

正常导入。

Documentation：

完整。

GitHub：

支持长期维护。