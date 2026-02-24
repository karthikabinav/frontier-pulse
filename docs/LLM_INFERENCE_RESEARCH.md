# LLM Inference Research Notes (V1)

Date: 2026-02-21

## Objective
Pick a practical V1 inference strategy for aifrontierpulse with low recurring cost, high flexibility, and good enough quality for structured extraction.

## Decision Summary
- Primary: local inference via Ollama.
- Optional fallback: OpenRouter for free-tier/low-cost cloud routing.
- V1 model policy: one model used for extraction and synthesis, configurable for future split.
- Default local model: `qwen2.5:7b-instruct`.
- Default cloud fallback model: `meta-llama/llama-3.1-8b-instruct:free`.

## Why
- Local-first preserves cost control and privacy alignment.
- OpenRouter fallback reduces single-point-of-failure risk when local runtime is unavailable or overloaded.
- One-model V1 strategy keeps operations and evaluation simple.

## Source Links
- Ollama docs: https://docs.ollama.com/
- vLLM docs: https://docs.vllm.ai/
- OpenRouter docs: https://openrouter.ai/docs/quickstart
- OpenRouter models: https://openrouter.ai/models

## Notes
- Model availability and free-tier routing can change over time.
- Revalidate model IDs and rate limits before production rollout.
