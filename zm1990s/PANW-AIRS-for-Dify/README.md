## PANW AI Security

**Author:** Matt Zhang

**Version:** 0.0.2

**Type:** tool

### Overview

This plugin is a PANW AI Runtime Security API security tool designed for the Dify platform, aiming to enhance the security of AI model and interactions. By integrating Palo Alto Networks' advanced cloud threat detection services, it provides users with comprehensive security protection.

### Prerequisites

Authorized users should refer to the [AI Runtime Security: API Intercept Overview](https://docs.paloaltonetworks.com/ai-runtime-security/activation-and-onboarding/ai-runtime-security-api-intercept-overview) to complete the configuration of AI Runtime Security.

If you have not yet been authorized, please [contact our Palo Alto Networks account manager](https://www.paloaltonetworks.com/company/contact-support).

### Main Features

- **Prompt Detection**: Scans user inputs in Dify applications to prevent prompt injection, large model DoS attacks, and unsafe URLs, ensuring the secure operation of AI models.
- **Model and Data Protection**: Scans the outputs of large models to prevent accidental leakage of sensitive data such as PII; prevents large models from returning malicious URLs or malicious content.
- **Flexible Integration**: Seamlessly integrates into Dify's existing architecture without requiring customized modifications to the model, supporting various integration methods such as workflows and Agents.

### Basic Usage Example

#### Installation and Authorization

Install the plugin via **Marketplace/Github/Local Plugin**, and after installation, click "Authorize" to fill in the authentication information.

![img1](_assets/img1-en.png)

#### Calling in Chatflow

You can call the plugin in Chatflow to retrieve input and output content separately. It is also necessary to use "conditional branches" for judgment. If the detection result includes "allow", the workflow continues; otherwise, static content is returned, the and workflow is stopped.

![img2](_assets/img2-en.png)

The following is an example of calling the input side tool:

![img3](_assets/img3-en.png)

The specific parameters are described as follows:

- **Input Check or Output Check?** The PANW AIRS Prompt/Response identifier is used to distinguish whether the content to be checked belongs to input or output.
- **App Name (Optional)**: The name of the Chatflow/Agent, used for logging purposes.
- **User Name (Optional)**: The user identifier for the current application, used for logging purposes.
- **Model Name (Optional)**: The name of the model used by the current application, used for logging purposes.
- **PANW AIRS Profile Name Override (Optional)**: If you want to use a different Profile for this application, you can adjust it through this parameter. The default will use the globally configured Profile Name.

The input judgment component is configured as follows:

![img4](_assets/img4-en.png)

The following is an example of calling the output side tool:

![img5](_assets/img5-en.png)

The output judgment component is configured as follows:

![img6](_assets/img6-en.png)

#### Calling in Agent

![img7](_assets/img7-en.png)

Prompt examples:

> You are a personal information inquiry chatbot.
>
> 
>
> You need to chat with users. Before chatting, you should call the `palo_alto_networks_ai_security_api` tool to check the user's input. If the detection result includes "block", reply to the user with "Input is prohibited", otherwise answer the question normally.
>
> 
>
> If the user is asking about information related to Matt, you need to query the knowledge base for relevant content.
>
> 
>
> Before answering the question, you should call the `palo_alto_networks_ai_security_api` tool to check the output. If the detection result includes "block", reply to the user with "Output is prohibited", otherwise answer the question normally.

### Simple Demo

![img8](_assets/img8-en.png)