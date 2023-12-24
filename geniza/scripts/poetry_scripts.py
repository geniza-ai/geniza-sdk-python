import subprocess


def lint():
    """
    Runs Pylint in the project virtualenv.
    """
    subprocess.run(['pylint', '--recursive=y', '.'], check=False)


def test():
    """
    Run all unit tests in the project virtualenv.
    """
    subprocess.run(['python3', '-u', '-m', 'unittest'], check=False)
