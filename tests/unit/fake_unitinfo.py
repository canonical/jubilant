FULL_UNITINFO = {
    'mysql/0': {
        'workload-version': '8.0.41',
        'relation-info': [
            {
                'endpoint': 'database',
                'relation-id': 5,
                'related-endpoint': 'database',
                'cross-model': False,
                'application-data': {'foo': 'bar'},
                'local-unit': {'in-scope': True, 'data': {'ingress-address': '10.0.0.1'}},
                'related-units': {
                    'wordpress/0': {'in-scope': True, 'data': {'egress-subnets': '10.1.1.1/32'}}
                },
            }
        ],
        'opened-ports': ['3306/tcp'],
        'charm': 'mysql',
        'leader': True,
        'life': 'alive',
        'machine': '0',
        'public-address': '10.0.0.1',
        'address': '10.0.0.1',
        'provider-id': 'mysql-0',
    }
}


MINIMAL_UNITINFO = {
    'mysql/0': {
        'charm': 'mysql',
        'leader': False,
    }
}
