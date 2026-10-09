"""Single-case quote CLI, driven with the fake client and a temp folder."""

import io
import json

import quote
from tests.fakes import FakeLLM

CLEAN = (
    "Hi, I'm Maya Chen, 29, software engineer in Ohio. I rent an apartment and want "
    "$100,000 of renters insurance. No prior claims. SSN 900-01-0001."
)


def test_completed_case_is_saved(tmp_path, capsys):
    code = quote.main([CLEAN], llm=FakeLLM(), quote_dir=tmp_path)
    assert code == 0
    path = tmp_path / "900-01-0001.json"
    assert path.exists()
    document = json.loads(path.read_text(encoding="utf-8"))
    assert document["status"] == "completed"
    assert document["case_id"] == "900-01-0001"
    out = capsys.readouterr().out
    assert "warm-up" in out
    assert "status=completed" in out


def test_text_without_an_ssn_exits_2_and_writes_nothing(tmp_path, capsys):
    fake = FakeLLM()
    code = quote.main(["Maya Chen needs renters insurance."], llm=fake, quote_dir=tmp_path)
    assert code == 2
    assert list(tmp_path.iterdir()) == []
    assert fake.calls == []
    assert "SSN" in capsys.readouterr().out


def test_empty_input_prints_usage(tmp_path, capsys):
    code = quote.main([], llm=FakeLLM(), quote_dir=tmp_path, stdin=io.StringIO(""))
    assert code == 2
    assert "usage" in capsys.readouterr().out
    assert list(tmp_path.iterdir()) == []


def test_stdin_is_read_when_no_argument(tmp_path):
    code = quote.main([], llm=FakeLLM(), quote_dir=tmp_path, stdin=io.StringIO(CLEAN + "\n"))
    assert code == 0
    assert (tmp_path / "900-01-0001.json").exists()


def test_unknown_ssn_escalates_with_bureau_span(tmp_path):
    fake = FakeLLM()
    code = quote.main(
        ["New applicant Nora Kim, 33, teacher in Maine. SSN 900-99-9999."],
        llm=fake,
        quote_dir=tmp_path,
    )
    assert code == 1
    assert fake.calls == []
    document = json.loads((tmp_path / "900-99-9999.json").read_text(encoding="utf-8"))
    assert document["status"] == "escalated"
    assert document["recommendation"]["decision"] == "refer"
    assert document["spans"][0]["agent"] == "bureau_lookup"


def test_no_save_prints_only(tmp_path):
    code = quote.main(["--no-save", CLEAN], llm=FakeLLM(), quote_dir=tmp_path)
    assert code == 0
    assert list(tmp_path.iterdir()) == []
