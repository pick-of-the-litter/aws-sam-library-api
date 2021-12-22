format:
	- poetry run black --line-length=120 --target-version=py38 src tests
lint:
	- poetry run flake8 --max-line-length=120
test:
	- poetry run pytest
ci: format lint test