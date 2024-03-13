import dbus
import helper

SUCCESS = 0x0000
INVALID_STATE = 0x0001
INVALID_CONFIGURATION = 0x0002
INVALID_LENGTH = 0x0003
INVALID_PARAM = 0x0004
INVALID_COMMAND = 0xFFFF

# returns command result in bytes
def get_command_result(command_op_code, response_status):
    opcode_in_bytes = command_op_code.to_bytes(2, 'big')
    response_status_in_bytes = response_status.to_bytes(2, 'big')
    return opcode_in_bytes + response_status_in_bytes