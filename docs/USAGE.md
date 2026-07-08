# USAGE.md — installing AI-Ultimate-Network on each client

Three configs are generated from one source of truth (`scripts/strategy.py` + `rules/*.list`):

| Client | File | Platform | Status |
|---|---|---|---|
| Shadowrocket | `config/AI-Ultimate.conf` | iOS | ✅ stable |
| Clash Meta / **Clash Verge** | `config/AI-Ultimate.clash.yaml` | Windows / macOS / Linux | 🧪 beta |
| Surge | `config/AI-Ultimate.surge.conf` | macOS / iOS | 🧪 beta |

**Common rule for all clients:** your airport **node names must contain a region token** —
`TW / US / SG / JP` or `台湾 / 美国 / 新加坡 / 日本` — because groups auto-select nodes by regex.
Then pick a node once per AI group; nothing auto-switches (Select-only, stable IP).

Region → group map (identical on every client):

| Group | Region regex | Pick a node in… |
|---|---|---|
| Claude | Taiwan | 一个台湾节点 |
| ChatGPT | US / SG | 一个美国节点（备选新加坡） |
| GitHub | US / JP | 美国 / 日本 |
| Google | JP / SG | 日本 / 新加坡 |
| Apple | — (default DIRECT) | 保持 DIRECT（Apple Intelligence 可切 Proxy） |

---

## 1. Shadowrocket (iOS)

1. **Add your airport subscription**: 首页 → **+** → Subscribe → 粘贴订阅链接 → 保存.
2. **Import config**: 配置 → **+** → 粘贴：
   ```
   https://raw.githubusercontent.com/yomixiba0225/AI-Ultimate-Network/main/config/AI-Ultimate.conf
   ```
   → 下载 → 点 ✔️ 启用.
3. **Pick nodes once** in the `Claude` / `ChatGPT` / `GitHub` / `Google` groups.
4. Turn on the VPN (install profile on first run). Done.

New nodes auto-join the matching group — no edits. Update: swipe the config → Update.

---

## 2. Clash Verge (Windows / macOS / Linux)

Two ways. **If you have multiple subscriptions, use 2A (Global Merge)** — it's the whole point.

### 2A. Multiple subscriptions — Global Merge overlay ✅ recommended

Use `config/AI-Ultimate.clash-merge.yaml`. This overlays our AI groups + rules on top of
**every** subscription profile at once, so you never edit per-subscription files. Identical
steps on **macOS and Windows** (Clash Verge is the same app on both).

1. Keep your airport subscriptions as normal **Remote** profiles in Clash Verge (they provide
   the nodes). You can have as many as you like.
2. Open **Settings → Merge** (Clash Verge Rev: 设置 → **全局扩展覆写配置 / Global Merge**;
   older builds: per-profile ⋯ → *Edit* → *Merge*). This is the box you found empty.
3. Paste the **entire contents** of `config/AI-Ultimate.clash-merge.yaml` there. Save.
4. That's it. Switch between any subscription profile — the `Claude / ChatGPT / GitHub / Google /
   Proxy / Apple` groups and the AI rules apply automatically, because the groups use
   `include-all: true` (they pull nodes from whichever profile is active). **No node URLs, no
   per-sub copy-paste.**
5. In the **Proxies** page, pick a node once per AI group (Claude→TW, ChatGPT→US, …).

Notes:
- The overlay **prepends** its rules, so AI/Apple/China routing wins; everything else falls
  through to each subscription's own rules + final policy (untouched).
- It only adds groups/rules — it does **not** touch your **Global Script** (e.g. your Adobe
  block). Merge (YAML) and Script (JS) are separate stages and run together.
- Multiple region nodes across different airports all match by name regex, so e.g. a Taiwan node
  from *any* subscription shows up in the Claude group.

### 2B. Single subscription — standalone profile

Clash Verge (Rev) runs the **Clash Meta** core, so it uses `AI-Ultimate.clash.yaml`.

1. **Set your airport subscription URL.** Open `config/AI-Ultimate.clash.yaml` and replace the
   placeholder with your airport's subscription link:
   ```yaml
   proxy-providers:
     airport:
       type: http
       url: "YOUR_AIRPORT_SUBSCRIPTION_URL"   # ← paste your airport sub link
   ```
   > Tip: if your airport gives a Clash subscription, that URL works directly here. The
   > `proxy-providers` mechanism pulls all its nodes; the groups filter them by region.
2. **Import the profile** into Clash Verge:
   - Profiles → **New** → *Local* → paste the edited YAML (or point *Remote* at your own raw
     GitHub URL of this file after you commit your subscription URL — don't commit secrets to a
     public repo; keep your sub URL local).
   - Select the profile to activate it.
3. **Choose nodes**: open the `Claude` / `ChatGPT` / `GitHub` / `Google` proxy groups and select
   a node in each. Set mode to **Rule**.
4. Enable **TUN / System Proxy** as you prefer.

Notes:
- Bulk non-AI routing uses Clash's built-in `GEOSITE` / `GEOIP` (no external rule lists to
  break). AI routing is precise (inlined domains).
- If a group looks empty, your subscription has no node with that region token — add one or
  rename nodes to include `TW/US/SG/JP`.

---

## 3. Surge (macOS / iOS)

Uses `config/AI-Ultimate.surge.conf`.

1. **Add your nodes**: paste your proxies into the `[Proxy]` section, or add your airport via
   **Surge → Subscription**. The groups use `include-all-proxies`, so they see all of them.
2. **Load the config**: Surge → Profiles → put `AI-Ultimate.surge.conf` in your Surge profile
   directory (or paste its contents into your active profile).
3. **Choose nodes** in the `Claude` / `ChatGPT` / `GitHub` / `Google` groups.

Notes:
- Surge coverage for non-AI China/foreign split is `GEOIP,CN` + `FINAL` (coarser than
  Shadowrocket). Add Surge `RULE-SET`s if you want finer control.
- AI separation and region pinning are identical to the other clients.

---

## Optional tweaks (all clients)

- **Pin a preferred node** (e.g. Claude → Berry Hinet): in the source template/strategy add a
  preferred-node selector, rebuild. Shadowrocket: `policy-select-name=`. Clash/Surge: select it
  once in the group (it persists).
- **Enable Apple Intelligence**: flip the `Apple` group from DIRECT to Proxy. Only affects Apple
  Intelligence / Private Relay; the App Store & iCloud always stay DIRECT.

## Rebuilding after edits

Edit `rules/*.list` or `scripts/strategy.py`, then:
```bash
python3 scripts/build.py        # regenerates all three configs
python3 scripts/validate.py     # gate
python3 -m unittest discover -s tests
```
