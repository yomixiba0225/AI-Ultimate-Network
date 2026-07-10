<div align="center">

# AI-Ultimate-Network

**一个面向 AI 开发者的网络代理配置项目 — 专为 Claude、ChatGPT、GitHub 和 Gemini 优化，覆盖 Shadowrocket、Clash Verge 和 Surge。**

*An AI-first network config for developers who live in Claude, ChatGPT, GitHub & Gemini — on Shadowrocket, Clash Verge & Surge.*

稳定的 AI 服务区域分流 · 正则零配置节点管理 · 单一数据源，三端同步 · 像软件工程一样构建、验证和版本管理。

*Stable region-pinned routing · zero-config regex node management · one source of truth, three clients · built, validated, and versioned like real software.*

[![validate](https://github.com/yomixiba0225/AI-Ultimate-Network/actions/workflows/validate.yml/badge.svg)](https://github.com/yomixiba0225/AI-Ultimate-Network/actions/workflows/validate.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
![Shadowrocket](https://img.shields.io/badge/Shadowrocket-stable-blue)
![Clash Verge](https://img.shields.io/badge/Clash%20Verge-beta-orange)
![Surge](https://img.shields.io/badge/Surge-beta-orange)
![version](https://img.shields.io/badge/version-0.3.5-brightgreen)

</div>

---

## 为什么会有这个项目

*Why this exists*

大多数代理配置把所有 AI 服务扔进一个通用的 `PROXY` 策略组，随便指向哪个节点。这会破坏 AI 工作流：Claude 需要**稳定的台湾 IP**，ChatGPT 需要**稳定的美国 IP**，而自动测速切换会不断改变它们的出口，导致封号和风控。

*Most proxy configs dump every AI service into one generic `PROXY` policy. That breaks AI workflows: Claude wants a stable Taiwan IP, ChatGPT wants a stable US IP, and auto-speed-testing keeps changing both out from under you.*

**AI-Ultimate** 为每个 AI 服务提供独立的 **Select-only** 策略组，绑定固定区域：

- 🟣 **Claude → 台湾**（不做 url-test，不故障转移，不负载均衡）
- 🟢 **ChatGPT（含 Codex）→ 美国 / 新加坡 / 日本 / 香港** — 一个组
- ⚫ **GitHub → 香港**，🔵 **Google/Gemini → 香港 / 日本 / 新加坡 / 美国**，🎵 **TikTok → 日本 / 台湾 / 新加坡**
- 🍎 **Apple → DIRECT**（App Store 和 iCloud 始终直连；Apple Intelligence 可手动切换）
- 🌐 **其他 → Proxy**，🇨🇳 **中国 → DIRECT**

节点通过**名称正则**自动加入对应策略组——新增一台 `台湾107` 节点，它会自动进入 Claude 组——**零配置修改**。

*Nodes auto-join groups by name regex — add a `台湾107` node and it lands in the Claude group — zero config edits.*

> 这不是在原版 `lazy.conf` 上改几行。它逆向分析了原版配置（见 [`docs/LAZY_ANALYSIS.md`](docs/LAZY_ANALYSIS.md)），并重建了原版缺失的策略/规则/正则层。
>
> *This is not a fork of `lazy.conf`. It reverse-engineers the stock config and rebuilds the strategy/provider/regex layers it was missing.*

---

## 支持的客户端

*Supported clients*

| 客户端 | 配置文件 | 平台 | 状态 |
|---|---|---|---|
| **Shadowrocket** | [`config/AI-Ultimate.conf`](config/AI-Ultimate.conf) | iOS | ✅ 稳定 |
| **Clash Verge** (Clash Meta) | [`config/AI-Ultimate.clash.yaml`](config/AI-Ultimate.clash.yaml) | Windows / macOS / Linux | 🧪 Beta |
| **Surge** | [`config/AI-Ultimate.surge.conf`](config/AI-Ultimate.surge.conf) | macOS / iOS | 🧪 Beta |

三端配置均由同一套 `rules/*.list` + `scripts/strategy.py` 生成，AI 策略（分流、区域绑定、正则节点选择）在各客户端完全一致——跨端测试保证它们不会漂移。完整配置指南：[`docs/USAGE.md`](docs/USAGE.md)。

*All three are generated from the same source. Cross-client tests guarantee they can't drift. See [`docs/USAGE.md`](docs/USAGE.md).*

## 快速开始（Shadowrocket）

*Quick start*

1. **添加机场订阅**到 Shadowrocket（节点来源）。确保节点名称包含区域标识 — `TW / US / SG / JP` 或 `台湾 / 美国 / 新加坡 / 日本`。
2. **导入配置。**Shadowrocket → 配置 → 从 URL 添加：
   ```
   https://raw.githubusercontent.com/yomixiba0225/AI-Ultimate-Network/main/config/AI-Ultimate.conf
   ```
3. **在 `Claude`、`ChatGPT`、`GitHub`、`Google` 四个组中各选一次节点。**选好后不再变动。
4. 完成。后续新增的节点会自动出现在对应分组中。

> **Clash Verge / Surge 用户：**参见 **[`docs/USAGE.md`](docs/USAGE.md)** — 一行指向机场订阅，然后在同样的四个组中选择节点。

---

## 策略一览

*Strategy at a glance*

| 策略组 | 类型 | 区域正则 | 默认 | 设计理由 |
|---|---|---|---|---|
| **Claude** | `select` | `TW` | 台湾 | Anthropic 需要稳定 IP；ADR-0001 |
| **ChatGPT** | `select` | `US / SG / JP / HK` | 美国 | OpenAI 含 Codex — 一个组；ADR-0002/0008 |
| **GitHub** | `select` | `HK` | 香港 | ADR-0008 |
| **Google** | `select` | `HK / JP / SG / US` | 香港 | Gemini/AI Studio；ADR-0008 |
| **TikTok** | `select` | `JP / TW / SG` | 日本 | 区域敏感；ADR-0008 |
| **Apple** | `select` | — | **DIRECT** | Apple Intelligence 可切换；ADR-0003 |
| **Proxy** | `select` | `.*` | 任意节点 | 通用国外站点 |
| **Auto** | `url-test` | `.*` | 最低延迟 | 非 AI 场景使用 |
| **Final** | `select` | → Proxy/DIRECT | Proxy | `FINAL` 规则指向 |

**AI 策略组故意设为 Select-only** — 不使用 `url-test`、`fallback` 或 `load-balance`（由 `scripts/validate.py` 强制检查）。详见 [ADR-0004](docs/adr/ADR-0004-select-only-ai.md)。

*AI groups are Select-only by design — enforced by `scripts/validate.py`. See [ADR-0004](docs/adr/ADR-0004-select-only-ai.md).*

**规则顺序是合约**（非经文档 + CHANGELOG 更新，不得重排）：

*Rule order is a contract:*

```
Anthropic → OpenAI → GitHub → Google → Apple → China → Proxy → Final
```

---

## 构建方式（配置即代码）

*How it's built (configuration-as-code)*

你不需要手动编辑生成的配置文件。只需修改**规则文件** + **策略定义**，一条构建命令即可生成三端配置：

*You never hand-edit the shipped configs. Edit rule providers + strategy, one build emits all three clients:*

```
scripts/strategy.py   ─┐                         ┌─▶ config/AI-Ultimate.conf         (Shadowrocket)
rules/anthropic.list   │   python3 scripts/build.py ─┼─▶ config/AI-Ultimate.clash.yaml   (Clash Verge)
rules/openai.list      ├────────────────────────▶ └─▶ config/AI-Ultimate.surge.conf   (Surge)
rules/*.list          ─┘   (Shadowrocket 还需要 config/AI-Ultimate.template.conf)
```

```bash
python3 scripts/build.py                 # 重新生成所有客户端配置
python3 scripts/build.py --target clash  # 或只生成一个
python3 scripts/validate.py              # ≤10 个组、AI=select-only、引用完整性、规则顺序、FINAL/MATCH 检查 — 全客户端
python3 -m unittest discover -s tests    # 验收测试 + 跨端一致性测试
```

CI 在每次 push/PR 时运行 构建 → 时效性 → 验证 → 测试（[`.github/workflows/validate.yml`](.github/workflows/validate.yml)）。

*CI runs build → freshness → validate → tests on every push/PR.*

### 30 秒新增一个 AI 服务

*Add an AI service in 30 seconds*

1. 将其域名添加到对应的 `rules/*.list`（或新建一个）。
2. `python3 scripts/build.py && python3 scripts/validate.py`
3. 提交。完成——无需架构改动（见 [`docs/DESIGN.md`](docs/DESIGN.md) §3）。

---

## 项目结构

*Project structure*

```
AI-Ultimate-Network/
├── config/
│   ├── AI-Ultimate.conf            # ← 生成文件 — Shadowrocket
│   ├── AI-Ultimate.clash.yaml      # ← 生成文件 — Clash Verge / Meta
│   ├── AI-Ultimate.surge.conf      # ← 生成文件 — Surge
│   ├── AI-Ultimate.template.conf   # Shadowrocket 模板（编辑此文件）
│   └── lazy.conf                   # 原始基线，保留以供参考/回滚
├── rules/                          # 各服务规则文件（共享数据源）
│   ├── anthropic.list  openai.list  github.list  google.list
│   ├── apple.list  ai-extra.list  china.list  proxy.list  tiktok.list
├── scripts/
│   ├── strategy.py                 # 客户端无关策略定义（分组/区域/顺序）
│   ├── build.py                    # 策略 + 规则 → 三端配置文件
│   └── validate.py                 # 质量门禁（全客户端）
├── tests/test_config.py            # 验收测试 + 跨端一致性测试
├── docs/
│   ├── 01_PROJECT_CHARTER.md  02_PRD.md.md  03_ARCHITECTURE.md
│   ├── CONFIG_ANALYSIS.md  LAZY_ANALYSIS.md  GAP_ANALYSIS.md  DESIGN.md
│   ├── USAGE.md  IMPLEMENTATION_PLAN.md  ROADMAP.md
│   └── adr/                        # 架构决策记录 (ADR-0001…0007)
├── .github/                        # CI + Issue/PR 模板
├── CHANGELOG.md   LICENSE   .gitignore
```

---

## 兼容性与安全性

*Compatibility & safety*

- ✅ 可无语法错误导入 Shadowrocket（已验证）。
- ✅ 保留原版中国流量直连行为（Prefer Extension over Replacement）。
- ♻️ **回滚：**原版 `config/lazy.conf` 完整保留；每次变更都是小提交；详见 [`docs/DESIGN.md`](docs/DESIGN.md) §10。
- 🔒 你的机场订阅链接和节点列表**永远不会**被提交（见 `.gitignore`）。

> Clash Verge 全局脚本和独立 Profile 强制 `ipv6=false`，避免不稳定的 IPv6 路径导致 TUN 卡住。Shadowrocket 的 `dns over proxy` 和 `ipv6=false` 仍为可选 P2 调整，建议先在自己的网络和节点上验证后再启用。

---

## 路线图

*Roadmap*

多客户端生成（Shadowrocket / Clash Verge / Surge）已在 v0.2.0 交付。下一步：更丰富的 Clash/Surge 非 AI 覆盖、指定优选节点、Beta 客户端转稳定——详见 [`docs/ROADMAP.md`](docs/ROADMAP.md)。

*Multi-client generation shipped in v0.2.0. Next: richer non-AI coverage, provider pinning, beta→stable promotion — see [`docs/ROADMAP.md`](docs/ROADMAP.md).*

## 文档

*Documentation*

从 [`docs/DESIGN.md`](docs/DESIGN.md) 开始了解架构，然后阅读 [`docs/adr/`](docs/adr) 中的 ADR 了解每条路由决策的*原因*。

*Start with [`docs/DESIGN.md`](docs/DESIGN.md) for architecture, then ADRs for why.*

## 致谢

*Credits*

基线规则集来自 [blackmatrix7/ios_rule_script](https://github.com/blackmatrix7/ios_rule_script) 和原版 [Shadowrocket-ADBlock-Rules-Forever](https://github.com/johnshall/Shadowrocket-ADBlock-Rules-Forever) 的 `lazy.conf`。策略设计、AI 分流、正则节点模型和工具链为本项目原创。

*Baseline rule-sets from blackmatrix7 and the stock lazy.conf. Strategy design, AI separation, regex node model, and tooling are original to this project.*

## 许可证

*License*

[MIT](LICENSE) © 2026 yomixiba0225
