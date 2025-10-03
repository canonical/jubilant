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

STATUS_ERRORS_JSON = """
{
    "model": {
        "name": "tt",
        "type": "caas",
        "controller": "microk8s-localhost",
        "cloud": "microk8s",
        "version": "3.6.1",
        "model-status": {
            "status-error": "model status error!"
        }
    },
    "machines": {
        "machine-failed": {
            "status-error": "machine status error!"
        }
    },
    "applications": {
        "app-failed": {
            "status-error": "app status error!"
        },
        "unit-failed": {
            "charm": "unit-failed",
            "charm-origin": "origin",
            "charm-name": "unit-failed",
            "charm-rev": 0,
            "exposed": false,
            "units": {
                "unit-failed/0": {
                    "status-error": "unit status error!"
                }
            }
        }
    },
    "offers": {
        "offer-failed": {
            "status-error": "offer status error!"
        }
    },
    "application-endpoints": {
        "remote-app-failed": {
            "status-error": "remote app status error!"
        }
    }
}
"""

SUBORDINATES_JSON = """
{
    "model": {
        "name": "t",
        "type": "iaas",
        "controller": "lxd",
        "cloud": "localhost",
        "region": "localhost",
        "version": "3.6.4",
        "model-status": {
            "current": "available",
            "since": "09 Jun 2025 11:04:48+12:00"
        },
        "sla": "unsupported"
    },
    "machines": {
        "1": {
            "juju-status": {
                "current": "started",
                "since": "09 Jun 2025 11:14:50+12:00",
                "version": "3.6.4"
            },
            "hostname": "juju-663cb8-1",
            "dns-name": "10.103.56.99",
            "ip-addresses": [
                "10.103.56.99",
                "fd42:63bf:36e0:2d9b:216:3eff:fe37:b62f"
            ],
            "instance-id": "juju-663cb8-1",
            "machine-status": {
                "current": "running",
                "message": "Running",
                "since": "09 Jun 2025 11:14:06+12:00"
            },
            "modification-status": {
                "current": "applied",
                "since": "09 Jun 2025 11:14:02+12:00"
            },
            "base": {
                "name": "ubuntu",
                "channel": "24.04"
            },
            "network-interfaces": {
                "eth0": {
                    "ip-addresses": [
                        "10.103.56.99",
                        "fd42:63bf:36e0:2d9b:216:3eff:fe37:b62f"
                    ],
                    "mac-address": "00:16:3e:37:b6:2f",
                    "gateway": "10.103.56.1 10.103.56.1",
                    "space": "alpha",
                    "is-up": true
                }
            },
            "constraints": "arch=amd64",
            "hardware": "arch=amd64 cores=0 mem=0M virt-type=container"
        },
        "2": {
            "juju-status": {
                "current": "started",
                "since": "09 Jun 2025 11:22:29+12:00",
                "version": "3.6.4"
            },
            "hostname": "juju-663cb8-2",
            "dns-name": "10.103.56.129",
            "ip-addresses": [
                "10.103.56.129",
                "fd42:63bf:36e0:2d9b:216:3eff:fe4f:a835"
            ],
            "instance-id": "juju-663cb8-2",
            "machine-status": {
                "current": "running",
                "message": "Running",
                "since": "09 Jun 2025 11:21:40+12:00"
            },
            "modification-status": {
                "current": "applied",
                "since": "09 Jun 2025 11:21:35+12:00"
            },
            "base": {
                "name": "ubuntu",
                "channel": "24.04"
            },
            "network-interfaces": {
                "eth0": {
                    "ip-addresses": [
                        "10.103.56.129",
                        "fd42:63bf:36e0:2d9b:216:3eff:fe4f:a835"
                    ],
                    "mac-address": "00:16:3e:4f:a8:35",
                    "gateway": "10.103.56.1 10.103.56.1",
                    "space": "alpha",
                    "is-up": true
                }
            },
            "constraints": "arch=amd64",
            "hardware": "arch=amd64 cores=0 mem=0M virt-type=container"
        }
    },
    "applications": {
        "nrpe": {
            "charm": "nrpe",
            "base": {
                "name": "ubuntu",
                "channel": "24.04"
            },
            "charm-origin": "charmhub",
            "charm-name": "nrpe",
            "charm-rev": 165,
            "charm-channel": "latest/stable",
            "exposed": false,
            "application-status": {
                "current": "blocked",
                "message": "Nagios server not configured or related",
                "since": "09 Jun 2025 11:17:02+12:00"
            },
            "relations": {
                "general-info": [
                    {
                        "related-application": "ubun2",
                        "interface": "juju-info",
                        "scope": "container"
                    },
                    {
                        "related-application": "ubuntu",
                        "interface": "juju-info",
                        "scope": "container"
                    }
                ]
            },
            "subordinate-to": [
                "ubun2",
                "ubuntu"
            ],
            "endpoint-bindings": {
                "": "alpha",
                "general-info": "alpha",
                "local-monitors": "alpha",
                "monitors": "alpha",
                "nrpe": "alpha",
                "nrpe-external-master": "alpha"
            }
        },
        "ubun2": {
            "charm": "ubuntu",
            "base": {
                "name": "ubuntu",
                "channel": "24.04"
            },
            "charm-origin": "charmhub",
            "charm-name": "ubuntu",
            "charm-rev": 26,
            "charm-channel": "latest/stable",
            "exposed": false,
            "application-status": {
                "current": "active",
                "since": "09 Jun 2025 11:22:39+12:00"
            },
            "relations": {
                "juju-info": [
                    {
                        "related-application": "nrpe",
                        "interface": "juju-info",
                        "scope": "container"
                    }
                ]
            },
            "units": {
                "ubun2/0": {
                    "workload-status": {
                        "current": "active",
                        "since": "09 Jun 2025 11:22:39+12:00"
                    },
                    "juju-status": {
                        "current": "idle",
                        "since": "09 Jun 2025 11:22:41+12:00",
                        "version": "3.6.4"
                    },
                    "leader": true,
                    "machine": "2",
                    "public-address": "10.103.56.129",
                    "subordinates": {
                        "nrpe/2": {
                            "workload-status": {
                                "current": "blocked",
                                "message": "Nagios server not configured or related",
                                "since": "09 Jun 2025 11:25:06+12:00"
                            },
                            "juju-status": {
                                "current": "idle",
                                "since": "09 Jun 2025 11:25:06+12:00",
                                "version": "3.6.4"
                            },
                            "open-ports": [
                                "icmp",
                                "5666/tcp"
                            ],
                            "public-address": "10.103.56.129"
                        }
                    }
                }
            },
            "version": "24.04"
        },
        "ubuntu": {
            "charm": "ubuntu",
            "base": {
                "name": "ubuntu",
                "channel": "24.04"
            },
            "charm-origin": "charmhub",
            "charm-name": "ubuntu",
            "charm-rev": 26,
            "charm-channel": "latest/stable",
            "exposed": false,
            "application-status": {
                "current": "active",
                "since": "09 Jun 2025 11:15:00+12:00"
            },
            "relations": {
                "juju-info": [
                    {
                        "related-application": "nrpe",
                        "interface": "juju-info",
                        "scope": "container"
                    }
                ]
            },
            "units": {
                "ubuntu/1": {
                    "workload-status": {
                        "current": "active",
                        "since": "09 Jun 2025 11:15:00+12:00"
                    },
                    "juju-status": {
                        "current": "idle",
                        "since": "09 Jun 2025 11:15:02+12:00",
                        "version": "3.6.4"
                    },
                    "leader": true,
                    "machine": "1",
                    "public-address": "10.103.56.99",
                    "subordinates": {
                        "nrpe/1": {
                            "workload-status": {
                                "current": "blocked",
                                "message": "Nagios server not configured or related",
                                "since": "09 Jun 2025 11:17:02+12:00"
                            },
                            "juju-status": {
                                "current": "idle",
                                "since": "09 Jun 2025 11:17:02+12:00",
                                "version": "3.6.4"
                            },
                            "leader": true,
                            "open-ports": [
                                "icmp",
                                "5666/tcp"
                            ],
                            "public-address": "10.103.56.99"
                        }
                    }
                }
            },
            "version": "24.04"
        }
    },
    "storage": {},
    "controller": {
        "timestamp": "12:11:53+12:00"
    }
}
"""

