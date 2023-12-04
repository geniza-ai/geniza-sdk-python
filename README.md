Geniza Python SDK
=========================
[![License](https://img.shields.io/packagist/l/geniza-ai/geniza-sdk-php?logo=MIT&logoColor=ffffff)](LICENSE)

This SDK is the best and easiest way to connect to the Geniza.ai API from Python.

Installation
------------

Install using pip:

```sh
pip install geniza_sdk_python
```

Usage
-----

```python
from geniza_sdk_python import Geniza

geniza = Geniza(key, secret_key)
answer = geniza.ask_sapient_squirrel('How much wood would a woodchuck chuck?')
print(answer)
```
