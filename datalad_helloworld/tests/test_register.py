from datalad.tests.utils import assert_result_count


def test_register():
    import datalad.api as da
    assert hasattr(da, 'hello_py')
    assert_result_count(
        da.hello_py(),
        1,
        action='demo')

