from typing import List

from common.handle import Response
from watchmen.utils import output
from watchmen.utils.types import String


def print_result(res: List[Response]) -> None:
    for r in res:
        data = r.data
        if 'String' in r.data:
            data = r.data['String']
        result = f'{r.code}\t{r.msg}\t{data}'
        if r.code == 10000:
            output(String.green(result))
        elif r.code == 40000:
            output(String.yellow(result))
        elif r.code == 50000:
            output(String.red(result))
        else:
            output(result)
