from myhdl import (Signal, ResetSignal, intbv, always, instance, Simulation, 
        StopSimulation)
from unittest import TestCase

from fpgaedu import ControllerSpec
from fpgaedu.hdl import ClockGen, Controller

class ControllerTestCase(TestCase):

    HALF_PERIOD = 5
    WIDTH_ADDR = 32
    WIDTH_DATA = 8
    MEM = { 234: 7 }

    def setUp(self):
        self.spec = ControllerSpec(width_addr=self.WIDTH_ADDR, 
                width_data=self.WIDTH_DATA)
        # Input signals
        self.clk = Signal(False)
        self.reset = ResetSignal(True, active=False, async=False)
        self.rx_fifo_data_read = Signal(intbv(0)[self.spec.width_message:0])
        self.rx_fifo_empty = Signal(True)
        self.tx_fifo_full = Signal(False)
        self.exp_data_read = Signal(intbv(0)[self.spec.width_data:0])
        # Output signals
        self.rx_fifo_dequeue = Signal(False)
        self.tx_fifo_data_write = Signal(intbv(0)[self.spec.width_message:0])
        self.tx_fifo_enqueue = Signal(False)
        self.exp_addr = Signal(intbv(0)[self.spec.width_addr:0])
        self.exp_data_write = Signal(intbv(0)[self.spec.width_data:0])
        self.exp_wen = Signal(False)
        self.exp_reset = ResetSignal(True, active=False, async=False)
        self.exp_clk_en = Signal(False)

        self.clockgen = ClockGen(clk=self.clk, half_period=self.HALF_PERIOD)
        self.controller = Controller(spec=self.spec, clk=self.clk, 
                reset=self.reset, rx_fifo_data_read=self.rx_fifo_data_read, 
                rx_fifo_dequeue=self.rx_fifo_dequeue,
                rx_fifo_empty=self.rx_fifo_empty,
                tx_fifo_data_write =self.tx_fifo_data_write,
                tx_fifo_enqueue=self.tx_fifo_enqueue,
                tx_fifo_full=self.tx_fifo_full, exp_addr=self.exp_addr, 
                exp_data_write=self.exp_data_write, 
                exp_data_read=self.exp_data_read,
                exp_wen=self.exp_wen, exp_reset=self.exp_reset,
                exp_clk_en=self.exp_clk_en)

        @always(self.clk.posedge)
        def _mock_experiment():
            if self.exp_wen: 
                self.MEM[self.exp_addr] = self.exp_din
            try:
                self.exp_dout.next = self.MEM[self.exp_addr]
            except KeyError:
                self.exp_out.next = 0

        self.mock_experiment = _mock_experiment

    def simulate(self, test_logic, duration=None):
        sim = Simulation(self.clockgen, self.controller, *test_logic)
        sim.run(duration, quiet=False)

    def stop_simulation(self):
        raise StopSimulation()

    def assert_value_type_response(self, opcode_expected, value_expected):
        opcode_actual = self.spec.parse_opcode(self.tx_fifo_din)
        value_actual = self.spec.parse_value(self.tx_fifo_din)
    
        self.assertEquals(opcode_actual, opcode_expected)
        self.assertEquals(value_actual, value_expected)

    def assert_addr_type_response(self, opcode_expected, address_expected, 
            data_expected):
        opcode_actual = self.spec.parse_opcode(self.tx_fifo_din)
        addr_actual = self.spec.parse_addr(self.tx_fifo_din)
        data_actual = self.spec.parse_data(self.tx_fifo_din)
        
        self.assertEquals(opcode_actual, opcode_expected)
        self.assertEquals(addr_actual, addr_expected)
        self.assertEquals(data_actual, data_expected)

    def test_read(self):

        opcode = self.spec.opcode_cmd_read
        addr = 234
        cmd = self.spec.addr_type_message(opcode, addr, 0)
        expected_res = self.spec.addr_type_message(
                self.spec.opcode_res_read_success, addr, 7)

        @instance
        def test():
            self.reset.next = False
            yield self.clk.negedge
            self.reset.next = True
            yield self.clk.negedge

            self.rx_fifo_data_read.next = cmd
            self.rx_fifo_empty.next = False

            yield self.clk.negedge


            self.stop_simulation()

        self.simulate([test])


