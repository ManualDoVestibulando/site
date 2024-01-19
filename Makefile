.PHONY: clean all initial final

SOURCE_DIR=src/
MODULE_DIR=$(SOURCE_DIR)/mdv/
SCRIPTS_DIR=$(MODULE_DIR)/scripts/
NOTEBOOK_DIR=$(MODULE_DIR)/notebooks/

all: initial final

initial: $(SCRIPTS_DIR)/initial.py
	cd $(SOURCE_DIR); python -m mdv.scripts.initial

final: $(SCRIPTS_DIR)/final.py
	echo "Dummy final"

$(SCRIPTS_DIR)/initial.py: 	$(NOTEBOOK_DIR)/a_parse_forms.py \
							$(NOTEBOOK_DIR)/b_parse_essays.py

$(NOTEBOOK_DIR)/%.py: $(NOTEBOOK_DIR)/%.ipynb
	jupytext --sync $@ $<

clean:
	rm -rf **/__pycache__
