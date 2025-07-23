MULTIPLE_SECRETS = {
    'd0vdtqnmp25c762e7jug': {
        'revision': 2,
        'owner': '<model>',
        'name': 'admin-account',
        'created': '2025-06-03T11:39:23Z',
        'updated': '2025-06-03T11:39:35Z',
    },
    'd0vdtqeski35bidi7jug': {
        'revision': 1,
        'owner': 'user',
        'name': 'admin-password',
        'created': '2025-06-03T13:39:23Z',
        'updated': '2025-06-03T13:39:35Z',
    },
}

SINGLE_SECRET = {
    'd1ehcifmp25c76e01vhg': {
        'revision': 1,
        'expires': '2025-06-27T09:43:38Z',
        'rotation': 'daily',
        'rotates': '2025-06-27T09:43:38Z',
        'owner': 'example-charm',
        'description': 'Some description',
        'label': 'example-charm-secret',
        'created': '2025-06-26T09:43:38Z',
        'updated': '2025-06-26T09:43:38Z',
    }
}


SINGLE_SECRET_REVEALED = {
    'd1ehcifmp25c76e01vhg': {
        'revision': 1,
        'checksum': '6e7780224ca82a052f4fe9bc57f8e25d2bd012fa0ca40891a083c8f1b2748a29',
        'expires': '2025-06-27T09:43:38Z',
        'rotation': 'daily',
        'rotates': '2025-06-27T09:43:38Z',
        'owner': 'example-charm',
        'description': 'Some description',
        'label': 'example-charm-secret',
        'created': '2025-06-26T09:43:38Z',
        'updated': '2025-06-26T09:43:38Z',
        'content': {'Data': {'password': 'secret', 'username': 'admin'}},
    }
}

SINGLE_SECRET_REVISIONS = {
    'd1ehcifmp25c76e01vhg': {
        'revision': 2,
        'expires': '2025-06-27T09:43:38Z',
        'rotation': 'daily',
        'rotates': '2025-06-27T09:43:38Z',
        'owner': 'example-charm',
        'description': 'Some description',
        'label': 'example-charm-secret',
        'created': '2025-06-26T09:43:38Z',
        'updated': '2025-06-26T09:43:38Z',
        'revisions': [
            {
                'revision': 1,
                'backend': 'demo-local',
                'created': '2025-06-26T09:43:38Z',
                'updated': '2025-06-26T09:43:38Z',
                'expires': '2025-06-27T09:43:38Z',
            },
            {
                'revision': 2,
                'backend': 'demo-local',
                'created': '2025-06-27T09:43:38Z',
                'updated': '2025-06-27T09:43:38Z',
                'expires': '2025-06-28T09:43:38Z',
            },
        ],
    }
}

SINGLE_SECRET_WITH_ACCESS = {
    'd0vdtqnmp25c762e7jug': {
        'revision': 2,
        'checksum': '0a3322b0d9c2b3ac8f7bae0da21c8828d69ada7d64cb26c0f5c55d2706971c91',
        'owner': '<model>',
        'name': 'admin-account',
        'created': '2025-06-03T11:39:23Z',
        'updated': '2025-06-03T11:39:35Z',
        'access': [
            {
                'target': 'application-example-charm',
                'scope': 'model-7fc4913e-e356-4783-8e80-f2ac9f19759e',
                'role': 'view',
            }
        ],
    }
}

SINGLE_SECRET_WITH_ACCESS_REVEALED = {
    'd0vdtqnmp25c762e7jug': {
        'revision': 2,
        'checksum': '0a3322b0d9c2b3ac8f7bae0da21c8828d69ada7d64cb26c0f5c55d2706971c91',
        'owner': '<model>',
        'name': 'admin-account',
        'created': '2025-06-03T11:39:23Z',
        'updated': '2025-06-03T11:39:35Z',
        'content': {'Data': {'password': 'hunter2', 'username': 'josh'}},
        'access': [
            {
                'target': 'application-example-charm',
                'scope': 'model-7fc4913e-e356-4783-8e80-f2ac9f19759e',
                'role': 'view',
            }
        ],
    }
}

SINGLE_SECRET_WITH_ACCESS_REVISIONS = {
    'd1ehcifmp25c76e01vhg': {
        'revision': 1,
        'expires': '2025-06-27T09:43:38Z',
        'rotation': 'daily',
        'rotates': '2025-06-27T09:43:38Z',
        'owner': 'example-charm',
        'description': 'Some description',
        'label': 'example-charm-secret',
        'created': '2025-06-26T09:43:38Z',
        'updated': '2025-06-26T09:43:38Z',
        'revisions': [
            {
                'revision': 1,
                'backend': 'demo-local',
                'created': '2025-06-26T09:43:38Z',
                'updated': '2025-06-26T09:43:38Z',
                'expires': '2025-06-27T09:43:38Z',
            }
        ],
    }
}
