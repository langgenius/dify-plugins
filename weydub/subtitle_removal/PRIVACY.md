# Plugin privacy

The plugin sends your source video URL to Weydub's processing service at `api.zhaoli.com`. That service retrieves the video and produces the cleaned result. Checking a job sends the work ID to the same service. The credential check requests an account balance and discards the response.

The App Key identifies your account. The plugin uses the App Secret locally to sign requests; it does not transmit the secret. It has no separate database, analytics or application logs. Work IDs and result URLs are returned to your Dify workflow and can appear in its run history. Anyone with access to a signed media URL may be able to download it. Set the appropriate access controls on your workflow and storage.

For processing and account data handled by Weydub, see the [Weydub privacy policy](https://weydub.com/Privacy_Policy_en.pdf). Contact: niumo@weydub.com.
