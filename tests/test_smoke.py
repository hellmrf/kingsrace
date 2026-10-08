from kingsrace import paths


def test_layout_de_dados_existe():
    for d in (paths.RAW, paths.INTERIM, paths.PROCESSED, paths.REFERENCE):
        assert d.is_dir(), d
