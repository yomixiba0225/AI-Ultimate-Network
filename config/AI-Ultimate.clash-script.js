// ============================================================================
// AI-Ultimate-Network — Clash Verge GLOBAL SCRIPT. GENERATED — DO NOT EDIT.
// Rebuild: python3 scripts/build.py --target clash-script
//
// Put this in Clash Verge:  设置 → 全局扩展脚本 (Global Script).
// If you ALREADY have a Global Script (e.g. Adobe block), keep ONE main() and paste
// only the code between "BEGIN" and "END" inside it, just before `return config`.
// Works across EVERY subscription automatically — builds groups from the live nodes.
// ============================================================================
function main(config) {
  // ===== AI-Ultimate-Network BEGIN =====
  var names = (config.proxies || []).map(function (p) { return p.name; });
  var pick = function (re) { return names.filter(function (n) { return re.test(n); }); };
  var R = {
    TW: /(\bTW\b|Taiwan|台湾|台灣)/i,
    US: /(\bUS\b|USA|美国|美國)/i,
    SG: /(\bSG\b|Singapore|新加坡|狮城)/i,
    JP: /(\bJP\b|Japan|日本)/i
  };
  var region = function () {
    var a = [];
    for (var i = 0; i < arguments.length; i++) a = a.concat(pick(R[arguments[i]]));
    return a.filter(function (v, idx) { return a.indexOf(v) === idx; });
  };
  var sel = function (name, list) {
    return { name: name, type: "select", proxies: (list.length ? list : ["Proxy"]) };
  };
  var aiGroups = [
    sel("Claude", region("TW")),
    sel("ChatGPT", region("US", "SG")),
    sel("GitHub", region("US", "JP")),
    sel("Google", region("JP", "SG")),
    { name: "Proxy", type: "select", proxies: (names.length ? names : ["DIRECT"]) },
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
    "GEOSITE,apple,DIRECT",
    "GEOSITE,geolocation-cn,DIRECT",
    "GEOIP,CN,DIRECT,no-resolve"
  ];
  config["rules"] = aiRules.concat(config["rules"] || []);
  // ===== AI-Ultimate-Network END =====
  return config;
}
