# Fine-Tuned Model Configuration

## Overview
Your system is now configured to use your fine-tuned model without any additional system prompts or instructions. The model will receive user questions directly.

## What Changed

### 1. Environment Configuration
Added `USE_FINETUNED_MODEL=true` to your `.env` file. This flag tells the system to:
- Skip all prompt crafting stages
- Remove system prompts from LLM calls
- Send user questions directly to your fine-tuned model

### 2. System Behavior
When `USE_FINETUNED_MODEL=true`:
- ✅ **No prompt engineering** - User questions go directly to your model
- ✅ **No system prompts** - Your fine-tuned model receives only the user's question
- ✅ **No instruction wrapping** - The model uses its fine-tuned knowledge
- ✅ **Works with all providers** - GROQ, OpenAI, DeepSeek, Gemini, Ollama

### 3. GROQ Support Added
- Added GROQ client configuration
- Your `LLM_MODEL=groq` setting is now fully supported
- GROQ API key from your `.env` will be used

## How to Use

### Enable Fine-Tuned Mode
```bash
# In your .env file
USE_FINETUNED_MODEL=true
```

### Disable Fine-Tuned Mode (Use Standard Prompts)
```bash
# In your .env file
USE_FINETUNED_MODEL=false
# or comment it out:
# USE_FINETUNED_MODEL=true
```

## Model Configuration

### Current Setup
```bash
LLM_MODEL=groq
GROQ_API_KEY=gsk_...
USE_FINETUNED_MODEL=true
```

### Supported Models
- **GROQ**: Set `LLM_MODEL=groq` and provide `GROQ_API_KEY`
- **OpenAI**: Set `OPENAI_API_KEY` 
- **DeepSeek**: Set `DEEPSEEK_API_KEY`
- **Gemini**: Set `GEMINI_API_KEY`
- **Ollama**: Set `OLLAMA_HOST` (for local models)

## Fallback Chain
If your primary model fails, the system will try (in order):
1. DeepSeek
2. OpenAI
3. Gemini
4. GROQ
5. Ollama

## Testing
To test your fine-tuned model:
1. Ensure `USE_FINETUNED_MODEL=true` in `.env`
2. Start the server: `python -m scripts.server.app`
3. Submit a question through the web interface
4. Check the console logs - you should see:
   ```
   [orchestrator] Fine-tuned model mode: Skipping prompt crafting
   [orchestrator] Fine-tuned model mode: Sending question directly without system prompts
   ```

## Troubleshooting

### Model not responding as expected?
- Verify `USE_FINETUNED_MODEL=true` is set in `.env`
- Check console logs for confirmation messages
- Ensure your API keys are valid

### Want to use custom prompts occasionally?
- Keep `USE_FINETUNED_MODEL=true` for general use
- Use the "Custom Prompt" feature in the web UI for specific cases
- The custom prompt will be appended to user questions (not used as system prompt)

### Need to switch back to standard mode?
- Set `USE_FINETUNED_MODEL=false` or remove the line
- System will resume using automatic prompt engineering

## Technical Details

### What Gets Skipped
1. **Prompt Crafting Stage**: The `craft_solver_prompt()` function is bypassed
2. **System Role Messages**: No system prompts added to API calls
3. **Instruction Wrapping**: User questions sent as-is

### Where Changes Were Made
- `scripts/orchestrator/prompt_orchestrator.py` - All solver functions
- `scripts/orchestrator/llm_clients.py` - Added GROQ client
- `.env` - Added USE_FINETUNED_MODEL flag

## Notes
- Your fine-tuned model should be trained to output valid JSON matching the expected schema
- If JSON parsing fails, the system will attempt to extract JSON from the response
- All existing features (voice generation, animation, etc.) continue to work normally
