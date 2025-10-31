import jubilant


def test_str():
    uri = jubilant.SecretURI('abc')
    assert isinstance(uri, str)
    assert uri == 'abc'


def test_repr():
    uri = jubilant.SecretURI('xyz')
    assert repr(uri) == "SecretURI('xyz')"


def test_unique_identifier():
    assert jubilant.SecretURI('abc').unique_identifier == 'abc'
    assert jubilant.SecretURI('secret:xyz').unique_identifier == 'xyz'
    assert jubilant.SecretURI('secret://model-uuid/unique').unique_identifier == 'unique'