MINIMAL_JSON29 = """
{
    "model": {
        "name": "mdl",
        "type": "typ",
        "controller": "ctl",
        "cloud": "aws",
        "version": "2.9.52"
    },
    "machines": {},
    "applications": {}
}
"""

MINIMAL_STATUS29 = jubilant.Status(
    model=jubilant.statustypes.ModelStatus(
        name='mdl',
        type='typ',
        controller='ctl',
        cloud='aws',
        version='2.9.52',
    ),
    machines={},
    apps={},
)


SNAPPASS_JSON29 = """
{
    "model": {
        "name": "tt",
        "type": "caas",
        "controller": "microk8s-localhost",
        "cloud": "microk8s",
        "region": "localhost",
        "version": "2.9.50",
        "model-status": {
            "current": "available",
            "since": "15 Jul 2025 21:16:45+12:00"
        },
        "sla": "unsupported"
    },
    "machines": {},
    "applications": {
        "snappass-test": {
            "charm": "snappass-test",
            "series": "kubernetes",
            "os": "kubernetes",
            "charm-origin": "charmhub",
            "charm-name": "snappass-test",
            "charm-rev": 9,
            "charm-channel": "stable",
            "scale": 1,
            "provider-id": "d16723dd-1ec7-4df3-b0fd-cc1422f71595",
            "address": "10.152.183.121",
            "exposed": false,
            "application-status": {
                "current": "active",
                "message": "snappass started",
                "since": "15 Jul 2025 21:18:37+12:00"
            },
            "units": {
                "snappass-test/0": {
                    "workload-status": {
                        "current": "active",
                        "message": "snappass started",
                        "since": "15 Jul 2025 21:18:37+12:00"
                    },
                    "juju-status": {
                        "current": "idle",
                        "since": "15 Jul 2025 21:19:06+12:00",
                        "version": "2.9.50"
                    },
                    "leader": true,
                    "address": "10.1.216.163",
                    "provider-id": "snappass-test-0"
                }
            }
        }
    },
    "storage": {},
    "controller": {
        "timestamp": "21:24:58+12:00"
    }
}
"""


