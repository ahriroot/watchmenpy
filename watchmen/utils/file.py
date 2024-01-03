
import os
import re
from typing import List


def recursive_search_files(foldr: str, regex: re.Pattern[str]) -> List[str]:
    matched_files: List[str] = []
    for root, _dirs, files in os.walk(foldr):
        for file in files:
            if re.match(regex, file):
                matched_files.append(os.path.join(root, file))
    return matched_files
