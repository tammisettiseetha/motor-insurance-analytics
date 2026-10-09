from src.data_loader import check_file_exists, load_table


def test_check_file_exists(tmp_path):
    file_path = tmp_path / "sample.csv"
    file_path.write_text("id\n1\n", encoding="utf-8")

    assert check_file_exists(file_path) is True


def test_missing_file_raises_error(tmp_path):
    file_path = tmp_path / "missing.csv"

    try:
        check_file_exists(file_path)
        assert False, "Expected FileNotFoundError"
    except FileNotFoundError:
        pass


def test_load_table(tmp_path):
    file_path = tmp_path / "sample.csv"
    file_path.write_text("id,value\n1,100\n", encoding="utf-8")

    df = load_table(file_path)

    assert df.shape == (1, 2)
    assert df.loc[0, "value"] == 100