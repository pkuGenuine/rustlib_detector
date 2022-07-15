from typing import Any
import json
from json import JSONEncoder

from general_utils.parser import parser

class SerializeEncoder(JSONEncoder):
    def default(self, o: Any) -> Any:
        return o.__dict__

# print(json.dumps(parser.parse('ttt::xxx<\'a,\'b,T>'), indent=2, cls=SerializeEncoder))
print(parser.parse('<algo::U32X4 as rustc_std_workspace_core::ops::MulAssign<u32>>::mul_assign').pretty())