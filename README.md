# PowerSchool Python Adapter


## Local Test

Go to the root directory of package (where setup.py is located) and run the following command:

```bash
pip install -e .
```
## Build Package

```bash
python setup.py sdist bdist_wheel
```

## Publish Package

```bash
pip install twine
twine upload dist/*
```

## Use Package

```bash
pip install psps
```