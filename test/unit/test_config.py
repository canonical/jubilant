import jubilant

from . import mocks

CONFIG_JSON = """
{
    "application-config": {
      "juju-application-path": {"value": "/", "type": "string"},
      "trust": {"value": false, "type": "bool"}
    },
    "settings": {
        "booly": {"value": true, "type": "boolean"},
        "inty": {"value": 42, "type": "int"},
        "floaty": {"value": 7.5, "type": "float"},
        "stry": {"value": "A string.", "type": "string"},
        "secrety": {"value": "secret:abcd1234", "type": "secret"}
    }
}
"""


def test_get(run: mocks.Run):
    run.handle(['juju', 'config', '--format', 'json', 'app1'], stdout=CONFIG_JSON)

    juju = jubilant.Juju()
    values = juju.config('app1')
    assert values == {
        'booly': True,
        'inty': 42,
        'floaty': 7.5,
        'stry': 'A string.',
        'secrety': jubilant.SecretURI('secret:abcd1234'),
    }


def test_get_app_config(run: mocks.Run):
    run.handle(['juju', 'config', '--format', 'json', 'appc'], stdout=CONFIG_JSON)

    juju = jubilant.Juju()
    values = juju.config('appc', app_config=True)
    assert values == {
        'juju-application-path': '/',
        'trust': False,
    }


def test_get_with_model(run: mocks.Run):
    run.handle(
        ['juju', 'config', '--model', 'mdl', '--format', 'json', 'app1'], stdout=CONFIG_JSON
    )

    juju = jubilant.Juju(model='mdl')
    values = juju.config('app1')
    assert values == {
        'booly': True,
        'inty': 42,
        'floaty': 7.5,
        'stry': 'A string.',
        'secrety': jubilant.SecretURI('secret:abcd1234'),
    }


def test_set(run: mocks.Run):
    run.handle(
        [
            'juju',
            'config',
            'app2',
            'booly=true',
            'inty=42',
            'floaty=7.5',
            'stry=A string.',
            'secrety=secret:foo',
        ]
    )

    juju = jubilant.Juju()
    values = {
        'booly': True,
        'inty': 42,
        'floaty': 7.5,
        'stry': 'A string.',
        'secrety': jubilant.SecretURI('secret:foo'),
    }
    retval = juju.config('app2', values)
    assert retval is None


def test_set_with_model(run: mocks.Run):
    run.handle(['juju', 'config', 'app2', 'foo=bar'])

    juju = jubilant.Juju()
    retval = juju.config('app2', {'foo': 'bar'})
    assert retval is None


def test_reset(run: mocks.Run):
    run.handle(['juju', 'config', 'app1', '--reset', 'x,why,zed'])

    juju = jubilant.Juju()
    retval = juju.config('app1', {'x': None, 'why': None, 'zed': None})
    assert retval is None


def test_set_with_reset(run: mocks.Run):
    run.handle(['juju', 'config', 'app1', 'foo=bar', '--reset', 'baz,buzz'])

    juju = jubilant.Juju()
    retval = juju.config('app1', {'foo': 'bar', 'baz': None, 'buzz': None})
    assert retval is None
