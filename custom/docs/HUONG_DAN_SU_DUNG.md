# Hướng dẫn sử dụng PDFMathTranslate để dịch PDF sang Tiếng Việt

> Công cụ: [PDFMathTranslate](https://github.com/PDFMathTranslate/PDFMathTranslate) (`pdf2zh`)
> Đã cài đặt tại: `/home/tantq/Apps/PDFMathTranslate` (virtualenv Python 3.12 tại `.venv`)

## Mục lục

- [1. Kích hoạt môi trường](#1-kích-hoạt-môi-trường)
- [2. Dịch cơ bản sang Tiếng Việt](#2-dịch-cơ-bản-sang-tiếng-việt)
- [3. Dùng giao diện web (GUI)](#3-dùng-giao-diện-web-gui)
- [4. Chọn engine/service dịch](#4-chọn-enginetranslation-service)
- [5. Dùng LLM để tăng độ chính xác](#5-dùng-llm-để-tăng-độ-chính-xác)
- [6. Prompt tùy chỉnh (thuật ngữ chuyên ngành)](#6-prompt-tùy-chỉnh-thuật-ngữ-chuyên-ngành)
- [7. File cấu hình cố định (config.json)](#7-file-cấu-hình-cố-định-configjson)
- [8. Giữ nguyên công thức toán học](#8-giữ-nguyên-công-thức-toán-học)
- [9. Các tùy chọn khác](#9-các-tùy-chọn-khác)
- [10. Bảng tổng hợp toàn bộ tham số](#10-bảng-tổng-hợp-toàn-bộ-tham-số)
- [11. Cấu hình khuyến nghị cho độ chính xác cao nhất](#11-cấu-hình-khuyến-nghị-cho-độ-chính-xác-cao-nhất)
- [12. Xử lý sự cố](#12-xử-lý-sự-cố)
- [13. Xử lý tài liệu dài (chunk & merge)](#13-xử-lý-tài-liệu-dài-chunk--merge)

---

## 1. Kích hoạt môi trường

Mỗi lần mở terminal mới, cần kích hoạt virtualenv trước khi dùng lệnh `pdf2zh`:

```bash
cd /home/tantq/Apps/PDFMathTranslate
source .venv/bin/activate
```

Kiểm tra đã cài đúng:

```bash
pdf2zh --version
```

---

## 2. Dịch cơ bản sang Tiếng Việt

```bash
pdf2zh document.pdf -li en -lo vi
```

| Tham số | Ý nghĩa |
|---|---|
| `-li` | Ngôn ngữ nguồn, ví dụ `en` (tiếng Anh) |
| `-lo` | Ngôn ngữ đích. Mặc định dùng service **Google** (miễn phí, không cần API key) |

**Kết quả sinh ra** (mặc định lưu ở thư mục hiện tại, hoặc chỉ định bằng `-o`):

- `document-mono.pdf` — chỉ chứa bản dịch tiếng Việt
- `document-dual.pdf` — bản song ngữ, xen kẽ trang gốc/trang dịch

Ví dụ lưu vào thư mục riêng:

```bash
pdf2zh document.pdf -li en -lo vi -o ./output
```

> **Lưu ý mã ngôn ngữ:** Với engine Google/Bing dùng mã `vi`. Với các engine dựa trên LLM (OpenAI, Gemini, DeepSeek, Grok…), giá trị `-lo` được chèn thẳng vào câu prompt gửi cho mô hình, nên nên dùng `-lo Vietnamese` (viết chữ) thay vì `-lo vi` để mô hình hiểu chính xác hơn.

> **Về font:** Công cụ tự động tải font `GoNotoKurrent-Regular.ttf` (Google Noto) để hiển thị đầy đủ ký tự có dấu tiếng Việt — không cần cấu hình gì thêm.

---

## 3. Dùng giao diện web (GUI)

Nếu không quen dòng lệnh:

```bash
pdf2zh -i
```

Sau đó mở trình duyệt tại:

```
http://localhost:7860
```

Upload file PDF, chọn ngôn ngữ nguồn/đích và service dịch ngay trên giao diện.

Một số tùy chọn liên quan:

```bash
pdf2zh -i --share              # tạo public link tạm thời (Gradio)
pdf2zh -i --serverport 8080    # đổi cổng chạy web UI
pdf2zh -i --config config.json # dùng kèm file cấu hình (xem mục 7)
```

---

## 4. Chọn engine/translation service

Mặc định dùng **Google** (dịch máy thường, không cần key nhưng độ chính xác với văn bản khoa học/công thức không cao). Có thể đổi bằng `-s`:

```bash
pdf2zh document.pdf -lo vi -s bing
```

Cú pháp chọn model cụ thể cho service (nếu service đó hỗ trợ model):

```bash
pdf2zh document.pdf -lo Vietnamese -s openai:gpt-4o
# hoặc dùng biến môi trường: export OPENAI_MODEL=gpt-4o
```

### 4.1 Nhóm MT truyền thống (không có khái niệm "model", chất lượng cố định)

| Service | Cờ `-s` | Cần API key? | Hỗ trợ tiếng Việt? | Khuyến nghị dùng khi nào |
|---|---|---|---|---|
| **Google** | `google` | Không | ✅ Có | Mặc định để thử nghiệm nhanh, tài liệu phổ thông không chuyên sâu, không tốn phí. Yếu với thuật ngữ chuyên ngành/công thức. |
| **Bing** | `bing` | Không | ✅ Có | Dùng thay thế khi Google bị giới hạn/chặn IP; chất lượng tương đương Google. |
| **DeepL** | `deepl` | Có (`DEEPL_AUTH_KEY`) | ❌ **Không** — DeepL hiện chưa có tiếng Việt trong danh sách ngôn ngữ đích chính thức | **Không nên dùng cho mục tiêu dịch sang tiếng Việt.** Chỉ phù hợp nếu đích là các ngôn ngữ Âu (DE, FR, JA, ZH…). |
| **Azure (Microsoft Translator)** | `azure` | Có (`AZURE_API_KEY`) | ✅ Có, khá tốt | Khi tổ chức đã có sẵn Azure subscription; chất lượng nhỉnh hơn Google với văn bản trang trọng. |
| **Tencent** | `tencent` | Có (`TENCENTCLOUD_SECRET_ID/KEY`) | ✅ Có (mạnh về khu vực Đông Nam Á) | Khi đã có Tencent Cloud account, hoặc cần dịch cặp Trung↔Việt. |

### 4.2 Nhóm LLM quốc tế (OpenAI-compatible) — chọn được model, độ chính xác cao nhất

| Service | Cờ `-s` | Model mặc định (`*_MODEL`) | Model nên đổi sang | Khuyến nghị dùng khi nào |
|---|---|---|---|---|
| **OpenAI** | `openai` | `gpt-4o-mini` | `gpt-4o`, `gpt-4.1`, `o4-mini` (reasoning, chậm hơn nhưng chính xác cao với công thức/logic phức tạp) | **Ưu tiên số 1** cho tài liệu khoa học/kỹ thuật cần độ chính xác cao nhất, sẵn sàng trả phí theo token. |
| **Gemini** | `gemini` | `gemini-1.5-flash` | `gemini-1.5-pro`, `gemini-2.0-flash` | Cân bằng tốt giữa chi phí và chất lượng; có tier miễn phí hạn mức khá rộng, phù hợp dịch số lượng lớn. |
| **Grok** | `grok` | `grok-2-1212` | model Grok mới nhất theo tài khoản xAI | Khi đã có sẵn gói xAI/Grok, muốn so sánh chất lượng với OpenAI. |
| **Groq** *(lưu ý: khác Grok — đây là nền tảng inference tốc độ cao)* | `groq` | `llama-3-3-70b-versatile` | các model Llama/Mixtral mới hơn có trên Groq | Cần **tốc độ dịch rất nhanh** (chip LPU), tier miễn phí rộng, chấp nhận chất lượng thấp hơn GPT-4o một chút. |
| **DeepSeek** | `deepseek` | `deepseek-chat` | `deepseek-reasoner` (cho văn bản cần suy luận/công thức phức tạp) | Ngân sách hạn chế nhưng vẫn muốn chất lượng LLM tốt; giá rẻ hơn nhiều so với OpenAI. |
| **OpenAI-Liked** *(tự host)* | `openailiked` | tùy chỉnh (`OPENAILIKED_MODEL`) | model bạn tự chạy qua vLLM/LM Studio/text-generation-webui | Doanh nghiệp cần dữ liệu không rời khỏi hạ tầng nội bộ nhưng vẫn muốn dùng LLM. |

### 4.3 Nhóm LLM Trung Quốc (giá rẻ, hạn ngạch miễn phí lớn)

| Service | Cờ `-s` | Model mặc định | Model nên đổi sang | Khuyến nghị dùng khi nào |
|---|---|---|---|---|
| **Zhipu** | `zhipu` | `glm-4-flash` | `glm-4-plus` | Chi phí gần như miễn phí, chấp nhận chất lượng vừa phải; hợp tài liệu không quá phức tạp. |
| **ModelScope** | `modelscope` | `Qwen/Qwen2.5-Coder-32B-Instruct` | các bản Qwen2.5 lớn hơn nếu tài liệu nhiều thuật ngữ kỹ thuật/code | Tài liệu kỹ thuật/lập trình, tận dụng quota miễn phí của Alibaba. |
| **Silicon (SiliconCloud)** | `silicon` | `Qwen/Qwen2.5-7B-Instruct` | các model open-source lớn hơn có trên SiliconCloud | Muốn thử nhiều model open-source qua 1 API, chi phí rất thấp. |
| **Ali Qwen-MT** | `qwen-mt` | `qwen-mt-turbo` | `qwen-mt-plus` | Model **chuyên biệt cho dịch** (không phải chat model) nên tốc độ nhanh, giá rẻ; lưu ý chưa hỗ trợ tiếng Trung phồn thể. |
| **MiniMax** | `minimax` | `MiniMax-M2.7` | model MiniMax mới hơn nếu có | Ít phổ biến hơn, dùng khi đã có sẵn tài khoản MiniMax. |
| **302.AI** | `302ai` | `Gemma-7B` | model khác trên nền tảng 302.AI | Nền tảng trung gian gom nhiều model, tiện khi muốn đổi qua lại nhanh. |

### 4.4 Nhóm chạy local (miễn phí, riêng tư, không cần internet)

| Service | Cờ `-s` | Model mặc định | Model nên đổi sang | Khuyến nghị dùng khi nào |
|---|---|---|---|---|
| **Ollama** | `ollama` | `gemma2` | `qwen2.5:14b`, `llama3.1:8b` (tuỳ VRAM máy) | Dữ liệu **nhạy cảm/bảo mật**, không muốn gửi ra internet; cần máy có GPU/CPU đủ mạnh. Chất lượng thấp hơn LLM cloud lớn. |
| **Xinference** | `xinference` | `gemma-2-it` | tương tự Ollama, tuỳ model đã deploy | Tương tự Ollama nhưng cần quản lý nhiều loại model (LLM/embedding/rerank) trên cùng server nội bộ. |
| **Argos Translate** | `argos` | — (không dùng LLM, MT offline nhẹ) | — | Cần dịch hoàn toàn offline, máy yếu, chấp nhận chất lượng thấp nhất trong danh sách. |

> **Tóm tắt lựa chọn nhanh theo use case:**
> - **Chính xác nhất, không quan tâm chi phí** → `openai:gpt-4o` hoặc `openai:gpt-4.1`
> - **Cân bằng chi phí/chất lượng, dịch số lượng lớn** → `gemini:gemini-1.5-pro` hoặc `deepseek`
> - **Cần nhanh, tier miễn phí rộng** → `groq`
> - **Dữ liệu bảo mật, không được rời máy** → `ollama` (chạy local)
> - **Không cần chính xác cao, chỉ thử nhanh, miễn phí** → `google` (mặc định)
> - **Tuyệt đối tránh** `deepl` nếu ngôn ngữ đích là tiếng Việt (chưa hỗ trợ)

---

## 5. Dùng LLM để tăng độ chính xác

Đây là cách **quan trọng nhất** để nâng độ chính xác bản dịch, đặc biệt với tài liệu khoa học có thuật ngữ chuyên ngành và công thức.

```bash
export OPENAI_API_KEY=sk-xxxx
export OPENAI_MODEL=gpt-4o          # đổi sang model mạnh hơn thay vì mặc định gpt-4o-mini
pdf2zh document.pdf -lo Vietnamese -s openai
```

Hoặc chỉ định model ngay trên dòng lệnh, không cần env var riêng:

```bash
pdf2zh document.pdf -lo Vietnamese -s openai:gpt-4o
```

Tương tự với các LLM khác (đổi tên biến môi trường theo service):

```bash
export GEMINI_API_KEY=xxxx
export GEMINI_MODEL=gemini-1.5-pro
pdf2zh document.pdf -lo Vietnamese -s gemini
```

> **Mẹo chọn model:** model càng mạnh (ví dụ `gpt-4o` thay vì `gpt-4o-mini`, `gemini-1.5-pro` thay vì `gemini-1.5-flash`) thường cho bản dịch mượt và chính xác thuật ngữ hơn, đổi lại chi phí/API cao hơn và tốc độ chậm hơn.

---

## 6. Prompt tùy chỉnh (thuật ngữ chuyên ngành)

Chỉ áp dụng cho các service LLM. Dùng để ép mô hình giữ văn phong, thuật ngữ, hoặc bảng chú giải riêng.

```bash
pdf2zh document.pdf -lo Vietnamese -s openai --prompt prompt.txt
```

Nội dung mẫu `prompt.txt`:

```txt
Bạn là một dịch giả chuyên ngành khoa học kỹ thuật, dịch chính xác và tự nhiên.

Dịch đoạn văn bản Markdown sau sang ${lang_out}. Giữ nguyên ký hiệu công thức {v*} không đổi.
Giữ nguyên các thuật ngữ tiếng Anh đã được chấp nhận rộng rãi (ví dụ: neural network, transformer)
nếu dịch sang tiếng Việt gây khó hiểu. Chỉ xuất ra bản dịch, không thêm giải thích.

Văn bản gốc: ${text}

Bản dịch:
```

Ba biến có thể dùng trong file prompt:

| Biến | Ý nghĩa |
|---|---|
| `${lang_in}` | Ngôn ngữ nguồn |
| `${lang_out}` | Ngôn ngữ đích |
| `${text}` | Đoạn văn bản cần dịch |

---

## 7. File cấu hình cố định (config.json)

> **File thật của cá nhân:** `custom/config/config_gemini.json` (đã gitignore vì chứa API key thật —
> xem `custom/README.md`). Ví dụ `config.json` dưới đây chỉ minh hoạ cú pháp chung.

Thay vì `export` biến môi trường mỗi lần, có thể lưu sẵn API key/model vào file JSON:

```bash
pdf2zh document.pdf --config config.json
pdf2zh -i --config config.json     # dùng kèm GUI
```

Ví dụ `config.json`:

```json
{
    "PDF2ZH_LANG_FROM": "English",
    "PDF2ZH_LANG_TO": "Vietnamese",
    "translators": [
        {
            "name": "openai",
            "envs": {
                "OPENAI_BASE_URL": "https://api.openai.com/v1",
                "OPENAI_API_KEY": "sk-xxxx",
                "OPENAI_MODEL": "gpt-4o"
            }
        }
    ]
}
```

> **Quan trọng:** với các API tương thích OpenAI (Grok, OpenAI-liked, proxy riêng…), `BASE_URL` phải kết thúc bằng `/v1`, nếu không sẽ bị lỗi 404.

Mặc định, nếu không chỉ định `--config`, file cấu hình được đọc/ghi tại:

```
~/.config/PDFMathTranslate/config.json
```

Thứ tự ưu tiên: chương trình đọc `config.json` trước, sau đó đọc biến môi trường — nếu biến môi trường tồn tại thì giá trị đó được dùng và ghi đè lại vào file.

---

## 8. Giữ nguyên công thức toán học

Mặc định công cụ đã nhận diện các font công thức phổ biến (LaTeX, Math, Symbol, Italic, Mono, Code…) để **không dịch** phần đó. Nếu công thức trong PDF bị dịch nhầm (do dùng font đặc biệt), có thể tự chỉnh regex:

```bash
pdf2zh document.pdf -f "(CM[^R]|MS.M|XY|MT|BL|RM|EU|LA|RS|LINE|LCIRCLE|TeX-|rsfs|txsy|wasy|stmary|.*Mono|.*Code|.*Ital|.*Sym|.*Math)" \
                     -c "(\(|\||\)|\+|=|\d|[-﫿])"
```

- `-f`: regex khớp **tên font** cần giữ nguyên (không dịch)
- `-c`: regex khớp **ký tự** cần giữ nguyên trong vùng công thức

---

## 9. Các tùy chọn khác

| Tùy chọn | Tác dụng |
|---|---|
| `-p 1-3,5` | Chỉ dịch trang 1 đến 3 và trang 5 — dùng để **test nhanh** trước khi chạy cả tài liệu dài (đỡ tốn thời gian/API) |
| `-t 1` | Giới hạn số luồng song song — giảm rủi ro bị rate-limit từ API khiến một số đoạn bị bỏ sót/dịch lỗi |
| `--ignore-cache` | Bỏ qua bộ nhớ đệm, ép dịch lại toàn bộ — cần dùng sau khi đổi prompt/model để so sánh kết quả mới |
| `--compatible` | Bật chế độ tương thích khi PDF gốc có lỗi font/layout đặc biệt |
| `--skip-subset-fonts` | Tắt tối ưu hoá (subset) font, dùng khi gặp lỗi hiển thị font ở file kết quả |
| `--dir /path/to/folder` | Dịch hàng loạt tất cả PDF trong một thư mục |
| `--mode precise` | Kernel v2 (thử nghiệm), xử lý bố cục nhiều cột/trang phức tạp tốt hơn (yêu cầu submodule `pdf2zh_next`) |
| `--babeldoc` | Dùng backend thử nghiệm [BabelDOC](https://funstory-ai.github.io/BabelDOC/) |
| `--mcp` | Chạy dưới dạng MCP server (tích hợp với Claude Desktop, xem mục 12) |

---

## 10. Bảng tổng hợp toàn bộ tham số

| Tham số | Ví dụ |
|---|---|
| Dịch file local | `pdf2zh ~/local.pdf` |
| Dịch file online | `pdf2zh http://arxiv.org/paper.pdf` |
| Mở GUI | `pdf2zh -i` |
| Dịch một phần | `pdf2zh example.pdf -p 1` |
| Ngôn ngữ nguồn | `pdf2zh example.pdf -li en` |
| Ngôn ngữ đích | `pdf2zh example.pdf -lo vi` |
| Chọn service | `pdf2zh example.pdf -s openai` |
| Số luồng | `pdf2zh example.pdf -t 1` |
| Thư mục output | `pdf2zh example.pdf -o output` |
| Giữ nguyên font/ký tự | `pdf2zh example.pdf -f "(MS.*)"` |
| Chế độ tương thích | `pdf2zh example.pdf --compatible` |
| Bỏ subset font | `pdf2zh example.pdf --skip-subset-fonts` |
| Bỏ cache | `pdf2zh example.pdf --ignore-cache` |
| Public link (GUI) | `pdf2zh -i --share` |
| Prompt tùy chỉnh | `pdf2zh example.pdf --prompt prompt.txt` |
| File cấu hình | `pdf2zh example.pdf --config config.json` |
| Dịch hàng loạt | `pdf2zh --dir /path/to/folder` |
| Kernel v2 thử nghiệm | `pdf2zh --mode precise example.pdf` |
| Backend BabelDOC | `pdf2zh --babeldoc -s openai example.pdf` |

---

## 11. Cấu hình khuyến nghị cho độ chính xác cao nhất

```bash
export OPENAI_API_KEY=sk-xxxx
export OPENAI_MODEL=gpt-4o

# 1. Test nhanh vài trang trước
pdf2zh document.pdf -lo Vietnamese -s openai --prompt prompt.txt -p 1-3 -o ./test

# 2. Kiểm tra kết quả OK thì chạy toàn bộ
pdf2zh document.pdf -lo Vietnamese -s openai --prompt prompt.txt -t 2 -o ./output
```

**Thứ tự ưu tiên các yếu tố ảnh hưởng đến độ chính xác** (từ ảnh hưởng lớn → nhỏ):

1. **Chọn engine LLM** thay vì Google/Bing (hiểu ngữ cảnh, thuật ngữ tốt hơn nhiều)
2. **Chọn model mạnh** (`gpt-4o`, `gemini-1.5-pro`… thay vì bản "mini/flash")
3. **Prompt tùy chỉnh** khai báo thuật ngữ/văn phong chuyên ngành
4. Tinh chỉnh `-f`/`-c` nếu công thức toán bị dịch nhầm
5. Giảm `-t` (số luồng) nếu tài liệu dài hay bị lỗi rớt đoạn do rate-limit

---

## 12. Xử lý sự cố

**Lỗi tải model AI layout (`DocLayout-YOLO`) do mạng:**

```bash
export HF_ENDPOINT=https://hf-mirror.com
```

**Chạy như MCP server (tích hợp Claude Desktop):**

```json
{
    "mcpServers": {
        "translate_pdf": {
            "command": "uv",
            "args": ["run", "pdf2zh", "--mcp"]
        }
    }
}
```

Sau khi cấu hình, có thể yêu cầu Claude Desktop: *"tìm file test.pdf trong thư mục Document và dịch sang tiếng Việt"*.

**Tài liệu gốc chi tiết hơn:**

- `docs/ADVANCED.md` — toàn bộ tùy chọn nâng cao
- `docs/APIS.md` — dùng pdf2zh như thư viện Python / HTTP API
- `docs/PROXY_CONFIGURATION.md` — cấu hình proxy mạng

---

## 13. Xử lý tài liệu dài (chunk & merge)

### 13.1 Có bắt buộc phải chunk không?

**Không bắt buộc.** `pdf2zh` tự "chunk" nội bộ ở mức đoạn văn bản và có **cache dịch bền vững** tại `~/.cache/pdf2zh/cache.v1.db` (khoá theo engine + model + văn bản gốc). Nhờ vậy:

- Có thể chạy 1 lệnh duy nhất cho cả tài liệu hàng trăm trang.
- Nếu bị gián đoạn (hết quota, mất mạng, Ctrl+C, crash…), chỉ cần **chạy lại đúng lệnh đó** — các đoạn đã dịch được lấy từ cache (không gọi lại API), chỉ đoạn chưa dịch mới tiếp tục.

Tuy nhiên với tài liệu **rất dài (300-500+ trang)**, nên chủ động chunk vì:

| Vấn đề | Giải thích |
|---|---|
| Quota free tier hạn chế | Tài liệu dài sinh ra hàng nghìn đoạn cần dịch → dễ vượt giới hạn request/phút và request/ngày của các service free tier, phải chạy trải qua nhiều ngày. |
| Tốn công parse lại mỗi lần chạy | Cache chỉ bỏ qua bước **gọi API dịch**; bước phân tích layout PDF vẫn phải chạy lại từ đầu cho toàn bộ tài liệu mỗi lần lệnh được gọi lại. |
| Khó theo dõi tiến độ/lỗi | Một lệnh duy nhất cho cả tài liệu khiến khó xác định chính xác trang nào bị lỗi (font lạ, ký tự đặc biệt…). |
| Muốn chạy song song nhiều key | Có nhiều API key (vd Gemini + Groq) chỉ tận dụng được khi tài liệu đã được tách thành nhiều file độc lập. |

> **Lưu ý:** `-p 1-100` **không** dùng để chunk. Flag này vẫn xuất ra file đủ số trang gốc, chỉ dịch các trang trong danh sách, các trang còn lại giữ nguyên bản gốc — phù hợp để test nhanh một đoạn, không phù hợp để "chunk rồi ghép".

### 13.2 Cách chunk (tách PDF vật lý)

Dùng script `custom/scripts/split_pdf.py` (chỉ cần `pymupdf`, đã có sẵn trong `.venv` vì là dependency của `pdf2zh`):

```bash
cd /home/tantq/Apps/PDFMathTranslate
source .venv/bin/activate
python custom/scripts/split_pdf.py document.pdf 100 chunks/
# → chunks/chunk_001_p1-100.pdf, chunk_002_p101-200.pdf, ...
```

Tham số: `<input.pdf> <số trang mỗi chunk> <thư mục output>`.

### 13.3 Dịch từng chunk (có thể resume)

```bash
for f in chunks/*.pdf; do
    name=$(basename "$f" .pdf)
    out="translated/$name"
    if [ -f "$out/${name}-mono.pdf" ]; then
        echo "Bỏ qua $name (đã dịch)"
        continue
    fi
    echo "Đang dịch $name..."
    pdf2zh "$f" --config custom/config/config_gemini.json --prompt custom/prompts/prompt_vi.txt -o "$out" -t 1
done
```

- Kiểm tra file `-mono.pdf` đã tồn tại giúp **resume theo từng chunk**: dừng máy giữa chừng, chạy lại script sẽ tự bỏ qua chunk đã xong.
- Nếu hết quota trong ngày, hôm sau chạy lại đúng script này: chunk dở dang tiếp tục nhờ cache nội bộ của `pdf2zh`, chunk đã xong bị script bỏ qua ngay từ vòng lặp (không tốn thời gian parse lại).

### 13.4 Ghép lại

Dùng script `custom/scripts/merge_pdf.py`:

```bash
python custom/scripts/merge_pdf.py "translated/*/chunk_*-mono.pdf" document-vi-full.pdf
```

`glob` + `sorted()` đảm bảo ghép đúng thứ tự nhờ tên chunk có số thứ tự zero-padded (`chunk_001`, `chunk_002`...). Đổi pattern sang `*-dual.pdf` nếu muốn ghép bản song ngữ thay vì bản chỉ tiếng Việt.

### 13.5 Lưu ý khi tách/ghép thủ công

- **Mục lục (TOC)/bookmark và các liên kết nội bộ (internal links) sẽ bị mất** sau khi tách rồi ghép — mỗi chunk là 1 PDF độc lập nên anchor/link trỏ sang trang khác không còn đúng. Nếu tài liệu gốc có TOC quan trọng, cần chấp nhận đánh đổi này hoặc bổ sung lại TOC thủ công sau khi ghép.
- Số trang in trong nội dung văn bản (nếu có, vd "Page 12/560") sẽ không tự cập nhật lại — giới hạn chung của việc ghép PDF, không phải lỗi riêng của cách làm này.

### 13.6 Khuyến nghị theo số trang

| Số trang | Khuyến nghị |
|---|---|
| Dưới ~100-150 trang | Chạy thẳng 1 lệnh, không cần chunk, dựa vào cache để resume nếu lỗi giữa chừng. |
| 300-500+ trang | Nên chunk theo **~100 trang/chunk** (hoặc theo ranh giới chương nếu biết trước) để dễ theo dõi tiến độ, resume an toàn qua nhiều ngày do giới hạn quota free tier, và có thể chạy song song nếu có nhiều key. |
