# custom/

Personal customization layer for a Vietnamese-translation workflow, kept separate from the upstream
`pdf2zh` project so the two don't mix. Nothing in here is upstream code.

| Path | Purpose |
|---|---|
| `docs/HUONG_DAN_SU_DUNG.md` | Vietnamese usage guide for this specific install (services, models, prompt, config, chunking large PDFs). |
| `prompts/prompt_vi.txt` | Custom LLM prompt (glossary/style rules) passed via `--prompt`. |
| `config/config_gemini.json` | Per-model run config passed via `--config` (API key + model). **Gitignored** — holds a real key, never commit files here (`custom/config/*.json` is ignored as a whole). |
| `scripts/split_pdf.py`, `scripts/merge_pdf.py` | Chunk a long PDF before translation and reassemble the translated chunks after. See `docs/HUONG_DAN_SU_DUNG.md` section 13. |

Don't confuse this with the top-level `script/` directory (singular) — that one is upstream build/packaging
tooling (Windows build, Docker variants) and is unrelated to this workspace.
