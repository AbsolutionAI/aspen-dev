.PHONY: smoke docs-check
docs-check:
	@test -f README.md
	@test -f ARCHITECTURE.md
	@test -f CONTRACTS.md
	@test -f THIRD_PARTY.md
	@test -f SECURITY.md
	@test -f LICENSE
	@test -f docs/linear-map.md
	@test -d paperclip -o -d hermes -o -d ce-gates -o -d blueprints -o -d personas
	@echo 'docs-check ok'

smoke: docs-check
	@rg -n 'ghp_|xoxb-|sk-|OPENROUTER|board\.key|BEGIN (RSA|OPENSSH) PRIVATE' --glob '!.git/**' && exit 1 || true
	@echo 'aspen-dev smoke ok'
