# AI Module

OpenRouter AI integration for AI Workspace.

## Overview

This module provides AI-powered features for gear management:
- **Chat Interface**: Conversational AI to help manage gear items and containers
- **Structured Output**: AI returns JSON that automatically updates the database
- **Token Management**: Users can use their own OpenRouter API tokens
- **Caching**: PostgreSQL-based caching to reduce costs
- **History Tracking**: Full audit trail of AI interactions with token usage and costs

## Configuration

Required environment variables (see `backend/.env.example`):

```bash
AI_ENABLED=true
OPENROUTER_API_KEY=your_key_here
AI_TOKEN_ENCRYPTION_KEY=generate_with_fernet
AI_CACHE_ENABLED=true
AI_CACHE_TTL_CLASSIFY=7
AI_CACHE_TTL_EMBED=30
```

Generate encryption key:
```bash
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

## Access Control

**Phase 1**: AI features are **admin-only**.
Only users with `is_admin=True` can access AI endpoints.

## Architecture

### Module Structure

```
ai/
├── __init__.py              # Module exports
├── router.py                # Main router with sub-routers
├── db_models.py             # SQLAlchemy models (3 tables)
├── schemas.py               # Pydantic request/response models
├── exceptions.py            # AI-specific exceptions
├── dependencies.py          # FastAPI dependencies (admin check)
├── README.md                # This file
│
├── routers/
│   ├── __init__.py
│   ├── chat.py              # Chat interface endpoints
│   ├── settings.py          # User settings endpoints
│   └── history.py           # History endpoints
│
├── services/
│   ├── __init__.py
│   ├── chat_service.py      # Chat orchestration
│   ├── settings_service.py  # User settings management
│   └── history_service.py   # History tracking
│
├── repositories/
│   ├── __init__.py
│   ├── settings_repository.py
│   ├── history_repository.py
│   └── cache_repository.py
│
├── providers/
│   ├── __init__.py
│   ├── base.py              # Abstract base provider
│   └── openrouter.py        # OpenRouter implementation (OpenAI SDK)
│
├── cache/
│   ├── __init__.py
│   └── postgres_cache.py    # PostgreSQL cache service
│
├── parsers/
│   ├── __init__.py
│   └── structured_output.py # JSON parsing & validation
│
├── prompts/
│   ├── __init__.py
│   ├── system_prompts.py    # System prompt templates
│   └── examples.py          # Few-shot examples
│
└── utils/
    ├── __init__.py
    ├── encryption.py        # Token encryption (Fernet)
    ├── models_config.py     # 10 AI models configuration
    └── token_calculator.py  # Token counting utilities
```

### Database Schema

#### ai_user_settings
- `id` (UUID, PK)
- `user_id` (VARCHAR(36), FK to users, UNIQUE)
- `use_own_token` (BOOLEAN)
- `encrypted_api_token` (TEXT, nullable)
- `selected_model` (VARCHAR(255))
- `context_fields` (JSONB) - which fields to include in AI context
- `max_tokens` (INTEGER, nullable)
- `temperature` (REAL, default 1.0)
- `created_at`, `updated_at`

#### ai_history
- `id` (UUID, PK)
- `user_id` (VARCHAR(36), FK to users)
- `operation_type` (VARCHAR(50)) - 'chat', 'classify', 'embed', etc.
- `model` (VARCHAR(255))
- `prompt_tokens`, `completion_tokens`, `total_tokens` (INTEGER)
- `cost_usd` (REAL, nullable)
- `input_data` (JSONB) - user message and context
- `output_data` (JSONB) - AI response
- `metadata` (JSONB, nullable)
- `created_at`

#### ai_cache
- `cache_key` (VARCHAR(64), PK) - SHA-256 hash
- `operation_type` (VARCHAR(50))
- `model` (VARCHAR(255))
- `cached_data` (JSONB)
- `hit_count` (INTEGER, default 0)
- `created_at`, `expires_at`

## Usage

### Chat Interface

```python
# POST /api/ai/chat
{
  "message": "Add a flashlight to my EDC bag",
  "context": {
    "container_id": "01JEXAMPLE123",
    "include_items": true
  }
}

# Response
{
  "message": "I've added a flashlight to your EDC bag...",
  "structured_output": {
    "action": "create_item",
    "data": {
      "name": "Flashlight",
      "category": "tools",
      "priority": "high"
    }
  },
  "tokens_used": 245,
  "cost_usd": 0.00123
}
```

### User Settings

```python
# GET /api/ai/settings
# PUT /api/ai/settings
{
  "use_own_token": true,
  "api_token": "sk-or-v1-...",
  "selected_model": "openai/gpt-4o-mini",
  "context_fields": {
    "container_name": true,
    "items_list": true,
    "total_weight": false
  }
}
```

## Development

### Adding New Models

Edit `utils/models_config.py`:

```python
MODELS = [
    {
        "id": "openai/gpt-4o-mini",
        "name": "GPT-4o Mini",
        "provider": "OpenAI",
        "context_length": 128000,
        "cost_per_1m_input": 0.15,
        "cost_per_1m_output": 0.60,
    },
    # ... add more models
]
```

### Testing

```bash
# Run AI module tests
pytest tests/modules/ai -v

# Test specific functionality
pytest tests/modules/ai/test_chat.py -v
```

## Future Phases

- **Phase 2**: Chat interface with structured output (✅ Current)
- **Phase 3**: Classification & auto-tagging
- **Phase 4**: Embeddings & semantic search
- **Phase 5**: Plans & limits system
- **Phase 6**: Public access (non-admin users)

## References

- [OpenRouter Documentation](https://openrouter.ai/docs)
- [OpenAI SDK](https://github.com/openai/openai-python) (used for OpenRouter)
- [Fernet Encryption](https://cryptography.io/en/latest/fernet/)
