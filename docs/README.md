# Documentation

Install with the "docs" extra to get the required dependencies:

```bash
pip install -e "ontolutils[docs]"
```

## Build

```bash
make clean
sphinx-build -b html . _build
```

View `_build/index.html` with your browser.

https://docutils.sourceforge.io/docs/user/rst/quickref.html