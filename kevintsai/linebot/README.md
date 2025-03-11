## linebot

**Author:** [@kevintsai1202](https://github.com/kevintsai1202)
**Version:** 0.0.1
**Type:** extension

### Description
Follow these steps to integrate the Line Bot plugin:

1. **Create Provider and Messaging API channel**
  Line developers URL: https://developers.line.biz
  <img src="./_assets/2025-03-10 20 34 06.png" width="600" />

2. **Copy the Channel secret and Channel access token of the Messaging API**
  - Go to Basic settings.
  - Copy the Channel secret (if it hasn’t been created yet, click "issue" to generate it).
  <img src="./_assets/2025-03-10 21 07 14.png" width="600" />
  
  - Go to Messaging API.
  - Enable Use webhook
  - Copy the Channel access token (if it hasn’t been created yet, click "issue" to generate it).
  <img src="./_assets/2025-03-10 21 06 36.png" width="600" />

3. **Set Up Dify Line Bot Endpoint**
   - Set Endpoint name
   - Paste "Channel secret" and "Channel access token"
   - Select a Chat Workflow
   <img src="./_assets/2025-03-10 21 08 10.png" width="600" />

4. **Save and copy Line Bot webhook url**
  <img src="./_assets/2025-03-10 21 02 33.png" width="600" />

5. ** Set webhook url and verify **
  - Go back to the Messaging API page on Line Developers.
  - Paste the URL from the previous step into the Webhook URL.
  - Verify Line Bot
  <img src="./_assets/2025-03-10 21 03 50.png" width="600" />
  <img src="./_assets/2025-03-10 21 08 36.png" width="600" />

6. ** Use Line to add the Bot Basic ID, and you can chat with the Dify flow **
  <img src="./_assets/S__320659478.jpg" width="600" />

