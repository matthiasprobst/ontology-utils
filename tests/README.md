# Tests

Make sure you installed the package with the `test` extra:

```bash
pip install -e .[test]
```

## Running the tests
To test the package, you can run the following command in the terminal (from the root directory of the package):

```bash
pytest
```

This will run all the tests in the `tests` directory.

## Test coverage

To check the test coverage, you can run the following command in the terminal (from the root directory of the package):

```bash
pytest --cov=ontolutils --cov-report html
```

This will create a folder `htmlcov/` with an `index.html` file in it.

## Running pylint

To check the code style, you can run the following command in the terminal (from the root directory of the package):

```bash
pylint ontolutils --output=.pylint
```