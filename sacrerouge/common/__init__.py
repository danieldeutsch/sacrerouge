import os
from pathlib import Path

from sacrerouge.common.checks import ConfigurationError
from sacrerouge.common.params import Params
from sacrerouge.common.from_params import FromParams
from sacrerouge.common.registrable import Registrable
from sacrerouge.common.tempdir import TemporaryDirectory

DATA_ROOT = os.getenv('SACREROUGE_DATA_ROOT', Path.home() / '.sacrerouge')
