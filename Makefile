format:
	- poetry run black --line-length=120 --target-version=py38 src tests

lint:
	- poetry run flake8 --max-line-length=120

test:
	- poetry run pytest

package:
	- sam package --template-file sam-template.yaml --s3-bucket artifacts-for-lambda-ashm --output-template-file sam-output-template.yaml

ci: format lint test package

deploy:
	- sam package --template-file sam-template.yaml --s3-bucket artifacts-for-lambda-ashm --output-template-file sam-output-template.yaml
	- sam deploy --template-file sam-output-template.yaml --stack-name library --capabilities CAPABILITY_IAM 