from LLM4Intent.common.utils import convert_tool


# Annotation 0
def func_for_test(arg1: str, arg2: int, arg3: float) -> int:
    """Annotation 1"""
    return 65535


def test_convert_tool():
    tool = convert_tool(func_for_test)
    print(tool)
    assert tool["function"]["parameters"]["properties"]["arg1"]["type"] == "string"
    assert tool["function"]["parameters"]["properties"]["arg2"]["type"] == "integer"
    assert tool["function"]["parameters"]["properties"]["arg3"]["type"] == "number"
    assert tool["function"]["parameters"]["required"] == ["arg1", "arg2", "arg3"]
    # assert tool["function"]["returns"]["type"] == "integer" # convert_tool has no returns type


# {
#     "type": "function",
#     "function": {
#         "name": "func_for_test",
#         "description": " Annotation 1\n    ",
#         "parameters": {
#             "type": "object",
#             "properties": {
#                 "arg1": {"type": "string"},
#                 "arg2": {"type": "string"},
#                 "arg3": {"type": "string"},
#                 "return": {"type": "string"},
#             },
#             "required": ["arg1", "arg2", "arg3", "return"],
#         },
#     },
# }

# {
#     "type": "function",
#     "function": {
#         "name": "func_for_test",
#         "description": "Annotation 1",
#         "parameters": {
#             "type": "object",
#             "properties": {
#                 "arg1": {"type": "string"},
#                 "arg2": {"type": "integer"},
#                 "arg3": {"type": "number"},
#             },
#             "required": ["arg1", "arg2", "arg3"],
#         },
#         "returns": {"type": "integer"},
#     },
# }
