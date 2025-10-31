FULL_MODELINFO = {
    't': {
        'name': 'admin/t',
        'short-name': 't',
        'model-uuid': '910dff48-2bc2-4007-858b-e382d2fcdc0f',
        'model-type': 'iaas',
        'controller-uuid': '82fa1bd2-e1a6-4aeb-87c3-5aaed212d4ff',
        'controller-name': 'localhost-localhost',
        'is-controller': False,
        'owner': 'admin',
        'cloud': 'localhost',
        'region': 'localhost',
        'type': 'lxd',
        'life': 'alive',
        'status': {'current': 'available', 'since': '18 hours ago'},
        'users': {
            'admin': {
                'display-name': 'admin',
                'access': 'admin',
                'last-connection': '58 minutes ago',
            }
        },
        'sla': 'unsupported',
        'agent-version': '3.6.10',
        'credential': {
            'name': 'localhost',
            'owner': 'admin',
            'cloud': 'localhost',
            'validity-check': 'valid',
        },
        'supported-features': [
            {
                'name': 'juju',
                'description': 'the version of Juju used by the model',
                'version': '3.6.10',
            }
        ],
    }
}

MINIMAL_MODELINFO = {
    'min': {
        'name': 'admin/min',
        'short-name': 'min',
        'model-uuid': '910dff48-2bc2-4007-858b-e382d2fcdc0e',
        'model-type': 'caas',
        'controller-uuid': '82fa1bd2-e1a6-4aeb-87c3-5aaed212d4fe',
        'controller-name': 'ctrl',
        'is-controller': True,
        'cloud': 'aws',
        'life': 'dying',
    },
}
