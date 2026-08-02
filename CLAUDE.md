# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

`pdf2zh` (PDFMathTranslate) is a scientific PDF translator that preserves document layout — formulas, charts,
table of contents, and annotations stay intact while text is translated. It ships as a CLI, a Gradio web GUI,
a Flask/Celery HTTP backend, and an MCP server. This is the stable v1.x fork (`Byaidu/PDFMathTranslate`); a
separate, more actively developed fork with additional features lives at `PDFMathTranslate/PDFMathTranslate-next`
(referenced here only as an optional git submodule, see "Kernel abstraction" below).

This working copy also has local additions on top of upstream that are not part of the public project:
`HUONG_DAN_SU_DUNG.md` (Vietnamese usage notes for this specific install), `config.json` / `config_gemini.json`
/ `prompt_vi.txt` (fixed run configs and a custom glossary prompt for Vietnamese translation), and
`scripts/split_pdf.py` / `scripts/merge_pdf.py` (chunk a large PDF before translation, then reassemble the
translated chunks). Keep these in mind when the user references "the usual workflow" — they're describing a
Vietnamese-translation setup layered on the generic tool.

## Common commands

Environment setup (uv is the expected tool; a `.venv` already exists in this checkout):

```bash
uv sync                    # install/sync dependencies from pyproject.toml
source .venv/bin/activate  # or prefix commands with `uv run`
```

Running the CLI:

```bash
pdf2zh document.pdf                       # translate, default Google service, en->zh
pdf2zh document.pdf -li en -lo vi -s google -o ./output
pdf2zh -i                                 # launch the Gradio web GUI on :7860
pdf2zh --mcp                              # run as an MCP server (STDIO)
pdf2zh --config /path/to/config.json      # run with a fixed config file
```

Tests (unittest-based, run via pytest):

```bash
uv run pytest .                                   # full suite
uv run pytest test/test_translator.py             # single file
uv run pytest test/test_translator.py::TestClassName::test_method  # single test
```

CLI smoke tests used in CI (see `.github/workflows/python-test.yml`):

```bash
uv run pdf2zh ./test/file/translate.cli.plain.text.pdf -o ./test/file
uv run pdf2zh ./test/file/translate.cli.text.with.figure.pdf -o ./test/file
timeout 10 uv run pdf2zh -i   # GUI should start and exit cleanly
```

