# Development and validation

This plugin uses fixed Pillow image operations, with no user-supplied code, shell commands, database access, outbound API calls, or external credentials. The only local file read by the processor is its bundled preset JSON. Input image bytes are read through the Dify file abstraction; PNG results are returned through the SDK blob message API.

## Reproduce the standalone checks

Use Python 3.12 in a virtual environment, install `requirements.txt`, then run:

```sh
python -m unittest discover -p test_plugin.py -v
```

The checks exercise both RGB and RGBA inputs for all three presets, PNG dimensions, transparent corners, opaque centers, output filenames and actual SDK file messages. They also check missing images, empty/corrupt/oversized files, unknown presets, and the 16-megapixel limit. These are synthetic images, with no private artwork or credentials.

Local validation on Python 3.12, Pillow 13.0.0 and Dify SDK 0.11.0 passed. Plugin, provider and tool YAML were also validated against the SDK schemas. Six RGB/RGBA results matched the original image-processing implementation byte-for-byte in a separate local comparison.

## Live-environment limitations

A Dify Community Edition instance rejected installation of the unsigned package because signature verification was enabled. No verification policy was disabled, and the plugin was not executed on that instance. An independent draft workflow verified that its code sandbox had no `PIL` package; this is separate from the plugin runtime and is not an end-to-end plugin test.

Dify Cloud and a live end-to-end workflow using this plugin have not been tested. Reviewers should treat these as validation gaps, not as successful deployment evidence.

## Packaging

The distribution archive contains only runtime Python files, YAML declarations, bundled presets, icon and required documentation. Tests and this development note are source-only, outside the runtime archive. It contains no `.env`, credentials, private keys, virtual environments, caches, logs, executables, test artwork, or company platform modules.
