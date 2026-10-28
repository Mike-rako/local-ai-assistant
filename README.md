# Local AI Assistant

🌐 **English** | [Español](README.es.md)

An AI assistant that runs **100% on your own computer**, with no servers or external accounts. It stays in the background and you call it with keyboard shortcuts from any application: browser, Word, PDF reader, text editor, and so on.

- **Language model:** [llama.cpp](https://github.com/ggerganov/llama.cpp) (via `llama-cpp-python`) with any `.gguf` model.
- **Speech to text:** [faster-whisper](https://github.com/SYSTRAN/faster-whisper), also local.
- **Interface:** minimalist dark-theme windows built with `tkinter` (no extra dependencies).

> The assistant's interface and prompts are currently in Spanish. The assistant itself answers in the language set by `ASSISTANT_LANGUAGE`.

## What you can do

| Shortcut (default) | Action |
|---|---|
| `Ctrl+Alt+T` | Type a question in a text box |
| `Ctrl+Alt+G` | Ask by voice (press the same shortcut again to stop recording) |
| `Ctrl+Alt+S` | Send the text you have selected in any app to the AI |
| `Ctrl+Alt+I` | Send the selected text together with an instruction (e.g. "summarize this", "translate to English") |

All shortcuts can be changed in the `.env` file.

## Requirements

- **Python 3.9 or higher**
- **Windows** (recommended). The `keyboard` library needs administrator rights on Windows and root on Linux, and it barely works on macOS.
- A microphone (only for the voice feature).
- A `.gguf` model. As a reference, a 7B model quantized to 3 bits takes about 4 GB on disk and needs several GB of free RAM.
- On Linux, also: `sudo apt install python3-tk`.

## Installation

**1. Clone the repository**

```bash
git clone https://github.com/Mike-rako/local-ai-assistant.git
cd local-ai-assistant
```

**2. (Recommended) Create a virtual environment**

```bash
python -m venv .venv
.venv\Scripts\activate        # Windows
# source .venv/bin/activate   # Linux
```

**3. Install the dependencies**

```bash
pip install -r requirements.txt
```

> `llama-cpp-python` is compiled during installation, and on Windows that may require the Visual Studio "Build Tools". If it fails, you can install a precompiled CPU version instead:
>
> ```bash
> pip install llama-cpp-python --extra-index-url https://abetlen.github.io/llama-cpp-python/whl/cpu
> ```

**4. Download a `.gguf` model (required)**

> ⚠️ **This repository does NOT include any AI model**, because they weigh several GB. You must download one yourself; without it, the program cannot answer.

1. Pick a chat model in GGUF format. These repositories are verified and work with this project (check Hugging Face for newer versions):

   | Model | Link | File to download | Size | License | Best for |
   |---|---|---|---|---|---|
   | Qwen2.5 1.5B Instruct | [Qwen/Qwen2.5-1.5B-Instruct-GGUF](https://huggingface.co/Qwen/Qwen2.5-1.5B-Instruct-GGUF) | `qwen2.5-1.5b-instruct-q4_k_m.gguf` | ~1 GB | Apache 2.0 | Low-RAM machines; fast but more basic |
   | Qwen2.5 3B Instruct | [Qwen/Qwen2.5-3B-Instruct-GGUF](https://huggingface.co/Qwen/Qwen2.5-3B-Instruct-GGUF) | `qwen2.5-3b-instruct-q4_k_m.gguf` | ~2.1 GB | Qwen Research (non-commercial) | Good balance between quality and speed |
   | Qwen2.5 7B Instruct | [Qwen/Qwen2.5-7B-Instruct-GGUF](https://huggingface.co/Qwen/Qwen2.5-7B-Instruct-GGUF) | `qwen2.5-7b-instruct-q3_k_m.gguf` | ~3.8 GB | Apache 2.0 | Better answers; slower and needs more RAM (**default model of this project**) |

   Each repository has several `.gguf` files with different quantizations (smaller files = lower quality). Download **only one** file. Be careful with files whose names end in `-00001-of-0000X.gguf`: the model is split into several parts that must be merged first. The files in the table are single files, so they work as they are. Any other GGUF chat model also works.

2. Open the link of the model you picked, go to the **Files and versions** tab and download the `.gguf` file listed in the table.

3. Save the file in the project's `models/` folder. Create the folder if it doesn't exist.

4. Set the file name in your `.env`. By default the program looks for `models/qwen2.5-7b-instruct-q3_k_m.gguf`, so if you downloaded a different model you **must** adjust `MODEL_PATH`:

   ```env
   MODEL_PATH=models/qwen2.5-1.5b-instruct-q4_k_m.gguf
   ```

   If you haven't created the `.env` yet, do it in the next step and then edit that line (see [Configuration](#configuration)).

**5. (Optional) Create your configuration file**

```bash
copy .env.example .env        # Windows
# cp .env.example .env        # Linux
```

This is not mandatory: every variable has a default value, so the program works without a `.env`.

## Usage

```bash
python main.py
```

On Windows, **run the terminal as administrator** so the global shortcuts work in every application. Keep the console window open while you use the assistant; close it to quit.

Notes:
- The **first answer** takes a few seconds because the model is loaded into memory.
- The **first time you use voice**, faster-whisper downloads its model (internet is needed only that once).

## Configuration

All variables are optional and are defined in the `.env` file (you can start from `.env.example`).

| Variable | Default | Description |
|---|---|---|
| `MODEL_PATH` | `models/qwen2.5-7b-instruct-q3_k_m.gguf` | Path to the `.gguf` model (relative to the project or absolute) |
| `N_CTX` | `2048` | Model context size, in tokens |
| `MAX_TOKENS` | `512` | Maximum length of each answer |
| `TEMPERATURE` | `0.7` | Creativity of the answers (lower = more predictable) |
| `ASSISTANT_LANGUAGE` | `español` | Preferred language of the answers (e.g. `English`) |
| `MEMORY_ENABLED` | `true` | Whether the assistant remembers the conversation |
| `MEMORY_MAX_MESSAGES` | `10` | Number of remembered messages (questions and answers both count) |
| `WHISPER_MODEL_SIZE` | `base` | Voice model size: `tiny`, `base`, `small`, `medium`, `large-v3` |
| `WHISPER_LANGUAGE` | `es` | Voice language (`es`, `en`, ...) or `auto` to detect it |
| `MAX_RECORDING_SECONDS` | `60` | Maximum duration of a recording |
| `HOTKEY_TEXT` | `ctrl+alt+t` | Shortcut to ask by text |
| `HOTKEY_VOICE` | `ctrl+alt+g` | Shortcut to ask by voice |
| `HOTKEY_SELECTION` | `ctrl+alt+s` | Shortcut to send the selected text |
| `HOTKEY_SELECTION_INSTRUCTION` | `ctrl+alt+i` | Shortcut for selected text + instruction |

## Project structure

```
├── main.py             # Main program and keyboard shortcuts
├── config.py           # Reads the .env with default values
├── llm_client.py       # Model loading and chat with memory
├── stt.py              # Audio recording and transcription (Whisper)
├── clipboard_util.py   # Captures the selected text in any app
├── ui.py               # Input and answer windows (tkinter)
├── requirements.txt
├── .env.example        # Configuration template
└── models/             # Your .gguf model goes here (not tracked by Git)
```

## Privacy

- Everything is processed on your machine: the model, the speech transcription and the answers. The program does not send data to any server.
- To capture the selected text, the app simulates `Ctrl+C` and reads the clipboard; afterwards it **restores** whatever you had copied before.
- Recorded audio is saved to a temporary file and deleted as soon as it is transcribed.
- Internet is needed only to download the `.gguf` model and, the first time, the Whisper model.

## Troubleshooting

| Problem | Possible fix |
|---|---|
| Shortcuts don't respond in some apps | Run the terminal as administrator |
| `No se encontró el modelo en: ...` (model not found) | Check that the `.gguf` is in `models/` or fix `MODEL_PATH` in `.env` |
| Error installing `llama-cpp-python` | Use the precompiled install (see step 3) or install the Visual Studio Build Tools |
| The selection shortcut copies nothing | Make sure the text is selected before pressing the shortcut |
| Very slow answers | Use a smaller model or a lighter quantization, or lower `MAX_TOKENS` |
| Voice is not transcribed well | Try `WHISPER_MODEL_SIZE=small` or check your default microphone |

## License

Distributed under the MIT license. See the [LICENSE](LICENSE) file for details.