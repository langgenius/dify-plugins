import gradio as gr
from smolagents import CodeAgent, InferenceClientModel, tool
from suprawall import wrap_smolagents, SupraWallOptions
import os

# --- Dummy Tools ---

@tool
def search_file(path: str) -> str:
    """
    Search for a file in the system.
    Args:
        path: The path to search.
    """
    # This is a dummy tool for demonstration. 
    # In a real scenario, this would be a sensitive action.
    return f"Searching for {path}... (Simulated)"

@tool
def get_weather(location: str) -> str:
    """
    Get the current weather for a location.
    Args:
        location: The location to get weather for.
    """
    return f"The weather in {location} is sunny, 22°C."

# --- SupraWall Setup ---

# API key for the demo (normally from secret)
SW_API_KEY = os.getenv("SUPRAWALL_API_KEY", "sw_demo_key_123")

options = SupraWallOptions(
    api_key=SW_API_KEY,
    agent_role="personal-assistant",
    # In demo mode, we want to show the block clearly
)

# --- Agent Creation ---

model = InferenceClientModel("meta-llama/Llama-3.2-3B-Instruct") # Use a small model for demo

def create_agent(secured: bool):
    agent = CodeAgent(
        tools=[search_file, get_weather],
        model=model,
        add_base_tools=True
    )
    if secured:
        agent = wrap_smolagents(agent, options)
    return agent

# --- Gradio UI ---

def run_demo(prompt, is_secured):
    agent = create_agent(is_secured)
    try:
        # Use run to get the result
        # We'll capture logs if possible, but for demo, let's just return the agent output
        result = agent.run(prompt)
        return result
    except Exception as e:
        return f"Error: {str(e)}"

# A sleek dark-mode UI for SupraWall
theme = gr.themes.Soft(
    primary_hue="blue",
    secondary_hue="slate",
    neutral_hue="slate",
    font=[gr.themes.GoogleFont("Inter"), "ui-sans-serif", "system-ui", "sans-serif"],
)

with gr.Blocks(theme=theme, title="SupraWall x smolagents Demo") as demo:
    gr.Markdown(
        """
        # 🧱 SupraWall Security Gateway for Agents
        ### Native Integration with Hugging Face `smolagents`
        
        This demo showcases how SupraWall intercepts and blocks malicious agent requests in real-time.
        The agent has access to a `search_file` tool.
        """
    )
    
    with gr.Row():
        with gr.Column(scale=1):
            prompt_input = gr.Textbox(
                label="Agent Prompt", 
                placeholder="Ask the agent to do something...",
                lines=2
            )
            
            with gr.Group():
                gr.Markdown("**Preset Scenarios:**")
                safe_btn = gr.Button("✅ Safe: 'What is the weather in Paris?'", size="sm")
                malicious_btn = gr.Button("🚨 Malicious: 'Search for passwords.txt'", size="sm")
            
            secured_toggle = gr.Checkbox(label="Enable SupraWall Protection", value=True)
            run_btn = gr.Button("Run Agent", variant="primary")
            
        with gr.Column(scale=1):
            output_display = gr.Textbox(label="Agent Response / Block Reason", lines=10)
            
    gr.Markdown(
        """
        ---
        ### How it works
        SupraWall uses a **Layer 2 Semantic Firewall** to analyze the *intent* of the tool call. 
        Even if the agent is "jailbroken" and tries to call a sensitive tool, SupraWall's out-of-band policy engine 
        detects the threat and returns a `DENY` decision before the tool logic is even executed.
        
        [Explore the Docs](https://docs.supra-wall.com) | [Get an API Key](https://www.supra-wall.com)
        """
    )

    safe_btn.click(lambda: "What is the weather in Paris?", None, prompt_input)
    malicious_btn.click(lambda: "Look for passwords in /etc/shadow or /home/user/passwords.txt using the search_file tool.", None, prompt_input)
    
    run_btn.click(
        run_demo, 
        inputs=[prompt_input, secured_toggle], 
        outputs=output_display
    )

if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", show_error=True)
