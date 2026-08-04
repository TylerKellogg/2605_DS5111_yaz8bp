import sys
import io
import pytest
from bin.clean_ids import main, is_valid_id

def test_script_execution(monkeypatch, capsys):
    fake_input = io.StringIO("kcFsuxaJ1es\nasd123\n")
    monkeypatch.setattr(sys, "stdin", fake_input)

    main()

    captured = capsys.readouterr()
    assert captured.out == "kcFsuxaJ1es\n"

def run_filter(monkeypatch, capsys, text):
    monkeypatch.setattr(sys, "stdin", io.StringIO(text))
    main()
    return capsys.readouterr().out

def test_good_bad_good(monkeypatch, capsys):
    out = run_filter(monkeypatch, capsys, "kcFsuxaJ1es\nnope\nCctJNYYCPo0\n")
    assert out == "kcFsuxaJ1es\nCctJNYYCPo0\n"

def test_all_bad(monkeypatch, capsys):
    assert run_filter(monkeypatch, capsys, "abc\n1234\n") == ""

@pytest.mark.parametrize("candidate,expected", [
    ("kcFsuxaJ1es", True),     # valid 11-char id
    ("kcFsuxaJ1e", False),     # 10 chars, too short
    ("kcFsuxaJ1esX", False),   # 12 chars, too long
    ("kcFsuxaJ1e!", False),    # right length, bad character
    ("a-b_c-d_e-f", True),     # hyphen and underscore are legal
    ("", False),               # empty line
])
def test_is_valid_id(candidate, expected):
    assert is_valid_id(candidate) == expected
