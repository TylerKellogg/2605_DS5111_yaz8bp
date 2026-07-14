import sys
import io
import pytest
from bin.clean_ids import main

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

def test_10_chars_rejected(monkeypatch, capsys):
    assert run_filter(monkeypatch, capsys, "kcFsuxaJ1e\n") == ""

def test_12_chars_rejected(monkeypatch, capsys):
    assert run_filter(monkeypatch, capsys, "kcFsuxaJ1esX\n") == ""

def test_invalid_characters(monkeypatch, capsys):
    assert run_filter(monkeypatch, capsys, "kcFsuxaJ1e!\n") == ""

def test_hyphen_underscore_ok(monkeypatch, capsys):
    assert run_filter(monkeypatch, capsys, "a-b_c-d_e-f\n") == "a-b_c-d_e-f\n"
