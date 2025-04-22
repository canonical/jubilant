import jubilant

from . import mocks

CONFIG_JSON = """
{
    "booly": {"Value": true, "type": "boolean"},
    "inty": {"Value": 42, "type": "int"},
    "floaty": {"Value": 7.5, "type": "float"},
    "stry": {"Value": "A string.", "type": "string"}
}
"""


def test_get(run: mocks.Run):
    run.handle(['juju', 'model-config', '--format', 'json'], stdout=CONFIG_JSON)

    juju = jubilant.Juju()
    values = juju.model_config()
    assert values == {
        'booly': True,
        'inty': 42,
        'floaty': 7.5,
        'stry': 'A string.',
    }


def test_get_with_model(run: mocks.Run):
    run.handle(['juju', 'model-config', '--model', 'mdl', '--format', 'json'], stdout=CONFIG_JSON)

    juju = jubilant.Juju(model='mdl')
    values = juju.model_config()
    assert values == {
        'booly': True,
        'inty': 42,
        'floaty': 7.5,
        'stry': 'A string.',
    }


def test_set(run: mocks.Run):
    run.handle(
        [
            'juju',
            'model-config',
            'booly=true',
            'inty=42',
            'floaty=7.5',
            'stry=A string.',
        ]
    )

    juju = jubilant.Juju()
    values = {
        'booly': True,
        'inty': 42,
        'floaty': 7.5,
        'stry': 'A string.',
    }
    retval = juju.model_config(values)
    assert retval is None


def test_set_with_model(run: mocks.Run):
    run.handle(['juju', 'model-config', '--model', 'mdl', 'foo=bar'])

    juju = jubilant.Juju(model='mdl')
    retval = juju.model_config({'foo': 'bar'})
    assert retval is None


def test_reset(run: mocks.Run):
    run.handle(['juju', 'model-config', '--reset', 'x,why,zed'])

    juju = jubilant.Juju()
    retval = juju.model_config({'x': None, 'why': None, 'zed': None})
    assert retval is None


def test_set_with_reset(run: mocks.Run):
    run.handle(['juju', 'model-config', 'foo=bar', '--reset', 'baz,buzz'])

    juju = jubilant.Juju()
    retval = juju.model_config({'foo': 'bar', 'baz': None, 'buzz': None})
    assert retval is None