DATABASE_WEBAPP_JSON29 = """
{
    "model": {
        "name": "tt",
        "type": "caas",
        "controller": "microk8s-localhost",
        "cloud": "microk8s",
        "region": "localhost",
        "version": "2.9.50",
        "model-status": {
            "current": "available",
            "since": "15 Jul 2025 21:16:45+12:00"
        },
        "sla": "unsupported"
    },
    "machines": {},
    "applications": {
        "database": {
            "charm": "local:jammy/database-0",
            "series": "jammy",
            "os": "ubuntu",
            "charm-origin": "local",
            "charm-name": "database",
            "charm-rev": 0,
            "scale": 1,
            "provider-id": "2d2fe9b8-ce7d-43fe-b9a6-484408f01296",
            "address": "10.152.183.254",
            "exposed": false,
            "application-status": {
                "current": "waiting",
                "message": "installing agent",
                "since": "15 Jul 2025 21:46:18+12:00"
            },
            "relations": {
                "db": [
                    "webapp"
                ]
            },
            "units": {
                "database/0": {
                    "workload-status": {
                        "current": "error",
                        "message": "hook failed: \"db-relation-created\" for webapp:db",
                        "since": "15 Jul 2025 21:51:59+12:00"
                    },
                    "juju-status": {
                        "current": "idle",
                        "since": "15 Jul 2025 21:51:59+12:00",
                        "version": "2.9.50"
                    },
                    "leader": true,
                    "address": "10.1.216.174",
                    "provider-id": "database-0"
                }
            },
            "endpoint-bindings": {
                "": "alpha",
                "db": "alpha"
            }
        },
        "webapp": {
            "charm": "local:jammy/webapp-0",
            "series": "jammy",
            "os": "ubuntu",
            "charm-origin": "local",
            "charm-name": "webapp",
            "charm-rev": 0,
            "scale": 1,
            "provider-id": "55bbcb2f-cbe5-409c-9b93-724d412860e9",
            "address": "10.152.183.153",
            "exposed": false,
            "application-status": {
                "current": "waiting",
                "message": "installing agent",
                "since": "15 Jul 2025 21:44:43+12:00"
            },
            "relations": {
                "db": [
                    "database"
                ]
            },
            "units": {
                "webapp/0": {
                    "workload-status": {
                        "current": "unknown",
                        "since": "15 Jul 2025 21:44:36+12:00"
                    },
                    "juju-status": {
                        "current": "idle",
                        "since": "15 Jul 2025 21:46:52+12:00",
                        "version": "2.9.50"
                    },
                    "leader": true,
                    "address": "10.1.216.173",
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
        "timestamp": "21:53:43+12:00"
    }
}
"""

