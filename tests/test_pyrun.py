import pytest

from checker.pyrun import run_python, same_output


def test_a_program_prints_its_output(data_dir):
    r = run_python("print(1 + 1)\nprint('hi')", data_dir)
    assert r.error is None and r.output == "2\nhi\n"


def test_an_error_is_returned_as_calm_text_with_the_last_line(data_dir):
    r = run_python("x = 1\nprint(y)", data_dir)
    assert r.error is not None and "NameError: name 'y' is not defined" in r.error
    assert "Traceback" not in r.error


def test_output_before_an_error_is_kept(data_dir):
    r = run_python("print('before')\n1 / 0", data_dir)
    assert r.output == "before\n" and "ZeroDivisionError" in r.error


def test_a_runaway_program_is_stopped(data_dir):
    r = run_python("while True:\n    pass", data_dir, timeout=0.5)
    assert r.error == "That took too long, so it was stopped."


def test_the_csv_files_are_there_to_read(data_dir):
    r = run_python("import csv\nprint(len(list(csv.DictReader(open('couriers.csv')))))", data_dir)
    assert r.output == "200\n"


def test_pandas_is_there(data_dir):
    r = run_python("import pandas as pd\nprint(len(pd.read_csv('restaurants.csv')))", data_dir)
    assert r.output == "60\n"


def test_the_core_data_cannot_be_changed(data_dir):
    before = (data_dir / "couriers.csv").read_bytes()
    r = run_python("open('couriers.csv', 'w').write('oops')", data_dir)
    assert r.error is not None and "Permission" in r.error
    r = run_python("import os\nos.remove('couriers.csv')\nprint(os.path.exists('couriers.csv'))", data_dir)
    assert (data_dir / "couriers.csv").read_bytes() == before
    assert run_python("print(len(open('couriers.csv').read()) > 100)", data_dir).output == "True\n"


def test_a_run_starts_clean(data_dir):
    run_python("open('scratch.txt', 'w').write('x')", data_dir)
    assert run_python("import os\nprint(os.path.exists('scratch.txt'))", data_dir).output == "False\n"


def test_the_order_of_a_set_of_words_is_the_same_every_time(data_dir):
    code = "print(list({'pizza', 'sushi', 'acai', 'coca'}))"
    assert run_python(code, data_dir).output == run_python(code, data_dir).output


def test_a_data_folder_that_is_missing_is_an_error_not_a_crash(tmp_path):
    r = run_python("print(1)", tmp_path / "nowhere")
    assert r.error is not None


@pytest.mark.parametrize("a, b, same", [
    ("1\n2\n", "1\n2", True),
    ("0.1 0.2", "0.1   0.2", True),
    ("0.30000000000000004", "0.3", True),
    ("pizza 2", "Pizza 2", False),
    ("1 2", "1 3", False),
    ("", "", True),
])
def test_output_is_compared_by_its_words_and_numbers(a, b, same):
    assert same_output(a, b) is same
