// ============================================================================
// AI-Ultimate-Network — Clash Verge GLOBAL SCRIPT. GENERATED — DO NOT EDIT.
// Rebuild: python3 scripts/build.py --target clash-script
//
// Put this in Clash Verge:  设置 → 全局扩展脚本 (Global Script).
// If you ALREADY have a Global Script (e.g. Adobe block), keep ONE main() and paste
// only the code between "BEGIN" and "END" inside it, just before `return config`.
//
// Groups use include-all + filter, so they pull nodes from the main subscription AND
// any airports you fuse in via proxy-providers (multi-airport). A region with no node
// falls back to Proxy (never DIRECT), so an empty region can't break the config.
// ============================================================================
function main(config) {
  // ===== AI-Ultimate-Network BEGIN =====
  // Base subscriptions may enable IPv6 even though the standalone profile does not.
  // Disable both kernel IPv6 handling and AAAA answers to avoid TUN direct-path stalls.
  config["ipv6"] = false;
  config["dns"] = config["dns"] || {};
  config["dns"]["ipv6"] = false;
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