STATUS_ERRORS_JSON29 = """
{
    "model": {
        "name": "tt",
        "type": "caas",
        "controller": "microk8s-localhost",
        "cloud": "microk8s",
        "version": "2.9.52",
        "model-status": {
            "status-error": "model status error!"
        }
    },
    "machines": {
        "machine-failed": {
            "status-error": "machine status error!"
        }
    },
    "applications": {
        "app-failed": {
            "status-error": "app status error!"
        },
        "unit-failed": {
            "charm": "unit-failed",
            "series": "jammy",
            "os": "ubuntu",
            "charm-origin": "origin",
            "charm-name": "unit-failed",
            "charm-rev": 0,
            "exposed": false,
            "units": {
                "unit-failed/0": {
                    "status-error": "unit status error!"
                }
            }
        }
    },
    "offers": {
        "offer-failed": {
            "status-error": "offer status error!"
        }
    },
    "application-endpoints": {
        "remote-app-failed": {
            "status-error": "remote app status error!"
        }
    }
}
"""

SUBORDINATES_JSON29 = """
{
    "model": {
        "name": "t",
        "type": "iaas",
        "controller": "lxd",
        "cloud": "localhost",
        "region": "localhost",
        "version": "2.9.52",
        "model-status": {
            "current": "available",
            "since": "15 Jul 2025 22:07:41+12:00"
        },
        "sla": "unsupported"
    },
    "machines": {
        "0": {
            "juju-status": {
                "current": "started",
                "since": "15 Jul 2025 22:20:36+12:00",
                "version": "2.9.52"
            },
            "hostname": "juju-4def64-0",
            "dns-name": "10.36.4.173",
            "ip-addresses": [
                "10.36.4.173",
                "fd42:51ee:3f62:3b1f:216:3eff:fe08:2b06"
            ],
            "instance-id": "juju-4def64-0",
            "machine-status": {
                "current": "running",
                "message": "Running",
                "since": "15 Jul 2025 22:18:07+12:00"
            },
            "modification-status": {
                "current": "applied",
                "since": "15 Jul 2025 22:17:39+12:00"
            },
            "series": "jammy",
            "network-interfaces": {
                "eth0": {
                    "ip-addresses": [
                        "10.36.4.173",
                        "fd42:51ee:3f62:3b1f:216:3eff:fe08:2b06"
                    ],
                    "mac-address": "00:16:3e:08:2b:06",
                    "gateway": "10.36.4.1 10.36.4.1",
                    "space": "alpha",
                    "is-up": true
                }
            },
            "constraints": "arch=amd64",
            "hardware": "arch=amd64 cores=0 mem=0M"
        },
        "1": {
            "juju-status": {
                "current": "started",
                "since": "15 Jul 2025 22:20:36+12:00",
                "version": "2.9.52"
            },
            "hostname": "juju-4def64-1",
            "dns-name": "10.36.4.84",
            "ip-addresses": [
                "10.36.4.84",
                "fd42:51ee:3f62:3b1f:216:3eff:fe23:e793"
            ],
            "instance-id": "juju-4def64-1",
            "machine-status": {
                "current": "running",
                "message": "Running",
                "since": "15 Jul 2025 22:18:17+12:00"
            },
            "modification-status": {
                "current": "applied",
                "since": "15 Jul 2025 22:17:45+12:00"
            },
            "series": "jammy",
            "network-interfaces": {
                "eth0": {
                    "ip-addresses": [
                        "10.36.4.84",
                        "fd42:51ee:3f62:3b1f:216:3eff:fe23:e793"
                    ],
                    "mac-address": "00:16:3e:23:e7:93",
                    "gateway": "10.36.4.1 10.36.4.1",
                    "space": "alpha",
                    "is-up": true
                }
            },
            "constraints": "arch=amd64",
            "hardware": "arch=amd64 cores=0 mem=0M"
        }
    },
    "applications": {
        "nrpe": {
            "charm": "nrpe",
            "series": "jammy",
            "os": "ubuntu",
            "charm-origin": "charmhub",
            "charm-name": "nrpe",
            "charm-rev": 165,
            "charm-channel": "stable",
            "exposed": false,
            "application-status": {
                "current": "blocked",
                "message": "Nagios server not configured or related",
                "since": "15 Jul 2025 22:23:12+12:00"
            },
            "relations": {
                "general-info": [
                    "ubun2",
                    "ubuntu"
                ]
            },
            "subordinate-to": [
                "ubun2",
                "ubuntu"
            ],
            "endpoint-bindings": {
                "": "alpha",
                "general-info": "alpha",
                "local-monitors": "alpha",
                "monitors": "alpha",
                "nrpe": "alpha",
                "nrpe-external-master": "alpha"
            }
        },
        "ubun2": {
            "charm": "ubuntu",
            "series": "jammy",
            "os": "ubuntu",
            "charm-origin": "charmhub",
            "charm-name": "ubuntu",
            "charm-rev": 26,
            "charm-channel": "stable",
            "exposed": false,
            "application-status": {
                "current": "active",
                "since": "15 Jul 2025 22:21:35+12:00"
            },
            "relations": {
                "juju-info": [
                    "nrpe"
                ]
            },
            "units": {
                "ubun2/0": {
                    "workload-status": {
                        "current": "active",
                        "since": "15 Jul 2025 22:21:35+12:00"
                    },
                    "juju-status": {
                        "current": "idle",
                        "since": "15 Jul 2025 22:21:42+12:00",
                        "version": "2.9.52"
                    },
                    "leader": true,
                    "machine": "1",
                    "public-address": "10.36.4.84",
                    "subordinates": {
                        "nrpe/0": {
                            "workload-status": {
                                "current": "blocked",
                                "message": "Nagios server not configured or related",
                                "since": "15 Jul 2025 22:23:12+12:00"
                            },
                            "juju-status": {
                                "current": "idle",
                                "since": "15 Jul 2025 22:23:12+12:00",
                                "version": "2.9.52"
                            },
                            "leader": true,
                            "open-ports": [
                                "icmp",
                                "5666/tcp"
                            ],
                            "public-address": "10.36.4.84"
                        }
                    }
                }
            },
            "version": "22.04"
        },
        "ubuntu": {
            "charm": "ubuntu",
            "series": "jammy",
            "os": "ubuntu",
            "charm-origin": "charmhub",
            "charm-name": "ubuntu",
            "charm-rev": 26,
            "charm-channel": "stable",
            "exposed": false,
            "application-status": {
                "current": "active",
                "since": "15 Jul 2025 22:21:35+12:00"
            },
            "relations": {
                "juju-info": [
                    "nrpe"
                ]
            },
            "units": {
                "ubuntu/0": {
                    "workload-status": {
                        "current": "active",
                        "since": "15 Jul 2025 22:21:35+12:00"
                    },
                    "juju-status": {
                        "current": "idle",
                        "since": "15 Jul 2025 22:21:43+12:00",
                        "version": "2.9.52"
                    },
                    "leader": true,
                    "machine": "0",
                    "public-address": "10.36.4.173",
                    "subordinates": {
                        "nrpe/1": {
                            "workload-status": {
                                "current": "blocked",
                                "message": "Nagios server not configured or related",
                                "since": "15 Jul 2025 22:23:11+12:00"
                            },
                            "juju-status": {
                                "current": "idle",
                                "since": "15 Jul 2025 22:23:12+12:00",
                                "version": "2.9.52"
                            },
                            "open-ports": [
                                "icmp",
                                "5666/tcp"
                            ],
                            "public-address": "10.36.4.173"
                        }
                    }
                }
            },
            "version": "22.04"
        }
    },
    "storage": {},
    "controller": {
        "timestamp": "22:25:16+12:00"
    }
}
"""
