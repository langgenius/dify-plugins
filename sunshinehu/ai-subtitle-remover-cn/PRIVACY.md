# Privacy information

This plugin sends the configured user number and API key, and the arguments of the invoked tool, to the 550W Open API at `https://www.550wai.cn`. Uploaded image and video operations transmit the selected media file. For videos, the plugin reads the Dify-provided file URL into bounded temporary storage, forwards the file to 550W, and closes the temporary file after the upload attempt. Other arguments include a public share link or direct video URL, video metadata, optional coordinates, and an idempotency identifier. The plugin does not send unrelated Dify conversation text. It receives the service response and returns it to the calling Dify application.

Dify stores provider credentials under its own credential handling. This plugin does not write credentials to local files, log them, or send them to another service. The plugin contains no analytics or advertising SDK. Service-side processing and retention are governed by the [550W privacy policy](https://eraser.550wai.com/privacy/) and [terms](https://eraser.550wai.com/terms/); users should review those pages before sending media.

Users can remove the provider credentials in Dify. To request deletion of service-side data or ask a privacy question, use the contact method listed in the [550W privacy policy](https://eraser.550wai.com/privacy/). Deleting a Dify plugin credential does not by itself delete tasks already sent to the service.

This is the independent China provider. API key management and credit purchase use qzm.550wai.cn. The shared 550W service and the service policy links above remain the same; changing the regional listing does not imply a different processing backend.
