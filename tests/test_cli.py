"""End-to-end CLI tests, entirely offline."""

import pytest
from jargon_simplifier import cli

SAMPLE = "Please be advised that, pursuant to the lease, the lessee shall remit payment on time.\n"


def run(argv):
    return cli.main(argv)


def test_cli_stdout_report(tmp_path, capsys):
    path = tmp_path / "in.txt"
    path.write_text(SAMPLE, encoding="utf-8")
    assert run([str(path)]) == 0
    out = capsys.readouterr().out
    assert "ORIGINAL" in out and "PLAIN ENGLISH" in out
    assert "Source: offline" in out
    assert "Glossary" in out
    assert "pursuant to" in out
    # Nothing was written to disk.
    assert path.read_text(encoding="utf-8") == SAMPLE


def test_cli_unified_and_plain_formats(tmp_path, capsys):
    path = tmp_path / "in.txt"
    path.write_text(SAMPLE, encoding="utf-8")
    for fmt in ("unified", "plain"):
        assert run([str(path), "-f", fmt]) == 0
        assert capsys.readouterr().out.strip()


def test_output_file_created(tmp_path, capsys):
    path = tmp_path / "in.txt"
    path.write_text(SAMPLE, encoding="utf-8")
    out_path = tmp_path / "plain.txt"
    assert run([str(path), "-o", str(out_path), "-f", "plain"]) == 0
    assert "under the lease" in out_path.read_text(encoding="utf-8").lower()
    assert out_path.read_text(encoding="utf-8").startswith("Under the lease")
    assert path.read_text(encoding="utf-8") == SAMPLE


def test_output_refuses_clobber_without_explicit_flag(tmp_path, capsys):
    path = tmp_path / "in.txt"
    path.write_text(SAMPLE, encoding="utf-8")
    target = tmp_path / "existing.txt"
    target.write_text("keep me", encoding="utf-8")

    with pytest.raises(SystemExit):
        run([str(path), "-o", str(target)])
    assert target.read_text(encoding="utf-8") == "keep me"

    assert run([str(path), "-o", str(target), "--overwrite", "-f", "plain"]) == 0
    assert "under the lease" in target.read_text(encoding="utf-8").lower()


def test_write_flag_overwrites_input_in_place(tmp_path, capsys):
    path = tmp_path / "in.txt"
    path.write_text(SAMPLE, encoding="utf-8")
    assert run([str(path), "--write", "-f", "plain"]) == 0
    assert "under the lease" in path.read_text(encoding="utf-8").lower()


def test_write_flag_errors_on_stdin(tmp_path, capsys, monkeypatch):
    import io
    monkeypatch.setattr("sys.stdin", io.StringIO(SAMPLE))
    with pytest.raises(SystemExit):
        run(["-", "--write"])


def test_stdin_reading(tmp_path, capsys, monkeypatch):
    import io
    monkeypatch.setattr("sys.stdin", io.StringIO(SAMPLE))
    assert run(["-t", "friend"]) == 0
    out = capsys.readouterr().out
    assert "Glossary" in out


def test_llm_flag_without_endpoint_falls_back(tmp_path, capsys):
    path = tmp_path / "in.txt"
    path.write_text(SAMPLE, encoding="utf-8")
    # Port 1 should be unreachable quickly; small timeout keeps the test fast.
    assert run([str(path), "--llm", "--url", "http://127.0.0.1:1/v1", "--timeout", "3"]) == 0
    out = capsys.readouterr().out
    assert "Source: offline" in out
    assert "fell back to offline engine" in out


def test_empty_input_reports_meaningfully(tmp_path, capsys):
    path = tmp_path / "empty.txt"
    path.write_text("\n\n", encoding="utf-8")
    with pytest.raises(SystemExit):
        run([str(path)])


def test_bad_tone_exits_cleanly(tmp_path):
    path = tmp_path / "in.txt"
    path.write_text(SAMPLE, encoding="utf-8")
    with pytest.raises(SystemExit):
        run([str(path), "-t", "shouty"])
