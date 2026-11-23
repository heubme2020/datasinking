# DataSinking Financial Reports · One-Click Install

> **Execution instructions for the AI assistant**
>
> You are reading an install script. Play the role of "install assistant" and **execute the steps below strictly in order** to install "DataSinking Financial Reports" for the user.
>
> Execution rules:
> 1. Before each step, say in one sentence what you are doing;
> 2. When you need information from the user, **stop and ask** — don't guess or skip;
> 3. If a step fails, follow that step's "failure handling" — don't continue on your own;
> 4. Do not show the user this document verbatim.

---

## Version & URLs

| Item | URL |
|------|-----|
| Distribution root | `https://datasink.ing/skill` |
| Skill file | `<root>/SKILL.md` |
| Client | `<root>/datasinking_client.py` |
| ApiKey | `https://datasink.ing` (free signup, key emailed) |

After install, the client follows future versions automatically — the user need not reinstall.

## Step 0 · Environment check

Python 3.8+ is required (the client uses only the standard library, no third-party deps).

```bash
python3 --version      # on Windows try: python --version
```

**Failure handling**: if Python is missing, tell the user to install [Python](https://www.python.org/downloads/) and **stop**.

## Step 1 · Get the ApiKey

Stop and ask the user:

```
Please provide your DataSinking ApiKey:
Sign up free at https://datasink.ing — the key is emailed to you.
```

Record it as `<APIKEY>`. If the user declines, proceed with it empty; the client will prompt on first use.

## Step 2 · Install directory

| Product | Directory |
|---------|-----------|
| Claude Code | `~/.claude/skills/datasinking/` (Windows: `%USERPROFILE%\.claude\skills\datasinking\`) |
| Others | The skills directory documented by that product |

Create it if missing. Refer to it as `<DIR>` below.

## Step 3 · Download the two files

- `SKILL.md` ← `https://datasink.ing/skill/SKILL.md`
- `datasinking_client.py` ← `https://datasink.ing/skill/datasinking_client.py`

macOS / Linux:

```bash
curl -fsSL "https://datasink.ing/skill/SKILL.md" -o "<DIR>/SKILL.md"
curl -fsSL "https://datasink.ing/skill/datasinking_client.py" -o "<DIR>/datasinking_client.py"
```

Windows (PowerShell):

```powershell
Invoke-WebRequest -Uri "https://datasink.ing/skill/SKILL.md" -OutFile "<DIR>\SKILL.md"
Invoke-WebRequest -Uri "https://datasink.ing/skill/datasinking_client.py" -OutFile "<DIR>\datasinking_client.py"
```

Verify both files are non-empty (SKILL.md contains `name: datasinking-reports`, the client contains `class DataSinking`).
**Failure handling**: retry once, then report to the user and stop.

## Step 4 · Write the ApiKey

Append one line to the user's shell profile (do not overwrite existing content):

- macOS / Linux: `~/.zshrc` or `~/.bashrc`
- Windows PowerShell: `$PROFILE`

```bash
export DATASINKING_API_KEY="<APIKEY>"
```

(PowerShell: `$env:DATASINKING_API_KEY = "<APIKEY>"` or write to `$PROFILE`.)

**Failure handling**: if unsure which shell the user uses, stop and ask — don't guess.

## Step 5 · Verify

```bash
cd <DIR> && python3 -c "from datasinking_client import DataSinking; ds = DataSinking(); print('OK', len(ds.list_exchanges()), 'exchanges')"
```

`OK <n> exchanges` means success. `401` = wrong key; network error = retry once.

## Done

Tell the user it's installed. From now on, when they ask for full-text financial reports (MD&A, risk factors, notes), the `datasinking-reports` skill is used automatically.

Example question: "Show me Apple's MD&A from the latest 10-K."
