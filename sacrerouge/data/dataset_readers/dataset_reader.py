from typing import List

from sacrerouge.common import Registrable
from sacrerouge.data import EvalInstance


class DatasetReader(Registrable):
    def read(self, *args: List[str]) -> List[EvalInstance]:
        raise NotImplementedError
