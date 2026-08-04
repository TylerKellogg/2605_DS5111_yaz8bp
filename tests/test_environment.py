"""Generic environment tests: OS, python version, required tooling."""
import sys
import os
import shutil
import platform
import pytest


def test_os_is_linux():
    assert sys.platform == "linux", f"expected linux but got {sys.platform}"


def test_python_version():
    assert sys.version_info >= (3, 10), f"python too old: {platform.python_version()}"


def test_python3_available():
    assert shutil.which("python3") is not None, "python3 not found on PATH"


def test_home_directory_exists():
    home = os.path.expanduser("~")
    assert os.path.isdir(home), f"home directory missing: {home}"


@pytest.mark.parametrize("required_file", [
    "bin/clean_ids.py",
    "requirements.txt",
    "makefile",
])
def test_repo_has_required_file(required_file):
    assert os.path.isfile(required_file), f"missing required file: {required_file}"
