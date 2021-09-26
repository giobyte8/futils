# futils

## Dev environment setup

1. Setup python env and dependencies
2. Install in editable mode
3. Run unit tests
4. Happy coding 🚀

### Setup python env

```bash

# Clone project if you haven't
git clone https://github.com/giobyte8/futils
cd futils

# Initialize python virtual env through pyenv
pyenv virtualenv 3.7.7 futils
pyenv local futils

# Install development requirements
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

Setup your IDE to use interpreter from **futils** virtual env

## Install in editable mode

`setup.py` includes some settings that will make easy to work
with packages in development mode

Once your python env has been setup, go to project root and execute
`pip install -e .` ('-e' stands for 'editable').

Above command will install **futils** as an editable package so that
changes made to code will immediately be available. To provide
this functionality pip generates symlinks to current source code.

With fu installed as an editable package you can run the entry
script from root folder `python fu/futils.py [args]`


## Run unit tests

From project root directory execute:

```bash
pytest
```

## Relase new version

1. Update version number in `setup.py` file
2. Create sources distribution with `python setup.py sdist`
3. Upload through `twine upload dist/futils-<version>.tar.gz`