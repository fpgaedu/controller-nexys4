from math import ceil
from myhdl import intbv

class ControllerSpec():
    '''
    address-type message layout
     - width_opcode: 8
     - width_addr:  32
     - width_data:   8
    
    47            40 39             \   \    8 7             0
     |----opcode---| |----address---/   /----| |-----data----|
     |             | |              \   \    | |             |
    |-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-/   /-|-|-|-|-|-|-|-|-|-|-|
                                    \   \

    value-type message layout
     - width_opcode: 8
     - width_addr:  40

    47            40 39                           \   \      0
     |----opcode---| |----value-------------------/   /------|
     |             | |                            \   \      |
    |-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-/   /-|-|-|-|
                                                  \   \
    '''
    _WIDTH_BYTE = 8
    # opcode width = 4 => 2^4=16 opcodes possible
    _WIDTH_OPCODE = 4

    _OPCODE_CMD_READ = 0
    # - addr
    _OPCODE_CMD_WRITE = 1
    # - addr
    # - data
    _OPCODE_CMD_RESET = 2
    _OPCODE_CMD_STEP = 3
    _OPCODE_CMD_START = 4
    _OPCODE_CMD_PAUSE = 5
    _OPCODE_CMD_STATUS = 6

    _OPCODE_RES_READ_SUCCESS = 0
    # - addr
    # - data
    _OPCODE_RES_READ_ERROR_MODE = 1
    # - addr
    _OPCODE_RES_WRITE_SUCCESS = 2
    # - addr
    # - data
    _OPCODE_RES_WRITE_ERROR_MODE = 3
    # - addr
    # - data
    _OPCODE_RES_RESET_SUCCESS = 4
    _OPCODE_RES_STEP_SUCCESS = 5
    # - value (cycle count after step)
    _OPCODE_RES_STEP_ERROR_MODE = 6
    _OPCODE_RES_START_SUCCESS = 7
    # - value (cycle count before start)
    _OPCODE_RES_START_ERROR_MODE = 8
    _OPCODE_RES_PAUSE_SUCCESS = 9
    # - value (cycle count after pause)
    _OPCODE_RES_PAUSE_ERROR_MODE = 10
    _OPCODE_RES_STATUS = 11 
    # - value (mode + cycle count)

    _ADDR_TYPE_CMD_OPCODES = [_OPCODE_CMD_READ, _OPCODE_CMD_WRITE] 
    _ADDR_TYPE_RES_OPCODES = [_OPCODE_RES_READ_SUCCESS, 
            _OPCODE_RES_READ_ERROR_MODE, _OPCODE_RES_WRITE_SUCCESS, 
            _OPCODE_RES_WRITE_ERROR_MODE]

    def __init__(self, width_addr, width_data):

        if width_addr < 1:
            raise ValueError('address width must be at least 1')
        if width_data < 1:
            raise ValueError('data width must be at least 1')

        self._width_addr = width_addr
        self._width_data = width_data

    @property
    def width_opcode(self):
        return self._WIDTH_OPCODE

    @property
    def width_addr(self):
        return self._width_addr

    @property
    def width_data(self):
        return self._width_data

    @property
    def width_value(self):
        return self.width_addr + self.width_data

    @property
    def width_message(self):
        return self.width_opcode + self.width_value

    @property
    def width_message_bytes(self):
        return int(ceil(float(self.width_message) / 
            float(self._WIDTH_BYTE)))

    @property
    def index_opcode_high(self):
        return self.width_message - 1

    @property
    def index_opcode_low(self):
        return self.width_message - self.width_opcode

    @property
    def index_addr_high(self):
        return self.width_message - self.width_opcode - 1

    @property
    def index_addr_low(self):
        return self.width_message - self.width_opcode - self.width_addr

    @property
    def index_data_high(self):
        return self.width_data - 1

    @property
    def index_data_low(self):
        return 0

    @property
    def index_value_high(self):
        return self.width_value - 1

    @property
    def index_value_low(self):
        return 0

    #Command opcodes
    @property
    def opcode_cmd_read(self):
        return self._OPCODE_CMD_READ

    @property
    def opcode_cmd_write(self):
        return self._OPCODE_CMD_WRITE

    @property
    def opcode_cmd_reset(self):
        return self._OPCODE_CMD_RESET

    @property
    def opcode_cmd_step(self):
        return self._OPCODE_CMD_STEP

    @property
    def opcode_cmd_start(self):
        return self._OPCODE_CMD_START

    @property
    def opcode_cmd_pause(self):
        return self._OPCODE_CMD_PAUSE

    @property
    def opcode_cmd_status(self):
        return self._OPCODE_CMD_STATUS
    
    # Repsonse opcodes
    @property
    def opcode_res_read_success(self):
        return self._OPCODE_RES_READ_SUCCESS

    @property
    def opcode_res_read_error_mode(self):
        return self._OPCODE_RES_READ_ERROR_MODE

    @property
    def opcode_res_write_success(self):
        return self._OPCODE_RES_WRITE_SUCCESS

    @property
    def opcode_res_write_error_mode(self):
        return self._OPCODE_RES_WRITE_ERROR_MODE

    @property
    def opcode_res_reset_success(self):
        return self._OPCODE_RES_RESET_SUCCESS

    @property
    def opcode_res_step_success(self):
        return self._OPCODE_RES_STEP_SUCCESS

    @property
    def opcode_res_step_error_mode(self):
        return self._OPCODE_RES_STEP_ERROR_MODE

    @property
    def opcode_res_start_success(self):
        return self._OPCODE_RES_START_SUCCESS

    @property
    def opcode_res_start_error_mode(self):
        return self._OPCODE_RES_START_ERROR_MODE

    @property
    def opcode_res_pause_success(self):
        return self._OPCODE_RES_PAUSE_SUCCESS

    @property
    def opcode_res_pause_error_mode(self):
        return self._OPCODE_RES_PAUSE_ERROR_MODE

    @property
    def opcode_res_status(self):
        return self._OPCODE_RES_STATUS

    def is_addr_type_command(self, opcode):
        return (opcode in self._ADDR_TYPE_CMD_OPCODES)

    def is_value_type_command(self, opcode):
        return not self.is_addr_type_command(opcode)

    def is_addr_type_response(self, opcode):
        return (opcode in self._ADDR_TYPE_RES_OPCODES)

    def is_value_type_response(self, opcode):
        return not self.is_addr_type_response(opcode)

    def value_type_message(self, opcode, value):
        message = intbv(0)[self.width_message:0]
        message[self.index_opcode_high+1:self.index_opcode_low] = opcode
        message[self.index_value_high+1:self.index_value_low] = value

        return int(message)

    def addr_type_message(self, opcode, address, data):
        message = intbv(0)[self.width_message:0]
        message[self.index_opcode_high+1:self.index_opcode_low] = opcode
        message[self.index_addr_high+1:self.index_addr_low] = address
        message[self.index_data_high+1:self.index_data_low] = data

        return int(message)

    def parse_opcode(self, message):
        m = intbv(message)
        return int(m[self.index_opcode_high+1:self.index_opcode_low])

    def parse_addr(self, message):
        m = intbv(message)
        return int(m[self.index_addr_high+1:self.index_addr_low])

    def parse_data(self, message):
        m = intbv(message)
        return int(m[self.index_data_high+1:self.index_data_low])

    def parse_value(self, message):
        m = intbv(message)
        return int(m[self.index_value_high+1:self.index_value_low])