Lint/format (also enforced by `.pre-commit-config.yaml` and CI's `black.format.yml`):

```bash
black --check --diff .
flake8 --ignore E203,E261,E501,W503,E741
```

Note: `setup.cfg` sets `max-line-length = 120` for flake8, but the pre-commit hook and `pyproject.toml`'s
`[tool.flake8]` both effectively allow 88 (black's default) since `E501` (line-too-long) is ignored in both
places — don't worry about wrapping long lines by hand.

Provisioning the experimental "precise" kernel (only needed when working with `--mode precise`):

```bash
git submodule update --init pdf2zh/kernel/PDFMathTranslate-next.git
pdf2zh-setup-precise   # creates an isolated venv under the submodule and pip-installs it
```

## Architecture

### Two entry paths into translation

The CLI (`pdf2zh.py`) and GUI (`gui.py`) both route through the **kernel registry** (see below) by default:
`KernelRegistry.switch(mode)` then `kernel.translate(request)`, where `mode` is `"fast"` or `"precise"`.
Both also have a third path, `--babeldoc` (`yadt_main()` in the CLI, `babeldoc_translate_file()` in the GUI),
which bypasses the kernel registry and calls straight into the `babeldoc` package's own translator — a
third translation engine entirely, separate from "fast" and "precise". The Flask backend (`backend.py`) and
the MCP server (`mcp_server.py`) are older/simpler paths that call `pdf2zh.translate_stream()` directly —
they bypass the kernel registry entirely and therefore only ever run the fast, in-process pipeline; they
have no route to the "precise" kernel or to babeldoc. Don't assume all these frontends are equivalent when
changing kernel-selection or precise-mode behavior.

### Fast pipeline (`high_level.py` / `converter.py` / `pdfinterp.py`)

```
translate()          -> per file: download/convert to PDF, optional PDF/A conversion
  (high_level.py)        -> translate_stream()
                               -> embeds Noto/CJK fonts into a copy of the doc
                               -> translate_patch()
                                    -> pdfminer PDFParser/PDFDocument walks pages
                                    -> doclayout.OnnxModel.predict() per page -> layout boxes
                                       (figures/tables/formulas are masked out of translation)
                                    -> PDFPageInterpreterEx (pdfinterp.py) replays page content
                                       streams through converter.TranslateConverter
                                         -> groups text into Paragraph objects, batches calls to a
                                            BaseTranslator subclass (translator.py), rewrites the
                                            PDF content stream with translated text
                               -> merges original + translated pages into mono/dual PDFs (pymupdf)
```

`translate()` is reached two ways: directly by `backend.py`/`mcp_server.py` (via `translate_stream()`, one
level in), and indirectly by the CLI/GUI via `LegacyKernel.translate()` (see below). Read `high_level.py`
first when tracing an end-to-end translation regardless of entry path.

### Kernel abstraction (`pdf2zh/kernel/`)

Wraps translation as a swappable "kernel" so a second, more advanced engine can run side by side with the
pipeline above:

- `kernel/protocol.py` — `KernelProtocol`, plus the shared `TranslateRequest`/`TranslateResult` dataclasses
  that both kernels speak, decoupling CLI/GUI argument parsing from kernel-specific config.
- `kernel/registry.py` — `KernelRegistry`, a thread-safe process-wide singleton (`register`/`get`/`switch`)
  that both kernels register themselves into on import.
- `kernel/legacy.py` — `LegacyKernel` ("fast"), a thin adapter over `high_level.translate()` — this is the
  pipeline described above and is always available.
- `kernel/precise.py` / `kernel/v2_bridge.py` / `kernel/v2_worker.py` — `PreciseKernel` ("precise"), which
  shells out to `pdf2zh_next` (the PDFMathTranslate-next project) running in its own isolated venv under
  `pdf2zh/kernel/PDFMathTranslate-next.git/.venv`, communicating via a JSON request piped to
  `v2_worker.py` over stdin and JSON events/results over stdout/stderr. `is_available()` returns `False`
  until the submodule is checked out and the venv provisioned — code must not assume "precise" is usable.

When touching kernel-selection logic, remember the fast kernel runs in-process while the precise kernel is a
subprocess in a separate virtualenv — error handling, cancellation, and progress callbacks work differently
for each (see `translate()` vs `translate_async()` in `precise.py`).

### Translation services (`pdf2zh/translator.py`)

All services subclass `BaseTranslator` and are looked up by name (`-s`/`--service` CLI flag, e.g. `google`,
`bing`, `deepl`, `ollama`, `openai`, `azure`, `tencent`, `gemini`, `deepseek`, `grok`, `groq`, `minimax`,
`qwen-mt`, etc.). Many LLM-backed services (`GeminiTranslator`, `ModelScopeTranslator`, `ZhipuTranslator`,
`DeepseekTranslator`, `GrokTranslator`, ...) are thin subclasses of `OpenAITranslator` that just override the
base URL/model, since they expose OpenAI-compatible chat completion APIs. Translation results are cached via
`pdf2zh/cache.py` (peewee/SQLite, under `~/.cache/pdf2zh`), keyed on (engine name, a sorted-JSON blob of
engine params such as languages/model, source text), unless `--ignore-cache` is set.

### Other modules worth knowing

- `pdf2zh/config.py` — `ConfigManager`, a singleton reading/writing `~/.config/PDFMathTranslate/config.json`
  (or a path passed via `--config`) for persisted defaults (API keys, endpoints, font paths, etc.).
- `pdf2zh/doclayout.py` — loads the `DocLayout-YOLO` ONNX model (`ModelInstance` singleton) used to detect
  figures/tables/formulas so they're excluded from translation and left visually untouched.

### Compatibility note

`docs/APIS.md` and `docs/ADVANCED.md` document the stable public Python/HTTP API and CLI flags respectively —
check them before changing signatures of `high_level.translate()`/`translate_stream()` or CLI argument names,
since downstream integrations depend on them.
