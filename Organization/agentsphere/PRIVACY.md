# Privacy Policy for AgentSphere Plugin

## 1. Data Collection
The AgentSphere plugin collects the following data to enable its functionality:
- **API Key**: Your AgentSphere API key is collected to authenticate requests to AgentSphere services. This key is used solely for authorization and is not stored beyond the active session.
- **User Inputs**: Code snippets, commands, file paths, and other operational parameters entered by users are temporarily processed to execute tasks (e.g., running code, uploading files) via AgentSphere's cloud sandboxes.
- **Execution Logs**: Basic metadata (e.g., task duration, success/failure status) is generated during task execution for debugging purposes, but does not include sensitive user content.

## 2. Data Storage
- **API Key**: Stored temporarily in the plugin's runtime memory only during active use. It is never persisted to disk or cloud storage.
- **User Inputs & Logs**: Processed in real-time and discarded immediately after task completion. No user-generated content (code, files, commands) is stored by the plugin itself.


## 3. Data Sharing
- The plugin solely shares data with AgentSphere's servers to fulfill user requests (e.g., executing code in their sandboxes). No third-party services outside of AgentSphere are involved.
- Data shared with AgentSphere is governed by their privacy practices, as outlined in their official documentation.

## 4. Data Security
- **API Key Protection**: Transmitted via encrypted HTTPS channels and never exposed in logs or unencrypted storage.
- **Input Sanitization**: User inputs (code, commands) are validated to prevent malicious operations, in compliance with AgentSphere's security protocols.
- **Isolation**: All tasks are executed in isolated cloud sandboxes provided by AgentSphere, ensuring no cross-user data leakage.

## 5. User Control
Users can revoke their AgentSphere API key at any time via the AgentSphere dashboard, which immediately stops the plugin's ability to make authenticated requests.