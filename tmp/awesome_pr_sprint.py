import os, sys, time, requests, subprocess

PAT = "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"
HEADERS = {"Authorization": f"Bearer {PAT}", "Accept": "application/vnd.github+json"}

REPOS = [
    {
        "repo": "punkpeye/awesome-mcp-servers", 
        "header": "## Security", 
        "entry": "- **SupraWall MCP Plugin** - Deterministic policy enforcement and audit logging for MCP tool calls. Apache 2.0. [supra-wall.com](https://supra-wall.com)"
    },
    {
        "repo": "e2b-dev/awesome-ai-agents", 
        "header": "## Safety", 
        "entry": "- **SupraWall** - Runtime security layer for autonomous agents. Intercepts tool calls, enforces policies, vaults credentials, generates EU AI Act compliant audit trails. Apache 2.0. [supra-wall.com](https://supra-wall.com)"
    },
    {
        "repo": "e2b-dev/awesome-agent-ai",
        "header": "## Safety",
        "entry": "- **SupraWall** - Runtime security layer for autonomous agents. Intercepts tool calls, enforces policies, vaults credentials, generates EU AI Act compliant audit trails. Apache 2.0. [supra-wall.com](https://supra-wall.com)"
    },
    {
        "repo": "Trusted-AI/awesome-llm-security", 
        "header": "## Defense", 
        "entry": "- **SupraWall** - Runtime policy enforcement and audit trails for LLM/AI agents. [supra-wall.com](https://supra-wall.com)"
    },
    {
        "repo": "Instruction-Injection/awesome-prompt-injection", 
        "header": "## Mitigations", 
        "entry": "- **SupraWall** - Credential vault and policy enforcement prevents prompt injection credential leakage. [supra-wall.com](https://supra-wall.com)"
    },
    {
        "repo": "chenryn/awesome-aiops", 
        "header": "## Observability", 
        "entry": "- **SupraWall** - EU AI Act compliant audit trails and policy enforcement for AI operations. [supra-wall.com](https://supra-wall.com)"
    },
    {
        "repo": "kananaman/awesome-ai-safety", 
        "header": "## Governance", 
        "entry": "- **SupraWall** - Runtime control and compliance framework for autonomous agents. [supra-wall.com](https://supra-wall.com)"
    }
]

print("Launching the Global Awesome PR Sprint! 🚀 🥳\n")

for r in REPOS:
    repo = r['repo']
    name = repo.split('/')[1]
    print(f"🏁 Targeting: {repo}...")
    
    res = requests.get(f"https://api.github.com/repos/{repo}", headers=HEADERS)
    if res.status_code != 200:
        print(f"❌ Repo {repo} not found, skipping.\n")
        continue
        
    branch = res.json().get("default_branch", "main")
    
    # Fork
    print("   -> Forking to wiserautomation...")
    requests.post(f"https://api.github.com/repos/{repo}/forks", json={"organization":"wiserautomation"}, headers=HEADERS)
    time.sleep(7)
    
    # Clone
    clone_dir = f"/Users/alejandropeghin/Desktop/AntiG/SW-Private/SupraWall/tmp/{name}"
    subprocess.run(["rm", "-rf", clone_dir], capture_output=True)
    subprocess.run(
        ["git", "clone", "--depth", "1", f"https://{PAT}@github.com/wiserautomation/{name}.git", clone_dir],
        capture_output=True
    )
    
    readme_path = f"{clone_dir}/README.md"
    if not os.path.exists(readme_path): 
        print(f"❌ README.md not found in {repo}, skipping.\n")
        continue
        
    with open(readme_path, 'r') as f:
        content = f.read()
        
    if "supra-wall.com" in content:
        print(f"✅ SupraWall already in {repo}!\n")
        continue

    header = r['header']
    if header in content:
        parts = content.split(header, 1)
        new_content = parts[0] + header + "\n" + r['entry'] + "\n" + parts[1]
    else:
        new_content = content + "\n\n## Security & Safety\n" + r['entry'] + "\n"
        
    with open(readme_path, 'w') as f:
        f.write(new_content)
        
    print("   -> Pushing changes...")
    subprocess.run(["git", "checkout", "-b", "chore/suprawall-integration"], cwd=clone_dir, capture_output=True)
    subprocess.run(["git", "config", "user.name", "wiserautomation"], cwd=clone_dir)
    subprocess.run(["git", "config", "user.email", "engineering@wiserautomation.com"], cwd=clone_dir)
    subprocess.run(["git", "add", "README.md"], cwd=clone_dir)
    subprocess.run(["git", "commit", "-m", "feat: Add SupraWall security integration"], cwd=clone_dir, capture_output=True)
    subprocess.run(["git", "push", "origin", "chore/suprawall-integration", "--force"], cwd=clone_dir, capture_output=True)
    
    pr_data = {
        "title": f"feat: Add SupraWall to ecosystem list",
        "head": "wiserautomation:chore/suprawall-integration",
        "base": branch,
        "body": "Adding SupraWall to the repository integrations to provide your developer community with access to deterministic security guardrails and EU AI Act compliant audit trails.\n\nLearn more: https://supra-wall.com"
    }
    pr_res = requests.post(f"https://api.github.com/repos/{repo}/pulls", json=pr_data, headers=HEADERS)
    if pr_res.status_code == 201:
        print(f"✅ SUCCESS: PR Created -> {pr_res.json().get('html_url')}\n")
    else:
        err_data = pr_res.json()
        err_msg = err_data.get('message', '')
        if 'A pull request already exists' in err_msg:
             print(f"✅ PR already exists for {repo}!\n")
        else:
             print(f"❌ FAILED PR for {repo}: {err_msg}\n")
