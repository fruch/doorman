import os.path

import pytest
from compose.cli.main import TopLevelCommand, project_from_options

@pytest.fixture(scope="session")
def docker_compose(request):
    """
    :type request: _pytest.python.FixtureRequest
    """

    options = {"--no-deps": False,
               "--abort-on-container-exit": False,
               "SERVICE": "",
               "--remove-orphans": False,
               "--no-recreate": True,
               "--force-recreate": False,
               "--build": False,
               '--no-build': False,
               '--no-color': False,
               "--rmi": "none",
               "--volumes": "",
               "--follow": False,
               "--timestamps": False,
               "--tail": "all",
               "-d": True,
               }

    project = project_from_options(os.path.dirname(__file__), options)
    cmd = TopLevelCommand(project)
    cmd.up(options)

    def fin():
        cmd.logs(options)
        cmd.down(options)

    request.addfinalizer(fin)