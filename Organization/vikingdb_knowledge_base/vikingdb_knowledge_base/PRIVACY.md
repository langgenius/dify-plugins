## Privacy

This privacy policy explains how the VikingDB Knowledge Base Endpoint plugin ("the plugin") handles data when connecting Dify with VikingDB Knowledge Base.

### Data Collection and Transmission
The plugin acts as a connector between Dify and VikingDB Knowledge Base and:

- Does not store any data locally or persistently within the plugin
- Transmits all data securely via HTTPS protocol
- Only processes data temporarily in memory during request handling

### Data Handled
The following types of data pass through the plugin:

1. VikingDB Credentials:
   - VikingDB Access Key
   - VikingDB Secret Access 
   
   These credentials are stored and managed by Dify's secure credential storage system.

2. Query Data:
   - Search queries and parameters sent from Dify to VikingDB 
   - Search results returned from VikingDB to Dify
   
   This data is stored and managed by Dify and VikingDB according to their respective privacy policies.

### Data Storage
- The plugin itself maintains no data storage
- All persistent data storage is handled by either:
  - Dify (credentials, queries, results)
  - VikingDB (knowledge base content, search indices)

### Third-Party Services
This plugin relies on:
- VikingDB Knowledge Base service
- Dify 

Users should refer to the privacy policies of these services for information about how they handle data:

- VikingDB Privacy Notice (https://www.volcengine.com/docs/6256/64902)
- Dify's privacy policy (https://dify.ai/privacy)
