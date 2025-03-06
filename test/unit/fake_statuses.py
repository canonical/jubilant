import jubilant

MINIMAL_JSON = """
{
    "model": {
        "name": "mdl",
        "type": "typ",
        "controller": "ctl",
        "cloud": "aws",
        "version": "3.0.0"
    },
    "machines": {},
    "applications": {}
}
"""

MINIMAL_STATUS = jubilant.Status(
    model=jubilant.statustypes.ModelStatus(
        name='mdl',
        type='typ',
        controller='ctl',
        cloud='aws',
        version='3.0.0',
    ),
    machines={},
    apps={},
)


SNAPPASS_JSON = """
{
    "model": {
        "name": "tt",
        "type": "caas",
        "controller": "microk8s-localhost",
        "cloud": "microk8s",
        "region": "localhost",
        "version": "3.6.1",
        "model-status": {
            "current": "available",
            "since": "24 Feb 2025 12:02:57+13:00"
        },
        "sla": "unsupported"
    },
    "machines": {},
    "applications": {
        "snappass-test": {
            "charm": "snappass-test",
            "base": {
                "name": "ubuntu",
                "channel": "20.04"
            },
            "charm-origin": "charmhub",
            "charm-name": "snappass-test",
            "charm-rev": 9,
            "charm-channel": "latest/stable",
            "scale": 1,
            "provider-id": "276bec9f-6a0c-46ea-8094-aca6337d46e5",
            "address": "10.152.183.248",
            "exposed": false,
            "application-status": {
                "current": "active",
                "message": "snappass started",
                "since": "24 Feb 2025 12:03:17+13:00"
            },
            "units": {
                "snappass-test/0": {
                    "workload-status": {
                        "current": "active",
                        "message": "snappass started",
                        "since": "24 Feb 2025 12:03:17+13:00"
                    },
                    "juju-status": {
                        "current": "idle",
                        "since": "24 Feb 2025 12:03:18+13:00",
                        "version": "3.6.1"
                    },
                    "leader": true,
                    "address": "10.1.164.138",
                    "provider-id": "snappass-test-0"
                }
            }
        }
    },
    "storage": {},
    "controller": {
        "timestamp": "12:04:55+13:00"
    }
}
"""


DATABASE_WEBAPP_JSON = """
{
    "model": {
        "name": "tt",
        "type": "caas",
        "controller": "microk8s-localhost",
        "cloud": "microk8s",
        "region": "localhost",
        "version": "3.6.1",
        "model-status": {
            "current": "available",
            "since": "24 Feb 2025 12:02:57+13:00"
        },
        "sla": "unsupported"
    },
    "machines": {},
    "applications": {
        "database": {
            "charm": "local:database-0",
            "base": {
                "name": "ubuntu",
                "channel": "22.04"
            },
            "charm-origin": "local",
            "charm-name": "database",
            "charm-rev": 0,
            "scale": 1,
            "provider-id": "fa764a56-2b71-4f7e-a6eb-b265f13adc4c",
            "address": "10.152.183.228",
            "exposed": false,
            "application-status": {
                "current": "active",
                "message": "relation-created: added new secret",
                "since": "24 Feb 2025 16:59:43+13:00"
            },
            "relations": {
                "db": [
                    {
                        "related-application": "webapp",
                        "interface": "dbi",
                        "scope": "global"
                    },
                    {
                        "related-application": "dummy",
                        "interface": "xyz",
                        "scope": "foobar"
                    }
                ]
            },
            "units": {
                "database/0": {
                    "workload-status": {
                        "current": "active",
                        "message": "relation-created: added new secret",
                        "since": "24 Feb 2025 16:59:43+13:00"
                    },
                    "juju-status": {
                        "current": "idle",
                        "since": "24 Feb 2025 16:59:44+13:00",
                        "version": "3.6.1"
                    },
                    "leader": true,
                    "address": "10.1.164.190",
                    "provider-id": "database-0",
                    "open-ports": ["8080/tcp"]
                }
            },
            "endpoint-bindings": {
                "": "alpha",
                "db": "alpha"
            }
        },
        "webapp": {
            "charm": "local:webapp-0",
            "base": {
                "name": "ubuntu",
                "channel": "22.04"
            },
            "charm-origin": "local",
            "charm-name": "webapp",
            "charm-rev": 0,
            "scale": 1,
            "provider-id": "5c49f9f9-09b3-4212-8a36-dfc081ee80b3",
            "address": "10.152.183.254",
            "exposed": false,
            "application-status": {
                "current": "active",
                "message": "relation-changed: would update web app's db secret",
                "since": "24 Feb 2025 16:59:43+13:00"
            },
            "relations": {
                "db": [
                    {
                        "related-application": "database",
                        "interface": "dbi",
                        "scope": "global"
                    }
                ]
            },
            "units": {
                "webapp/0": {
                    "workload-status": {
                        "current": "active",
                        "message": "relation-changed: would update web app's db secret",
                        "since": "24 Feb 2025 16:59:43+13:00"
                    },
                    "juju-status": {
                        "current": "idle",
                        "since": "24 Feb 2025 16:59:44+13:00",
                        "version": "3.6.1"
                    },
                    "leader": true,
                    "address": "10.1.164.179",
                    "provider-id": "webapp-0"
                }
            },
            "endpoint-bindings": {
                "": "alpha",
                "db": "alpha"
            }
        }
    },
    "storage": {},
    "controller": {
        "timestamp": "17:00:33+13:00"
    }
}
"""
