"""Tests for dynamic episode discovery and public-output restriction."""
from __future__ import annotations

import importlib.util
import tempfile
from pathlib import Path

script = Path(__file__).resolve().parent / "build.py"
spec = importlib.util.spec_from_file_location("prose_reader_build", script)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


def exercise(source: Path, output: Path, names: list[str]) -> None:
    mod.SOURCE = source
    mod.DEST = output
    mod.build()
    episodes = list((output / "episodes").glob("*.html"))
    assert sorted(p.name for p in episodes) == sorted(names)
    assert not (output / "episodes" / "INDEX.html").exists()
    assert not (output / "INDEX.md").exists()
    for doc in output.rglob("*.html"):
        content = doc.read_text(encoding="utf8")
        assert "SECRET-INDEX-MARKER" not in content
        assert "status: PENDING" not in content
        assert "story_adopted:" not in content
        assert "source_plot:" not in content
    all_files = [x.relative_to(output).as_posix() for x in output.rglob("*") if x.is_file()]
    assert not any(x.startswith(("story/", "canon/", "state/", "archive/", "workflow/")) for x in all_files)


def main() -> None:
    with tempfile.TemporaryDirectory(prefix="prose-build-check-") as tmp:
        folder = Path(tmp)
        source = folder / "source"
        output = folder / "dist"
        source.mkdir()
        (source / "INDEX.md").write_text("SECRET-INDEX-MARKER", encoding="utf8")
        (source / "第001話.md").write_text(
            "---\ntype: episode_prose\nstatus: PENDING\nstory_adopted: false\nsource_plot: secret/path\n---\n"
            "# 第001話「ランダムは1回だけ」\n\n　本文です。\n", encoding="utf8")
        (source / "第003話.md").write_text(
            "# 第003話「三番目の題名」\n\n　本文です。\n", encoding="utf8")
        exercise(source, output, ["001.html", "003.html"])
        home = (output / "index.html").read_text(encoding="utf8")
        assert "ランダムは1回だけ" in home
        assert "三番目の題名" in home
        assert home.index("第001話") < home.index("第003話")
        (source / "第002話.md").write_text("# 第002話「新しい話」\n\n　本文\n", encoding="utf8")
        exercise(source, output, ["001.html", "002.html", "003.html"])
        (source / "第001話.md").unlink()
        exercise(source, output, ["002.html", "003.html"])
        assert "第001話" not in (output / "index.html").read_text(encoding="utf8")
        print("PASS: dynamic discovery, addition, removal, gap, titles and INDEX/status exclusion")


if __name__ == "__main__":
    main()
