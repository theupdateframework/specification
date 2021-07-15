SHELL=/bin/bash -o pipefail
SPEC_DIR:=$(shell dirname $(realpath $(firstword $(MAKEFILE_LIST))))
.PHONY: spec

spec: $(SPEC_DIR)/tuf-spec.md
	bikeshed spec $(SPEC_DIR)/tuf-spec.md tuf-spec.html

latest: spec
	mkdir -p latest
	cp tuf-spec.html latest/index.html

draft: spec
	mkdir -p draft
	cp tuf-spec.html draft/index.html

versioned: spec
	mkdir -p $(shell python3 $(SPEC_DIR)/scripts/get_version.py $(SPEC_DIR)/tuf-spec.md)
	cp tuf-spec.html $(shell python3 $(SPEC_DIR)/scripts/get_version.py $(SPEC_DIR)/tuf-spec.md)/index.html

index:
	python3 $(SPEC_DIR)/scripts/build_index.py

release: spec latest versioned
