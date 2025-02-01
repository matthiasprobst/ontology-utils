pip install --upgrade build
pip install twine==6.0.1
pip install pkginfo==1.12.0
python -m build
python -m twine upload dist/*
@REM python -m twine upload --repository testpypi dist/*