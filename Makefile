SHELL=/bin/bash -o pipefail
.PHONY: local

local: tuf-spec.md
	bikeshed spec tuf-spec.md tuf-spec.html
