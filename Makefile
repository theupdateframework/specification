SHELL=/bin/bash -o pipefail
.PHONY: local

local: tuf-spec.md
	bikeshed spec tuf-spec.md tuf-spec.html --md-Text-Macro="COMMIT-SHA LOCAL COPY"
