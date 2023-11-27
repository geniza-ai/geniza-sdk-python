import subprocess


def test():
    """
    Run all unittests. Equivalent to:
    `poetry run python3 -u -m unittest`
    """
    subprocess.run(
        ['python3', '-u', '-m', 'unittest']
    )
