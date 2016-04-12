from myhdl import (Signal, intbv, always, instance, Simulation, 
        StopSimulation, delay)
from unittest import TestCase

from fpgaedu import ControllerSpec
from fpgaedu.hdl._controller_response_compose import ControllerResponseCompose


class ControllerResponseComposeTestCase(TestCase):

    WIDTH_ADDR = 32
    WIDTH_DATA = 8

    def setUp(self):
        self.spec = ControllerSpec(self.WIDTH_ADDR, self.WIDTH_DATA)
        #input signals
        self.opcode_res = Signal(intbv(0)[self.spec.width_opcode:0])
        self.addr = Signal(intbv(0)[self.spec.width_addr:0])
        self.data = Signal(intbv(0)[self.spec.width_data:0])
        self.nop = Signal(False)
        self.tx_fifo_full = Signal(False)
        self.cycle_count = Signal(intbv(0)[self.spec.width_value:0])
        # Output signals
        self.tx_fifo_enqueue = Signal(False)
        self.tx_fifo_din = Signal(intbv(0)[self.spec.width_message:0])

        self.response_compose = ControllerResponseCompose(spec=self.spec,
                opcode_res=self.opcode_res, addr=self.addr, data=self.data,
                nop=self.nop, cycle_count=self.cycle_count,
                tx_fifo_full=self.tx_fifo_full, 
                tx_fifo_enqueue=self.tx_fifo_enqueue,
                tx_fifo_din=self.tx_fifo_din)

    def simulate(self, test_logic, duration=None):
        sim = Simulation(self.response_compose, test_logic)
        sim.run(duration, quiet=False)

    def stop_simulation(self):
        raise StopSimulation()

    def assert_value_type_response(self, opcode_expected, value_expected):
        opcode_actual = self.spec.parse_opcode(self.tx_fifo_din.val)
        value_actual = self.spec.parse_value(self.tx_fifo_din.val)
    
        self.assertEquals(opcode_actual, opcode_expected)
        self.assertEquals(value_actual, value_expected)

    def assert_addr_type_response(self, opcode_expected, addr_expected, 
            data_expected):
        opcode_actual = self.spec.parse_opcode(self.tx_fifo_din.val)
        addr_actual = self.spec.parse_addr(self.tx_fifo_din.val)
        data_actual = self.spec.parse_data(self.tx_fifo_din.val)
        
        self.assertEquals(opcode_actual, opcode_expected)
        self.assertEquals(addr_actual, addr_expected)
        self.assertEquals(data_actual, data_expected)

    def test_tx_fifo_enqueue(self):

        @instance
        def test():
            yield delay(1)
            
            self.nop.next = True
            self.tx_fifo_full.next = True
            yield delay(1)
            self.assertFalse(self.tx_fifo_enqueue)

            self.nop.next = True
            self.tx_fifo_full.next = False
            yield delay(1)
            self.assertFalse(self.tx_fifo_enqueue)

            self.nop.next = False
            self.tx_fifo_full.next = True
            yield delay(1)
            self.assertFalse(self.tx_fifo_enqueue)

            self.nop.next = False
            self.tx_fifo_full.next = False
            yield delay(1)
            self.assertTrue(self.tx_fifo_enqueue)

            self.stop_simulation()

        self.simulate(test)

    def test_tx_fifo_din(self):

        @instance
        def test():
            self.nop.next = False
            self.tx_fifo_full.next = False

            # read success
            self.addr.next = 23
            self.data.next = 3
            self.opcode_res.next = self.spec.opcode_res_read_success
            yield delay(10)
            self.assert_addr_type_response(self.spec.opcode_res_read_success, 
                    23, 3)

            # read error
            self.opcode_res.next = self.spec.opcode_res_read_error_mode
            yield delay(1)
            self.assert_addr_type_response(
                    self.spec.opcode_res_read_error_mode, 23, 0)

            # write success
            self.addr.next = 26
            self.data.next = 6
            self.opcode_res.next = self.spec.opcode_res_write_success
            yield delay(10)
            self.assert_addr_type_response(self.spec.opcode_res_write_success, 
                    26, 6)

            # read error
            self.opcode_res.next = self.spec.opcode_res_write_error_mode
            yield delay(1)
            self.assert_addr_type_response(
                    self.spec.opcode_res_write_error_mode, 26, 0)

            # reset success
            self.opcode_res.next = self.spec.opcode_res_reset_success 
            yield delay(1)
            self.assert_value_type_response(
                    self.spec.opcode_res_reset_success, 0)

            # Step success
            self.cycle_count.next = 34523
            self.opcode_res.next = self.spec.opcode_res_step_success
            yield delay(1)
            self.assert_value_type_response(
                    self.spec.opcode_res_step_success, 34524)

            # Step error
            self.opcode_res.next = self.spec.opcode_res_step_error_mode
            yield delay(1)
            self.assert_value_type_response(
                    self.spec.opcode_res_step_error_mode, 0)

            # Start success
            self.cycle_count.next = 3523
            self.opcode_res.next = self.spec.opcode_res_start_success
            yield delay(1)
            self.assert_value_type_response(
                    self.spec.opcode_res_start_success, 3523)

            # Start error
            self.opcode_res.next = self.spec.opcode_res_start_error_mode
            yield delay(1)
            self.assert_value_type_response(
                    self.spec.opcode_res_start_error_mode, 0)

            # Pause success
            self.cycle_count.next = 823
            self.opcode_res.next = self.spec.opcode_res_pause_success
            yield delay(1)
            self.assert_value_type_response(
                    self.spec.opcode_res_pause_success, 823)

            # Pause error
            self.opcode_res.next = self.spec.opcode_res_pause_error_mode
            yield delay(1)
            self.assert_value_type_response(
                    self.spec.opcode_res_pause_error_mode, 0)

            # Status
            self.cycle_count.next = 11823
            self.opcode_res.next = self.spec.opcode_res_status
            yield delay(1)
            self.assert_value_type_response(
                    self.spec.opcode_res_status, 11823)
            
            self.stop_simulation()

        self.simulate(test)



