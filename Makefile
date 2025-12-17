# STAT 159 Redlining Project Makefile
.PHONY: env all html

# Create/update environment from environment.yml
env:
	conda env update -f environment.yml --prune

# Run all notebooks (Main.ipynb + analysis/)
all:
	PYTHONPATH=. jupyter nbconvert --to notebook --execute --inplace Main.ipynb
	PYTHONPATH=. jupyter nbconvert --to notebook --execute --inplace analysis/*.ipynb


# Build MyST HTML site
html:
	myst build --html
