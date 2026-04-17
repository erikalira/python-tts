# Bot/Desktop HTTP Contract

This guide documents the durable HTTP contract between the Windows Desktop App
and the Discord bot runtime.

## Why this exists

The repository contains two independent applications:

- Discord bot
- Windows Desktop App

They communicate through local HTTP endpoints exposed by the bot. The wire
format must remain explicit so both runtimes can evolve without depending on
hidden field conventions.

## Endpoints

### `GET /health`

Purpose: liveness and reachability check used by the Desktop App.

Success payload:

```json
{
  "status": "healthy"
}
```

### `GET /voice-context`

Purpose: detect the current guild/channel for a specific Discord member.

Query params:

- `member_id`: preferred identifier
- `user_id`: accepted alias for compatibility

Success payload:

```json
{
  "success": true,
  "code": "ok",
  "member_id": 123,
  "guild_id": 456,
  "guild_name": "Guild A",
  "channel_id": 789,
  "channel_name": "Sala 1"
}
```

Known failure payloads:

```json
{
  "success": false,
  "code": "member_required",
  "message": "member id is required"
}
```

```json
{
  "success": false,
  "code": "not_in_channel",
  "message": "user is not connected to a voice channel"
}
```

### `POST /speak`

Purpose: enqueue or execute speech through the bot runtime.

Request payload:

```json
{
  "text": "hello",
  "member_id": "123",
  "guild_id": 456,
  "channel_id": 789,
  "config_override": {
    "engine": "edge-tts",
    "language": "pt-BR",
    "voice_id": "pt-BR-FranciscaNeural",
    "rate": 210
  }
}
```

Notes:

- `member_id` is sent by the Desktop App as configured text and normalized by
  the bot before reaching the use case.
- `guild_id` and `channel_id` remain optional.
- `config_override` is optional and partial values are merged against the bot's
  resolved base config.

Response behavior:

- the endpoint keeps returning plain text plus HTTP status, preserving the
  current external behavior
- typed request parsing and response mapping now happen before final
  serialization at the HTTP boundary

## Implementation rule

- DTOs define the cross-runtime contract
- transports parse JSON into DTOs before application/runtime code consumes it
- presenters/controllers may serialize DTOs into JSON or text only at the final
  HTTP boundary
