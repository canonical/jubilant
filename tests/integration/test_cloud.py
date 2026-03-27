from __future__ import annotations

import jubilant


def test_add_and_update_cloud_client(juju: jubilant.Juju):
    cloud_name = 'it-cloud-client'

    original_endpoint = 'https://fake-endpoint-add.local:5000/v3'
    updated_endpoint = 'https://fake-endpoint-update.local:5000/v3'

    original_definition = {
        'clouds': {
            cloud_name: {
                'type': 'openstack',
                'auth-types': ['userpass'],
                'regions': {'dev-region': {'endpoint': original_endpoint}},
            }
        }
    }

    updated_definition = {
        'clouds': {
            cloud_name: {
                'type': 'openstack',
                'auth-types': ['userpass'],
                'regions': {'dev-region': {'endpoint': updated_endpoint}},
            }
        }
    }

    juju.add_cloud(cloud_name, original_definition, client=True)

    try:
        show_cloud = juju.cli('show-cloud', '--client', cloud_name, include_model=False)
        assert original_endpoint in show_cloud

        juju.update_cloud(cloud_name, updated_definition, client=True)
        show_cloud = juju.cli('show-cloud', '--client', cloud_name, include_model=False)
        assert updated_endpoint in show_cloud
    finally:
        juju.cli('remove-cloud', '--client', cloud_name, include_model=False)


def test_add_and_update_cloud_controller(juju: jubilant.Juju):
    controller = juju.show_model().controller_name
    cloud_name = 'it-cloud-controller'

    original_endpoint = 'https://fake-endpoint-add-ctrl.local:5000/v3'
    updated_endpoint = 'https://fake-endpoint-update-ctrl.local:5000/v3'

    original_definition = {
        'clouds': {
            cloud_name: {
                'type': 'openstack',
                'auth-types': ['userpass'],
                'regions': {'dev-region': {'endpoint': original_endpoint}},
            }
        }
    }

    updated_definition = {
        'clouds': {
            cloud_name: {
                'type': 'openstack',
                'auth-types': ['userpass'],
                'regions': {'dev-region': {'endpoint': updated_endpoint}},
            }
        }
    }

    juju.add_cloud(cloud_name, original_definition, controller=controller)

    try:
        show_cloud = juju.cli(
            'show-cloud', '--controller', controller, cloud_name, include_model=False
        )
        assert original_endpoint in show_cloud

        juju.update_cloud(cloud_name, updated_definition, controller=controller)
        show_cloud = juju.cli(
            'show-cloud', '--controller', controller, cloud_name, include_model=False
        )
        assert updated_endpoint in show_cloud
    finally:
        juju.cli('remove-cloud', '--controller', controller, cloud_name, include_model=False)
