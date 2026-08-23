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

# Fail only on high-entropy secret shapes, not docs that mention the audit patterns.
smoke: docs-check
	@if rg -n --glob '!.git/**' -e 'ghp_[A-Za-z0-9]{20,}' -e 'xoxb-[0-9]{8,}' -e 'sk-[A-Za-z0-9]{20,}' -e 'BEGIN (RSA|OPENSSH) PRIVATE KEY' . ; then \
	  echo 'secret-shaped token found'; exit 1; \
	else \
	  echo 'aspen-dev smoke ok'; \
	fi
