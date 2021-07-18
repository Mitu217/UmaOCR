.PHONY: pytest
pytest:
	pipenv run pytest

.PHONY: fmt
fmt:
	pipenv run yapf -i -r -p ./libs ./models ./tests
	pipenv run isort ./

.PHONY: freeze
freeze:
	pip freeze > requirements.txt

.PHONY: test
test:
	pipenv run pytest
