# Lightweight Cache (Redis-style)

An in-process key-value cache with Redis-style operations for Dify workflows.

## Features

- Redis-style SET / GET / DEL / EXISTS operations with TTL expiry
- No real Redis server required — runs entirely in-process
- Ideal for air-gapped/intranet environments
- Data is persisted to disk and survives container restarts

## Usage

Add the cache tools (**SET**, **GET**, **DEL**, **EXISTS**) to your Dify workflow to store and retrieve key-value data across steps.

## Privacy

All data is stored locally within the Dify plugin container. No data is sent to any external service. See `PRIVACY.md` for details.
