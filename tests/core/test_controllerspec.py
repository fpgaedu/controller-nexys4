from unittest import TestCase
from fpgaedu import ControllerSpec

class ControllerSpecTestCase(TestCase):

    def setUp(self):
        pass

    def test_constructor(self):

        with self.assertRaises(ValueError):
            spec = ControllerSpec(0, 1)
        with self.assertRaises(ValueError):
            spec = ControllerSpec(1, 0)

    def test_width_and_index_attrs(self):
        width_data = 12 
        width_addr = 22
        width_opcode = 4
        width_value = 34
        width_message = 38
        width_message_bytes = 5

        spec = ControllerSpec(width_addr, width_data)

        self.assertEquals(spec.width_opcode, width_opcode,
                '_WIDTH_OPCODE constant has changed')
        self.assertEquals(spec.width_data, width_data)
        self.assertEquals(spec.width_addr, width_addr)
        self.assertEquals(spec.width_value,width_value)
        self.assertEquals(spec.width_message, width_message)
        self.assertEquals(spec.width_message_bytes, width_message_bytes)

        self.assertEquals(spec.index_opcode_high, 37)
        self.assertEquals(spec.index_opcode_low, 34)
        self.assertEquals(spec.index_addr_high, 33)
        self.assertEquals(spec.index_addr_low, 12)
        self.assertEquals(spec.index_data_high, 11)
        self.assertEquals(spec.index_data_low, 0)
        self.assertEquals(spec.index_value_high, 33)
        self.assertEquals(spec.index_value_low, 0)

    def test_cmd_opcodes_defined(self):
        spec = ControllerSpec(1,1)
        self.assertIsInstance(spec.opcode_cmd_read, int)
        self.assertIsInstance(spec.opcode_cmd_write, int)
        self.assertIsInstance(spec.opcode_cmd_reset, int)
        self.assertIsInstance(spec.opcode_cmd_step, int)
        self.assertIsInstance(spec.opcode_cmd_start, int)
        self.assertIsInstance(spec.opcode_cmd_pause, int)
        self.assertIsInstance(spec.opcode_cmd_status, int)

    def test_cmd_opcodes_unique(self):
        spec = ControllerSpec(1,1)
        cmd_opcodes = [spec.opcode_cmd_read, spec.opcode_cmd_write,
                spec.opcode_cmd_reset, spec.opcode_cmd_step, 
                spec.opcode_cmd_start, spec.opcode_cmd_pause,
                spec.opcode_cmd_status]
        self.assertEquals(len(set(cmd_opcodes)), len(cmd_opcodes))

    def test_res_opcodes_defined(self):
        spec = ControllerSpec(1,1)
        self.assertIsInstance(spec.opcode_res_read_success, int)
        self.assertIsInstance(spec.opcode_res_read_error_mode, int)
        self.assertIsInstance(spec.opcode_res_write_success, int)
        self.assertIsInstance(spec.opcode_res_write_error_mode, int)
        self.assertIsInstance(spec.opcode_res_reset_success, int)
        self.assertIsInstance(spec.opcode_res_step_success, int)
        self.assertIsInstance(spec.opcode_res_step_error_mode, int)
        self.assertIsInstance(spec.opcode_res_start_success, int)
        self.assertIsInstance(spec.opcode_res_start_error_mode, int)
        self.assertIsInstance(spec.opcode_res_pause_success, int)
        self.assertIsInstance(spec.opcode_res_pause_error_mode, int)
        self.assertIsInstance(spec.opcode_res_status, int)

    def test_res_opcodes_unique(self):
        spec = ControllerSpec(1,1)
        res_opcodes = [spec.opcode_res_read_success, 
                spec.opcode_res_read_error_mode, spec.opcode_res_write_success, 
                spec.opcode_res_write_error_mode, 
                spec.opcode_res_reset_success, 
                spec.opcode_res_step_success, spec.opcode_res_step_error_mode,
                spec.opcode_res_start_success, 
                spec.opcode_res_start_error_mode,
                spec.opcode_res_pause_success, 
                spec.opcode_res_pause_error_mode,
                spec.opcode_res_status]
        self.assertEquals(len(set(res_opcodes)), len(res_opcodes))

    def test_message_classification(self):
        spec = ControllerSpec(1,1)

        # Test one from within the set
        self.assertTrue(spec.is_addr_type_response(
            spec.opcode_res_read_success))
        self.assertFalse(spec.is_value_type_response(
            spec.opcode_res_read_success))

        # Test one from outside the set
        self.assertFalse(spec.is_addr_type_command(
            spec.opcode_cmd_step))
        self.assertTrue(spec.is_value_type_command(
            spec.opcode_cmd_step))

    def test_value_type_message(self):
        spec = ControllerSpec(8, 8)

        opcode = int('1010', 2)
        value = int('1100110011001100', 2)
        expected = int('10101100110011001100', 2)

        message = spec.value_type_message(opcode, value)
        self.assertEquals(message, expected)

        with self.assertRaises(ValueError):
            value = int('11111111111111111', 2)
            message = spec.value_type_message(opcode, value)

    def test_addr_type_message(self):
        spec = ControllerSpec(8, 8)

        opcode = int('1010', 2)
        address = int('10111111', 2)
        data = int('11111111', 2)
        expected = int('10101011111111111111', 2)

        message = spec.addr_type_message(opcode, address, data)
        self.assertEquals(message, expected)

        with self.assertRaises(ValueError):
            data = int('111111111', 2)
            message = spec.addr_type_message(opcode, address, data)

    def test_parse(self):
        spec = ControllerSpec(8, 8)
        message = int('10101100110011110000', 2)

        parsed_opcode = spec.parse_opcode(message)
        self.assertEquals(parsed_opcode, int('1010', 2))

        parsed_addr = spec.parse_addr(message)
        self.assertEquals(parsed_addr, int('11001100', 2))
        
        parsed_data = spec.parse_data(message)
        self.assertEquals(parsed_data, int('11110000', 2))
        
        parsed_value = spec.parse_value(message)
        self.assertEquals(parsed_value, int('1100110011110000', 2))
