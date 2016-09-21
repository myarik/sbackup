test:
	py.test -q ./tests/ --capture=no

test_style:
	py.test -c setup.cfg --pep8 --junitxml=reports/pep8.report
	py.test --pylint --junitxml=reports/pylint.report

cov-dev:
	py.test --cov=main --cov-report=term --cov-report=html tests
	@echo "open file://`pwd`/coverage/index.html"

clean:
	rm -rf `find . -name __pycache__`
	rm -f `find . -type f -name '*.py[co]' `
	rm -f `find . -type f -name '*~' `
	rm -f `find . -type f -name '.*~' `
	rm -f `find . -type f -name '@*' `
	rm -f `find . -type f -name '#*#' `
	rm -f `find . -type f -name '*.orig' `
	rm -f `find . -type f -name '*.rej' `
	rm -f .coverage
	rm -rf coverage
	rm -rf build
	rm -rf cover
