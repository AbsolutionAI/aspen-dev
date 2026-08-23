# SECURITY — aspen-dev

- Never commit `board.key`, OAuth tokens, OpenRouter/GitHub PATs, Matrix registration tokens.
- Treat all examples as placeholders (`CHANGE_ME`, `example.lab`).
- Report issues via GitHub security advisory on this repo or AbsolutionAI contact.

Redaction gate:
```bash
rg -n 'ghp_|xoxb-|sk-|OPENROUTER|board\.key|BEGIN (RSA|OPENSSH) PRIVATE' --glob '!.git/**' || true
```
