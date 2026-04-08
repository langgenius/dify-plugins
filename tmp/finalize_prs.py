import os
import subprocess
import requests
import time

TOKEN = "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"
HEADERS = {
    "Authorization": f"Bearer {TOKEN}",
    "Accept": "application/vnd.github.v3+json"
}

targets = [
    {
        "upstream": "kyrolabs/awesome-langchain",
        "repo_name": "awesome-langchain",
        "section": "## Agents",
        "entry": "- **SupraWall** - Runtime security layer for autonomous agents. Intercepts tool calls, enforces policies, vaults credentials, generates EU AI Act compliant audit trails. Apache 2.0. [supra-wall.com](https://supra-wall.com)",
        "pr_title": "feat: Add SupraWall to Agents section",
        "pr_body": "Adding SupraWall runtime security."
    },
    {
        "upstream": "chenryn/aiops-handbook",
        "repo_name": "aiops-handbook",
        "section": "## Observability", # Fallback to simply appending if not found
        "entry": "- **SupraWall** - Runtime security layer for AIOps and autonomous agents. Intercepts tool calls, enforces policies, vaults credentials. Apache 2.0. [supra-wall.com](https://supra-wall.com)",
        "pr_title": "feat: Add SupraWall observability",
        "pr_body": "Adding SupraWall to AIOps ecosystem."
    }
]

def run_cmd(cmd):
    subprocess.run(cmd, shell=True, check=True)

for t in targets:
    upstream = t["upstream"]
    repo_name = t["repo_name"]
    print(f"\n🚀 Processing {upstream}...")
    
    # 1. Fork
    print("Forking repository...")
    requests.post(f"https://api.github.com/repos/{upstream}/forks", headers=HEADERS)
    time.sleep(3) # Wait for fork to be created
    
    # 2. Clone fork
    if os.path.exists(repo_name):
        run_cmd(f"rm -rf {repo_name}")
        
    print("Cloning fork...")
    run_cmd(f"git clone https://{TOKEN}@github.com/wiserautomation/{repo_name}.git")
    
    os.chdir(repo_name)
    
    # 3. Create branch
    branch_name = "feat/suprawall-integration"
    run_cmd(f"git checkout -b {branch_name}")
    run_cmd("git config user.name 'wiserautomation'")
    run_cmd("git config user.email 'engineering@wiserautomation.com'")
    
    # 4. Patch README.md
    print("Patching README.md...")
    readme_path = "README.md"
    if os.path.exists(readme_path):
        with open(readme_path, "r") as f:
            content = f.read()
            
        if "supra-wall.com" not in content:
            if t["section"] in content:
                content = content.replace(t["section"], f"{t['section']}\n{t['entry']}")
            else:
                # If section not found, append to the end
                content += f"\n\n## Security / Observability\n{t['entry']}\n"
                
            with open(readme_path, "w") as f:
                f.write(content)
        
        # 5. Commit and Push
        print("Committing and pushing...")
        run_cmd("git add README.md")
        try:
            run_cmd(f"git commit -m '{t['pr_title']}'")
            run_cmd(f"git push origin {branch_name} --force")
        except subprocess.CalledProcessError:
            print("No changes to commit or push failed.")
            
    os.chdir("..")
    
    # 6. Create PR via API
    print("Creating Pull Request...")
    create_url = f"https://api.github.com/repos/{upstream}/pulls"
    data_payload = {
        "title": t["pr_title"],
        "head": f"wiserautomation:{branch_name}",
        "base": "main",
        "body": t["pr_body"]
    }
    res = requests.post(create_url, headers=HEADERS, json=data_payload)
    if res.status_code == 201:
        print(f"✅ SUCCESSFULLY CREATED PR for {upstream}: {res.json()['html_url']}")
    else:
        # Fallback to base master
        data_payload["base"] = "master"
        res_master = requests.post(create_url, headers=HEADERS, json=data_payload)
        if res_master.status_code == 201:
            print(f"✅ SUCCESSFULLY CREATED PR for {upstream} (master base): {res_master.json()['html_url']}")
        else:
            print(f"❌ FAILED to create PR for {upstream}.")
            print(f"   Error: {res.text[:200]}")
