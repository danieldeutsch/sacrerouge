from typing import List

from sacrerouge.common import Registrable
from sacrerouge.data import EvalInstance


class DatasetReader(Registrable):
    def read(self) -> List[EvalInstance]:
        raise NotImplementedError
