// ============================================================================
// AI-Ultimate-Network — Clash Verge GLOBAL SCRIPT (Adobe + AI fused). GENERATED.
// Rebuild: python3 scripts/build.py --target clash-script-adobe
//
// ONE main(): Adobe telemetry block (RULE-SET -> REJECT) + the complete
// AI-Ultimate block (WeChat-safe DNS, IM process rules, 5 strategy groups).
// Paste this ENTIRE file into Clash Verge: 设置 → 全局扩展脚本 (full replace).
// Copy from the raw file only — never via Markdown editors/IM apps, they inject
// invisible zero-width characters that break JS parsing (learned the hard way).
// ============================================================================
function main(config) {
  // ===== Adobe block =====
  config["rule-providers"] = config["rule-providers"] || {};
  config["rule-providers"]["adobe-block"] = {
    type: "http", behavior: "classical", format: "yaml",
    url: "https://fastly.jsdelivr.net/gh/ignaciocastro/a-dove-is-dumb@latest/clash.yaml",
    path: "./ruleset/adobe-block.yaml", interval: 86400
  };
  config.rules = config.rules || [];
  config.rules.unshift("RULE-SET,adobe-block,REJECT");

  // ===== AI-Ultimate-Network BEGIN =====
  // Base subscriptions may enable IPv6 even though the standalone profile does not.
  // Disable both kernel IPv6 handling and AAAA answers to avoid TUN direct-path stalls.
  config["ipv6"] = false;
  // Belt: if the tun section is visible at enhance time, drop its v6 too. The Verge
  // UI "IPv6" toggle must ALSO be off — it is applied after scripts and wins.
  if (config["tun"]) config["tun"]["ipv6"] = false;
  // --- DNS: deterministic, WeChat-safe (see docs/adr/ADR-0009-wechat-tun-dns.md) ---
  // Root cause of "WeChat stuck at 收取中 for minutes under TUN": fake-ip answers for
  // IM domains break WeChat's own connection logic. Fix = own the dns section:
  // fake-ip mode BUT with IM/NTP/STUN domains excluded (fake-ip-filter), domestic DoH
  // for CN names, foreign fallback for the rest. Verge's "DNS 覆写" toggle can stay OFF.
  config["dns"] = {
    enable: true,
    ipv6: false,
    "enhanced-mode": "fake-ip",
    "fake-ip-range": "198.18.0.1/16",
    "fake-ip-filter": [
      "*.lan", "*.local", "*.localdomain",
      "+.msftconnecttest.com", "+.msftncsi.com",
      "+.stun.*.*", "+.stun.*.*.*",
      "time.*.com", "time.*.apple.com", "ntp.*.com", "+.pool.ntp.org",
      // IM — WeChat/QQ/DingTalk/Feishu must get REAL IPs or they stall under TUN:
      "+.qq.com", "+.weixin.qq.com", "+.wechat.com", "+.weixinbridge.com",
      "+.wechatapp.com", "+.qpic.cn", "+.qlogo.cn", "+.gtimg.cn", "+.tencent.com",
      "+.dingtalk.com", "+.feishu.cn", "+.larksuite.com",
      "+.163.com", "+.126.net", "+.netease.com"
    ],
    "default-nameserver": ["223.5.5.5", "119.29.29.29"],
    nameserver: ["https://doh.pub/dns-query", "https://dns.alidns.com/dns-query"],
    "nameserver-policy": {
      "geosite:cn": ["https://doh.pub/dns-query", "https://dns.alidns.com/dns-query"]
    },
    fallback: ["https://dns.google/dns-query", "https://cloudflare-dns.com/dns-query"],
    "fallback-filter": { geoip: true, "geoip-code": "CN", ipcidr: ["240.0.0.0/4"] }
  };
  var mk = function (name, filter) {
    return { name: name, type: "select", "include-all": true, filter: filter, proxies: ["Proxy"] };
  };
  var aiGroups = [
    mk("Claude", "(?i)(\\bTW\\b|Taiwan|台湾|台灣)"),
    mk("ChatGPT", "(?i)(\\bUS\\b|USA|美国|美國|\\bSG\\b|Singapore|新加坡|狮城|\\bJP\\b|Japan|日本|\\bHK\\b|Hong ?Kong|香港)"),
    mk("GitHub", "(?i)(\\bHK\\b|Hong ?Kong|香港)"),
    mk("Google", "(?i)(\\bHK\\b|Hong ?Kong|香港|\\bJP\\b|Japan|日本|\\bSG\\b|Singapore|新加坡|狮城|\\bUS\\b|USA|美国|美國)"),
    mk("TikTok", "(?i)(\\bJP\\b|Japan|日本|\\bTW\\b|Taiwan|台湾|台灣|\\bSG\\b|Singapore|新加坡|狮城)"),
    { name: "Proxy", type: "select", "include-all": true },
    { name: "Apple", type: "select", proxies: ["DIRECT", "Proxy"] }
  ];
  config["proxy-groups"] = aiGroups.concat(config["proxy-groups"] || []);
  var aiRules = [
    "IP-CIDR,2408:80f1::/32,REJECT,no-resolve",
    "PROCESS-NAME,WeChat,DIRECT",
    "PROCESS-NAME,QQ,DIRECT",
    "PROCESS-NAME,DingTalk,DIRECT",
    "PROCESS-NAME,Lark,DIRECT",
    "DOMAIN-SUFFIX,weixin.qq.com,DIRECT",
    "DOMAIN-SUFFIX,wechat.com,DIRECT",
    "DOMAIN-SUFFIX,qq.com,DIRECT",
    "DOMAIN-SUFFIX,qpic.cn,DIRECT",
    "DOMAIN-SUFFIX,qlogo.cn,DIRECT",
    "DOMAIN-SUFFIX,claude.ai,Claude",
    "DOMAIN-SUFFIX,anthropic.com,Claude",
    "DOMAIN-SUFFIX,claude.com,Claude",
    "DOMAIN-SUFFIX,claudeusercontent.com,Claude",
    "DOMAIN-KEYWORD,anthropic,Claude",
    "DOMAIN-SUFFIX,openai.com,ChatGPT",
    "DOMAIN-SUFFIX,chatgpt.com,ChatGPT",
    "DOMAIN-SUFFIX,chat.com,ChatGPT",
    "DOMAIN-SUFFIX,sora.com,ChatGPT",
    "DOMAIN-SUFFIX,oaistatic.com,ChatGPT",
    "DOMAIN-SUFFIX,oaiusercontent.com,ChatGPT",
    "DOMAIN-SUFFIX,livekit.cloud,ChatGPT",
    "DOMAIN,openaiapi-site.azureedge.net,ChatGPT",
    "DOMAIN,api.statsig.com,ChatGPT",
    "DOMAIN,api-iam.intercom.io,ChatGPT",
    "DOMAIN,o33249.ingest.sentry.io,ChatGPT",
    "DOMAIN-KEYWORD,openaiapi,ChatGPT",
    "DOMAIN-KEYWORD,openaicom,ChatGPT",
    "DOMAIN-SUFFIX,github.com,GitHub",
    "DOMAIN-SUFFIX,githubusercontent.com,GitHub",
    "DOMAIN-SUFFIX,githubassets.com,GitHub",
    "DOMAIN-SUFFIX,githubcopilot.com,GitHub",
    "DOMAIN-SUFFIX,github.io,GitHub",
    "DOMAIN-SUFFIX,github.dev,GitHub",
    "DOMAIN-SUFFIX,githubapp.com,GitHub",
    "DOMAIN-SUFFIX,ghcr.io,GitHub",
    "DOMAIN-SUFFIX,gemini.google.com,Google",
    "DOMAIN-SUFFIX,aistudio.google.com,Google",
    "DOMAIN-SUFFIX,ai.google.dev,Google",
    "DOMAIN-SUFFIX,generativelanguage.googleapis.com,Google",
    "DOMAIN-SUFFIX,notebooklm.google.com,Google",
    "DOMAIN-SUFFIX,bard.google.com,Google",
    "DOMAIN-SUFFIX,deepmind.com,Google",
    "DOMAIN-SUFFIX,deepmind.google,Google",
    "DOMAIN,labs.google,Google",
    "DOMAIN-SUFFIX,apps.mzstatic.com,Apple",
    "DOMAIN,smoot.apple.com,Apple",
    "DOMAIN,gspe1-ssl.ls.apple.com,Apple",
    "DOMAIN,guzzoni.apple.com,Apple",
    "DOMAIN,apple-relay.apple.com,Apple",
    "DOMAIN,apple-relay.cloudflare.com,Apple",
    "DOMAIN,apple-relay.fastly-edge.com,Apple",
    "DOMAIN,cp4.cloudflare.com,Apple",
    "DOMAIN-SUFFIX,tiktok.com,TikTok",
    "DOMAIN-SUFFIX,tiktokv.com,TikTok",
    "DOMAIN-SUFFIX,tiktokcdn.com,TikTok",
    "DOMAIN-SUFFIX,tiktokcdn-us.com,TikTok",
    "DOMAIN-SUFFIX,tiktokv.us,TikTok",
    "DOMAIN-SUFFIX,tiktokmusic.app,TikTok",
    "DOMAIN-SUFFIX,byteoversea.com,TikTok",
    "DOMAIN-SUFFIX,ibyteimg.com,TikTok",
    "DOMAIN-SUFFIX,ibytedtos.com,TikTok",
    "DOMAIN-SUFFIX,muscdn.com,TikTok",
    "DOMAIN-SUFFIX,ttwstatic.com,TikTok",
    "DOMAIN-SUFFIX,tik-tokapi.com,TikTok",
    "DOMAIN-KEYWORD,tiktok,TikTok",
    "DOMAIN-SUFFIX,perplexity.ai,Proxy",
    "DOMAIN-SUFFIX,pplx.ai,Proxy",
    "DOMAIN,pplx-res.cloudinary.com,Proxy",
    "DOMAIN-SUFFIX,x.ai,Proxy",
    "DOMAIN-SUFFIX,grok.com,Proxy",
    "DOMAIN-SUFFIX,openrouter.ai,Proxy",
    "DOMAIN,copilot.microsoft.com,Proxy",
    "DOMAIN,sydney.bing.com,Proxy",
    "DOMAIN-SUFFIX,mistral.ai,Proxy",
    "DOMAIN-SUFFIX,cohere.com,Proxy",
    "DOMAIN-SUFFIX,deepseek.com,DIRECT",
    "GEOSITE,github,GitHub",
    "GEOSITE,tiktok,TikTok",
    "GEOSITE,apple,DIRECT",
    "GEOSITE,geolocation-cn,DIRECT",
    "GEOIP,CN,DIRECT,no-resolve"
  ];
  config["rules"] = aiRules.concat(config["rules"] || []);
  // ===== AI-Ultimate-Network END =====
  return config;
}
