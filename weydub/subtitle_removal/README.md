# Weydub Pro Subtitle Removal

A supplier sends you a product video with captions already burned into the picture. Before adding a new language, remove those captions and download the cleaned MP4. Full-frame Pro scans the entire picture: signs, prices and product labels can also be erased. When those must stay, use the [Weydub browser editor](https://weydub.com/subtitle-removal/) to select a smaller area.

## Connect your account

Enter your Weydub App Key and App Secret in the provider settings. The credential check does not create a job. This version uses **your own Weydub credits**; see [API setup](https://weydub.com/docs/api/) and [account rates](https://weydub.com/vip/pricing-detail/). Dify needs outbound HTTPS access to `api.zhaoli.com`, the GhostCut API used by Weydub.

## Clean a clip

1. Give **Remove burned-in subtitles** a direct HTTPS URL to a video you are allowed to process. A signed link is fine if it remains valid while Weydub retrieves the file. A webpage or private local file path will not work. Running the tool submits one billable job.
2. Save its `work_id` output. Connect that output to **Check removal result**, or paste the ID into a separate workflow run later. When `state` is `processing`, wait about five minutes and run **only the result tool** again. A timeout during submission can mean the job was accepted: check your Weydub history before submitting a second time.
3. When `state` is `ready`, open `video_url` to download the cleaned MP4 or pass the URL to the next step. Treat that link as private. When `state` is `failed`, look up the work ID in Weydub instead of polling again.

For a reproducible example, use the [15-second coffee audition clip](https://weydub.com/creator-kit/clips/wrong-cup/en.mp4?v=c6a45c49c92e) as `video_url`. To see what to look for before spending credits, compare [the original frames](https://weydub.com/creator-kit/comparison/comedy-original-grid.webp) with [the same frames after removal](https://weydub.com/creator-kit/comparison/comedy-clean-grid.webp) from the Weydub Creator Kit.

[Plugin source](https://github.com/JollyToday/GhostCut-auto_video_translation/tree/main/integrations/dify) · [Plugin privacy](PRIVACY.md) · Support: niumo@weydub.com
