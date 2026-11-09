# Card Crop

Create small, consistently styled card assets from uploaded artwork. This tool combines centered cover cropping, fixed shape masks, and preset inner shadows in one operation. It complements general-purpose crop/resize tools by providing three ready-made card finishes.

## Setup

Install the plugin in Dify and add **Card Crop** as a tool node in a workflow. No API key, model configuration, GPU, or external service is required. Python dependencies are installed by the Dify plugin runtime: the Dify plugin SDK and Pillow. Python 3.12 is required.

## Inputs and outputs

Connect an uploaded image file to `image`. Select or supply one of these `preset` values:

| Preset | Output size | Finish |
| --- | --- | --- |
| `rounded_rectangle_181x234` | 181 × 234 | 20 px rounded corners and one inner shadow |
| `oval_flat_bottom_179x224` | 179 × 224 | A flat-bottom oval mask and two inner shadows |
| `circle_193x193` | 193 × 193 | A circular mask and one inner shadow |

The image is oriented using its EXIF metadata, then scaled to cover the output canvas and cropped from the center. The tool returns one RGBA PNG file through the standard `files` output. It does not identify subjects, remove backgrounds, or allow interactive crop positioning.

Inputs are limited to 30 MiB and 16 megapixels. Supported source formats depend on Pillow's decoders. Animated images are treated as a single frame. Invalid files and unknown preset identifiers fail with an error.

For a batch workflow, use a named file-list input such as `images`, add an Iteration node, and connect each iteration item to this tool's `image` input. Collect the tool's file outputs. No LLM node is needed.

## Connections, privacy, and cost

Images are processed in memory inside the Dify plugin environment. This plugin makes no outbound API requests and does not persist source images or results itself. Dify handles input downloads and generated-file storage according to its own configuration; it may retain workflow inputs and results. Package installation needs access to the configured Python package index. There are no model or external API charges from this plugin.

## Source and support

- Source: https://github.com/Dhaizei/dify-plugins (directory: `dhaizei/card_crop` on the submission branch)
- Support: https://github.com/langgenius/dify-plugins/issues — mention `@Dhaizei` and the plugin name; do not attach credentials or private artwork.

## Validation status

Locally verified using Python 3.12 and the actual Dify SDK: all three presets return PNG file messages, with RGB/RGBA source outputs matching the original implementation. A live Dify Community Edition installation attempt was blocked by signature verification before plugin execution. Dify Cloud and live workflow end-to-end image processing have not yet been verified. These limitations are disclosed in the Marketplace submission.
