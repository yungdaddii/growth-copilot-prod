# AI Provider Configuration Guide

Growth Co-pilot now supports multiple AI providers for enhanced analysis capabilities. You can use either Claude (Anthropic) or OpenAI models.

## Quick Setup

### Option 1: Claude 3.5 Sonnet (RECOMMENDED)
Claude 3.5 Sonnet is the latest and most capable model for analysis tasks, particularly good at understanding code and providing detailed insights.

1. Get your API key from [Anthropic Console](https://console.anthropic.com/)
2. Add to your `.env` file:
```env
CLAUDE_API_KEY=your-claude-api-key-here
CLAUDE_MODEL=claude-3-5-sonnet-20241022
```

### Option 2: OpenAI GPT-4o
The latest OpenAI model, significantly better than GPT-4-turbo.

1. Get your API key from [OpenAI Platform](https://platform.openai.com/api-keys)
2. Add to your `.env` file:
```env
OPENAI_API_KEY=your-openai-api-key-here
OPENAI_MODEL=gpt-4o
```

### Option 3: Use Both (Claude takes priority)
If both keys are provided, Claude will be used by default as it typically provides better analysis results.

## Available Models

### Claude Models (Anthropic)
- **claude-3-5-sonnet-20241022** - Latest Sonnet (Oct 2024) - BEST for analysis
- **claude-3-opus-20240229** - Most capable but slower
- **claude-3-sonnet-20240229** - Previous Sonnet version
- **claude-3-haiku-20240307** - Fastest and cheapest

### OpenAI Models
- **gpt-4o** - Latest model (Nov 2024) - Best OpenAI option
- **gpt-4o-mini** - Faster, cheaper alternative
- **gpt-4-turbo** - Previous generation
- **gpt-4** - Original GPT-4

## Performance Comparison

| Model | Speed | Quality | Cost | Best For |
|-------|-------|---------|------|----------|
| Claude 3.5 Sonnet | Fast | Excellent | Medium | Detailed analysis, code understanding |
| GPT-4o | Fast | Very Good | Medium | General analysis, quick responses |
| Claude 3 Opus | Slow | Excellent | High | Complex reasoning |
| GPT-4o-mini | Very Fast | Good | Low | Quick checks, budget usage |

## Implementation Details

The system automatically:
1. Detects which API keys are available
2. Selects the best available model
3. Falls back gracefully if no AI provider is configured
4. Logs which model is being used

### Priority Order
1. Claude (if CLAUDE_API_KEY is set)
2. OpenAI (if OPENAI_API_KEY is set)
3. Fallback mode (pattern-based responses)

### Code Architecture
```python
# backend/app/core/ai_providers.py
- AIProvider (abstract base class)
- OpenAIProvider (supports all GPT models)
- ClaudeProvider (supports all Claude models)
- AIProviderFactory (creates appropriate provider)

# Usage in analyzers
from app.core.ai_providers import AIProviderFactory

provider = AIProviderFactory.create_provider()
response = await provider.generate_completion(messages, temperature=0.7)
```

## Migration from Old Setup

If you were using the old GPT-4 setup:

1. Your existing `OPENAI_API_KEY` will still work
2. The system automatically upgrades old model names:
   - `gpt-4` → `gpt-4o`
   - `gpt-4-turbo-preview` → `gpt-4-turbo`
   - `gpt-3.5-turbo` → `gpt-4o-mini`

## Cost Considerations

### Approximate Costs (per 1M tokens)
- **Claude 3.5 Sonnet**: $3 input / $15 output
- **GPT-4o**: $2.50 input / $10 output
- **Claude 3 Haiku**: $0.25 input / $1.25 output
- **GPT-4o-mini**: $0.15 input / $0.60 output

### Per Analysis Estimate
Each website analysis uses approximately:
- Input: ~2,000 tokens (context + prompts)
- Output: ~1,500 tokens (responses)
- **Cost per analysis**: $0.02-0.07 depending on model

## Troubleshooting

### No AI Provider Available
If you see "No AI provider configured" in logs:
1. Check your `.env` file has either CLAUDE_API_KEY or OPENAI_API_KEY
2. Verify the API key is valid
3. Restart the backend: `docker-compose restart backend`

### Model Not Found
If you get a model error:
1. Check you're using a valid model name from the list above
2. Ensure your API key has access to that model
3. Some models require special access (e.g., Claude 3 Opus)

### Rate Limiting
Both providers have rate limits:
- **Claude**: 40,000 tokens/minute for most tiers
- **OpenAI**: Varies by tier, typically 90,000 tokens/minute

The system handles rate limiting gracefully with retries.

## Testing Your Configuration

After setting up, test with:
```bash
# Check logs to see which model is active
docker logs growthcopilot-backend | grep "AI Conversation Engine initialized"

# Should show something like:
# "AI Conversation Engine initialized with: claude-3-5-sonnet-20241022"
```

## Recommendations

1. **For Best Results**: Use Claude 3.5 Sonnet
   - Superior at understanding website structure
   - Better at identifying specific competitors
   - More accurate feature comparisons

2. **For Budget**: Use GPT-4o-mini
   - Still provides good analysis
   - 10x cheaper than premium models
   - Fast response times

3. **For Speed**: Use Claude 3 Haiku or GPT-4o-mini
   - Sub-second response times
   - Good for high-volume usage

## Future Models

The system is designed to easily support new models. When new versions are released:
- Claude 3.5 Opus (coming soon)
- GPT-4.5 or GPT-5 (future)
- Other providers (Gemini, Mistral, etc.)

Just update the model name in your `.env` file!