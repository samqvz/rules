import os
import json
import urllib.request
import yaml

# 上游规则源 (可根据需要替换为你喜欢的上游)
UPSTREAM_URLS = {
    "proxy": "https://github.com/Loyalsoldier/clash-rules/releases/download/202603232259/proxy.txt",
    "direct": "https://github.com/Loyalsoldier/clash-rules/releases/download/202603232259/direct.txt",
    "reject": "https://github.com/Loyalsoldier/clash-rules/releases/download/202603232259/reject.txt"
}

def fetch_upstream(url):
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req) as response:
            return set(response.read().decode('utf-8').splitlines())
    except Exception as e:
        print(f"下载失败 {url}: {e}")
        return set()

def read_local_rules(filename):
    filepath = os.path.join("custom_rules", filename)
    if os.path.exists(filepath):
        with open(filepath, "r", encoding="utf-8") as f:
            return set([line.strip() for line in f if line.strip() and not line.startswith('#')])
    return set()

def process_category(category):
    print(f"处理分类: {category}")
    upstream = fetch_upstream(UPSTREAM_URLS[category])
    add_rules = read_local_rules(f"{category}_add.txt")
    remove_rules = read_local_rules(f"{category}_remove.txt")
    
    # 核心合并逻辑
    final_rules = upstream.union(add_rules) - remove_rules
    final_list = sorted(list(final_rules))
    
    # 1. 生成 Mihomo YAML (behavior: domain)
    mihomo_payload = {"payload": final_list}
    with open(f"{category}.yaml", "w", encoding="utf-8") as f:
        yaml.dump(mihomo_payload, f, default_flow_style=False, sort_keys=False)
        
    # 2. 生成 Sing-box JSON 源文件
    singbox_payload = {
        "version": 1,
        "rules": [
            {
                "domain_suffix": final_list
            }
        ]
    }
    with open(f"{category}.json", "w", encoding="utf-8") as f:
        json.dump(singbox_payload, f, indent=2)

if __name__ == "__main__":
    for cat in UPSTREAM_URLS.keys():
        process_category(cat)
