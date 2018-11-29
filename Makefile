.PHONY: coverage

coverage:
	coverage run -m unittest discover extrpc-plugin-example/
	coverage run -m unittest discover tests/
	coverage report -m --omit=venv/*
	coverage html