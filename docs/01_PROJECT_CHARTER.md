# AI-Ultimate-Shadowrocket

Version: 1.0.0

Status: Project Charter

Author: Claude Code (Execute), ChatGPT (Architecture)

---

# Project Charter

## Project Vision

AI-Ultimate-Shadowrocket 是一个专门面向 AI 重度用户的 Shadowrocket 配置项目。

它不是一个普通的翻墙配置。

它也不是一个简单修改 Lazy.conf 的项目。

它的目标是：

> 为 AI Developer 提供长期稳定、可维护、可扩展的网络策略配置。

项目将长期维护，并最终支持：

- Shadowrocket
- Clash Meta
- Clash Verge
- Surge（规划）

所有平台共享统一的设计思想，而不是维护多份完全不同的配置。

---

# Background

随着 Claude、ChatGPT、Codex、Cursor、Gemini 等 AI 工具成为开发工作流的重要组成部分，传统的代理配置已经无法满足以下需求：

- AI 服务需要固定地区
- AI 服务需要固定 IP
- AI 服务需要长期稳定
- AI 服务需要独立策略
- 多机场需要协同工作
- 普通网站与 AI 网站应采用不同策略

目前大多数配置存在以下问题：

- AI 服务混杂在 Proxy 中
- 自动测速导致频繁切换 IP
- 无法针对 Claude 与 OpenAI 做独立优化
- 节点维护成本高
- 配置可读性差
- 不适合长期维护

因此，本项目诞生。

---

# Goals

本项目的目标：

## Goal 1

构建目前 GitHub 上质量最高的 AI Shadowrocket 配置。

---

## Goal 2

保持与 Lazy.conf 最大兼容性。

原则：

> Prefer Extension over Replacement.

尽可能新增，而不是推翻。

---

## Goal 3

针对 AI 服务进行深度优化。

包括：

Anthropic

OpenAI

Claude Code

Codex

Cursor

GitHub Copilot

Gemini

Perplexity

OpenRouter

AI Studio

未来新增 AI 服务应可以方便扩展。

---

## Goal 4

采用工程化开发。

项目必须具备：

- Documentation
- Version
- Changelog
- Release
- Testing
- Validation
- GitHub Workflow

而不是一个单独的 conf 文件。

---

# Non Goals

本项目不追求：

自动测速最快。

原因：

AI 服务更重视 IP 稳定性。

因此：

固定 IP

优先于

自动测速。

---

本项目不追求：

配置最短。

而追求：

配置最容易维护。

---

本项目不追求：

覆盖所有网站。

而重点覆盖：

AI 工作流。

---

# Design Principles

## Principle 1

Stable IP First

固定 IP

优先于

自动测速。

---

## Principle 2

AI First

所有 AI 服务必须拥有独立策略。

不得混入普通 Proxy。

---

## Principle 3

Keep Compatibility

保持 Lazy.conf 最大兼容性。

尽量新增。

避免删除。

避免破坏。

---

## Principle 4

Human Readable

配置必须具备良好的可读性。

所有：

Rule

Proxy Group

Provider

必须拥有清晰命名。

---

## Principle 5

Maintainability

新增节点时：

不得修改配置。

应通过：

Regex

自动识别。

---

## Principle 6

Git Friendly

任何修改：

必须：

Commit

Documentation

Changelog

同步更新。

---

# User Persona

主要用户：

AI Developer

特点：

- 使用 Claude
- 使用 ChatGPT
- 使用 GitHub
- 使用 Cursor
- 使用 Claude Code
- 使用 Codex

重度开发者。

---

# Primary Scenario

工作日：

打开 Mac

↓

启动 Clash Verge

↓

启动 Claude Code

↓

启动 Codex

↓

打开 GitHub

↓

打开 ChatGPT

↓

打开 Claude

整个过程：

无需切换节点。

无需测速。

无需修改配置。

---

手机：

打开 Shadowrocket。

↓

保持：

Claude

固定台湾。

ChatGPT

固定美国。

普通网站：

Proxy。

国内：

DIRECT。

---

# Strategy Philosophy

AI 服务：

必须：

固定地区。

固定节点。

固定策略。

手动切换。

禁止：

url-test。

禁止：

fallback。

禁止：

load-balance。

AI 服务：

仅允许：

Select。

---

普通网站：

可以：

自动测速。

可以：

自动选择。

可以：

Fallback。

---

# Airport Strategy

项目支持多个机场共同工作。

但：

不得：

按机场分类。

而：

按用途分类。

例如：

Claude

↓

台湾节点。

ChatGPT

↓

美国节点。

Google

↓

日本。

GitHub

↓

美国。

Proxy

↓

所有节点。

---

# Architecture Overview

配置由：

Rules

Providers

Proxy Groups

Scripts

Documentation

共同组成。

而不是：

一个 conf 文件。

---

# Expected Deliverables

最终应生成：

README

CHANGELOG

AI-Ultimate.conf

Documentation

Validation Scripts

GitHub Release

Version Tag

Roadmap

Testing Report

全部文档。

---

# Success Criteria

项目成功标准：

Claude：

固定台湾。

ChatGPT：

固定美国。

GitHub：

独立策略。

Google：

独立策略。

Apple：

DIRECT。

Lazy：

保持兼容。

Shadowrocket：

无语法错误。

Regex：

可自动识别节点。

Documentation：

完整。

GitHub：

可长期维护。

---

# Long-term Vision

未来：

不仅维护 Shadowrocket。

还将：

生成：

Clash Meta

Clash Verge

Surge

统一配置。

形成：

AI-Ultimate Network Stack。

项目将长期维护。

Version：

v1

↓

v2

↓

v3

持续迭代。