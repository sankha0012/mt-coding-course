from checker.__main__ import main


def test_clean_lesson_exits_zero_and_prints_reports(write_strand, data_dir, steps, capsys):
    folder = write_strand(steps)
    assert main([str(folder), "--data", str(data_dir)]) == 0
    out = capsys.readouterr().out
    assert "Spacing" in out and "Load" in out and "0 failures, 1 warnings" in out


def test_broken_lesson_exits_one_and_names_the_step(write_strand, data_dir, steps, capsys):
    steps[1]["model"] = "SELECT COUNT(*) FROM restaurant"
    folder = write_strand(steps)
    assert main([str(folder), "--data", str(data_dir)]) == 1
    assert "FAIL t-01 step 2: model answer does not run" in capsys.readouterr().out


def test_missing_files_exit_two(tmp_path, data_dir, capsys):
    assert main([str(tmp_path), "--data", str(data_dir)]) == 2
    assert "ERROR" in capsys.readouterr().out
