# Geniza Python SDK
[![License](https://img.shields.io/packagist/l/geniza-ai/geniza-sdk-php?logo=MIT&logoColor=ffffff)](LICENSE)

This SDK is the best and easiest way to connect to the Geniza.ai API from Python.

Installation
------------

## Install using pip:

```sh
pip install geniza_sdk_python
```

## Usage

```python
from geniza import Geniza

USER_KEY = "<Your User Key>"
SECRET_KEY = "<Your Secret Key>"

geniza = Geniza(USER_KEY, SECRET_KEY)
answer = geniza.ask_sapient_squirrel('How much wood would a woodchuck chuck?')
print(answer)
```
