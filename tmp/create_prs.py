import os
import requests
import json

TOKEN = "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"
HEADERS = {
    "Authorization": f"Bearer {TOKEN}",
    "Accept": "application/vnd.github.v3+json",
    "X-GitHub-Api-Version": "2022-11-28"
}

targets = [
    {"upstream": "Giskard-AI/awesome-ai-safety", "head": "wiserautomation:wiserautomation-patch-1", "title": "feat: Add SupraWall security layer for autonomous agents", "body": "Adding SupraWall to the Governance/Guardrails section."},
    {"upstream": "kyrolabs/awesome-langchain", "head": "wiserautomation:patch-1", "title": "feat: Add SupraWall to safety/agents", "body": "Adding SupraWall runtime security. [supra-wall.com](https://supra-wall.com)"},
    {"upstream": "Joe-B-Security/awesome-prompt-injection", "head": "wiserautomation:main", "title": "feat: Add SupraWall to tools", "body": "Adding SupraWall to defensive tools. [supra-wall.com](https://supra-wall.com)"},
    {"upstream": "chenryn/aiops-handbook", "head": "wiserautomation:main", "title": "feat: Add SupraWall observability", "body": "Adding SupraWall to AIOps ecosystem. [supra-wall.com](https://supra-wall.com)"}
]

for t in targets:
    upstream = t["upstream"]
    
    # Check open PRs for wiserautomation
    url = f"https://api.github.com/search/issues?q=state:open+author:wiserautomation+repo:{upstream}+type:pr"
    res = requests.get(url, headers=HEADERS)
    data = res.json()
    if data.get("total_count", 0) > 0:
        print(f"✅ PR ALREADY OPEN for {upstream}: {data['items'][0]['html_url']}")
    else:
        # Try to open PR
        create_url = f"https://api.github.com/repos/{upstream}/pulls"
        data_payload = {
            "title": t["title"],
            "head": t["head"],
            "base": "main",
            "body": t["body"]
        }
        res2 = requests.post(create_url, headers=HEADERS, json=data_payload)
        if res2.status_code == 201:
            print(f"🚀 SUCCESSFULLY CREATED PR for {upstream}: {res2.json()['html_url']}")
        else:
            # Fallback to master
            data_payload["base"] = "master"
            res3 = requests.post(create_url, headers=HEADERS, json=data_payload)
            if res3.status_code == 201:
                print(f"🚀 SUCCESSFULLY CREATED PR for {upstream} (master base): {res3.json()['html_url']}")
            else:
                print(f"❌ FAILED to create PR for {upstream}.")
                print(f"   main error: {res2.text[:200]}")
                print(f"   master error: {res3.text[:200]}")
