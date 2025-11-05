## Tencent RTC Conversational AI

  

**Author:** [Yuyang Wu](https://www.linkedin.com/in/yuyang-wu/)

**Version:** 0.0.1

**Plugin Type:** extension

**Github:** https://github.com/Xcode-wu/tencentrtc-dify-conai
  

## Description

  

Tencent RTC Conversational AI transforms your Dify agent into a Voice AI agent with real-time speech-to-text (STT) and text-to-speech (TTS) capabilities powered by Tencent RTC.
  

## Configuration


The plugin requires the following configuration parameters:

  
-  **Dify App**

Select a Dify agent from your library to turn into a voice assistant.

  

-  **TCloud SecretId**

Your Tencent Cloud SecretId for API authentication. Get it from [Tencent Cloud Console - API Keys](https://console.cloud.tencent.com/cam/capi).

  

-  **TCloud SecretKey**

Your Tencent Cloud SecretKey for API authentication. Keep this secure.

  

-  **Region**

The Tencent Cloud region for your TRTC service (default: `ap-singapore`). 

  
-  **TRTC SdkAppId**

Your TRTC application ID. Create one in [TRTC Console](https://trtc.io/).

  

-  **TRTC SecretKey**

The secret key for your TRTC application. Get it from your TRTC application settings.


-  **STT Config  (JSON)**

Configuration for Speech-to-Text service in JSON format. Refer to [TRTC STT documentation](https://trtc.io/document/69592?product=rtcengine&menulabel=core%20sdk&platform=web) for details.

Example:

```json
{
"STTType":"deepgram",
"ApiKey":"xxx",
"Model":"nova-2"
}
```

-  **STT Language**

The BCP-47 language tag for speech recognition (default: `en`). 


  -  **TTS Config  (JSON)**

Configuration for Text-to-Speech service in JSON format. Refer to [TRTC TTS documentation](https://trtc.io/document/68340?product=rtcengine&menulabel=core%20sdk&platform=web) for details.

Example:

```json
{  
"TTSType": "cartesia",   
"Model": "sonic-3",   
"APIKey": "xxx",
"VoiceId": "e07c00bc-4134-4eae-9ea4-1a55fb45746b" 
}
```


-  **Endpoint API Key** (Optional)

An API key to protect your LLM proxy endpoint for additional security.

  

## Usage

  

Once configured, the plugin provides the following endpoints:

  

#### Web Interface

  

Use the following URL to interact with your voice AI:

`https://<your-plugin-url>/trtc-web/demo.html`



## Support 

For issues or questions:

- Tencent RTC Support: [https://trtc.io/](https://trtc.io/)
- Tencent RTC Conversational AI Documentation: [https://trtc.io/document/64658?product=rtcengine&menulabel=core%20sdk&platform=web](https://trtc.io/document/64658?product=rtcengine&menulabel=core%20sdk&platform=web)