from myhdl import (Signal, ResetSignal, intbv, always, instance, Simulation, 
        StopSimulation, delay, always_comb)
from unittest import TestCase

from fpgaedu import ControllerSpec
from fpgaedu.hdl import ClockGen, Controller

def MockExperimentSetup(clk, reset, exp_addr, exp_din, exp_dout, exp_wen, 
        exp_reset, exp_clk_en, initial={}):

    memory = dict(initial)

    @always(clk.posedge)
    def logic():
        if exp_wen: 
            memory[int(exp_addr.val)] = exp_din.val

        try:
            exp_dout.next = memory[int(exp_addr.val)]
        except KeyError:
            exp_dout.next = 2
    
    return logic

class ControllerTestCase(TestCase):

    HALF_PERIOD = 5
    WIDTH_ADDR = 32
    WIDTH_DATA = 8
    MEM_INIT = { 3:4, 4:5, 5:6 }
    EXP_RESET_ACTIVE=False

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
        self.exp_reset = ResetSignal(not self.EXP_RESET_ACTIVE, 
                active=self.EXP_RESET_ACTIVE, async=False)
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
                exp_clk_en=self.exp_clk_en, 
                exp_reset_active=self.EXP_RESET_ACTIVE)

        self.mock_experiment = MockExperimentSetup(self.clk, self.reset, 
                self.exp_addr, self.exp_data_write, self.exp_data_read, self.exp_wen, 
                self.exp_reset, self.exp_clk_en, self.MEM_INIT)

    def simulate(self, test_logic, duration=None):
        sim = Simulation(self.clockgen, self.controller, self.mock_experiment, *test_logic)
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

    def test_reset(self):
        
        @instance
        def test():
            self.reset.next = self.reset.active
            yield self.clk.negedge
            self.assertFalse(self.rx_fifo_dequeue)
            self.assertFalse(self.tx_fifo_enqueue)
            self.assertEquals(self.exp_reset, self.EXP_RESET_ACTIVE)
            self.assertFalse(self.exp_wen)
            self.assertFalse(self.exp_clk_en)
            
            yield self.clk.negedge
            self.assertFalse(self.exp_clk_en)
            
            yield self.clk.negedge
            self.assertFalse(self.exp_clk_en)
            

            self.stop_simulation()

        self.simulate([test])

    def test_cmd_read(self):
        opcode = self.spec.opcode_cmd_read
        cmd1 = self.spec.addr_type_message(opcode, 3, 0)
        cmd2 = self.spec.addr_type_message(opcode, 4, 0)
        expected1 = self.spec.addr_type_message(
                self.spec.opcode_res_read_success, 3, 4)
        expected2 = self.spec.addr_type_message(
                self.spec.opcode_res_read_success, 4, 5)

        @instance
        def test():
            self.reset.next = self.reset.active
            yield self.clk.negedge
            self.reset.next = not self.reset.active
            yield self.clk.negedge
            self.assertFalse(self.tx_fifo_enqueue)

            self.rx_fifo_data_read.next = cmd1
            self.rx_fifo_empty.next = False
            self.tx_fifo_full.next = False
            yield delay(1)
            self.assertTrue(self.rx_fifo_dequeue)
            yield self.clk.negedge
            self.assertEquals(self.tx_fifo_data_write, expected1)
            self.assertTrue(self.tx_fifo_enqueue)

            self.rx_fifo_data_read.next = cmd2
            self.rx_fifo_empty.next = False
            yield delay(1)
            self.assertTrue(self.rx_fifo_dequeue)
            yield self.clk.negedge
            self.assertEquals(self.tx_fifo_data_write, expected2)
            self.assertTrue(self.tx_fifo_enqueue)

            self.rx_fifo_empty.next = True
            yield self.clk.negedge
            self.assertFalse(self.tx_fifo_enqueue)

            self.stop_simulation()

        self.simulate([test])

    def test_cmd_write(self):
        @instance
        def test():
            self.reset.next = self.reset.active
            yield self.clk.negedge

            self.reset.next = not self.reset.active
            self.rx_fifo_empty.next = False
            self.rx_fifo_data_read.next = self.spec.addr_type_message(
                    self.spec.opcode_cmd_write, 88, 9)
            self.tx_fifo_full.next = False
            yield delay(1)
            self.assertTrue(self.rx_fifo_dequeue)
            self.assertTrue(self.exp_wen)
            self.assertEquals(self.exp_addr, 88)

            yield self.clk.negedge
            self.assertEquals(self.exp_data_read, 9)
            self.assertTrue(self.tx_fifo_enqueue)
            self.assertEquals(self.exp_addr, 88)

            self.rx_fifo_empty.next = True
            yield delay(1)
            self.assertFalse(self.rx_fifo_dequeue)
            self.assertFalse(self.exp_wen)

            yield self.clk.negedge
            self.assertFalse(self.tx_fifo_enqueue)

            self.stop_simulation()
        
        self.simulate([test])

    def test_cmd_reset(self):
        @instance
        def test():
            self.reset.next = self.reset.active
            yield self.clk.negedge

            self.reset.next = not self.reset.active
            yield self.clk.negedge
            self.assertEquals(self.exp_reset, not self.EXP_RESET_ACTIVE)

            self.rx_fifo_data_read.next = self.spec.value_type_message(
                    self.spec.opcode_cmd_reset, 0)
            self.rx_fifo_empty.next = False
            self.tx_fifo_full.next = False
            yield delay(1) 
            self.assertEquals(self.exp_reset, self.EXP_RESET_ACTIVE)

            yield self.clk.negedge
            self.assertEquals(self.tx_fifo_data_write,
                    self.spec.value_type_message(
                        self.spec.opcode_res_reset_success, 0))
            
            self.stop_simulation()

        self.simulate([test])

    def test_cmd_step(self):
        @instance
        def test():
            self.reset.next = self.reset.active
            yield self.clk.negedge

            self.reset.next = not self.reset.active
            self.rx_fifo_empty.next = True
            self.tx_fifo_full.next = False
            yield self.clk.posedge
            yield delay(1)
            self.assertFalse(self.exp_clk_en)

            self.rx_fifo_data_read.next = self.spec.value_type_message(
                    self.spec.opcode_cmd_step, 0)
            self.rx_fifo_empty.next = False
            yield delay(1)
            self.assertFalse(self.exp_clk_en)
            yield self.clk.negedge
            yield delay(1)
            self.assertTrue(self.exp_clk_en)
            self.assertFalse(self.tx_fifo_enqueue)

            yield self.clk.posedge
            yield delay(1)
            self.assertTrue(self.exp_clk_en)
            self.assertTrue(self.tx_fifo_enqueue)

            self.rx_fifo_empty.next = True
            yield self.clk.negedge
            yield delay(1)
            self.assertFalse(self.exp_clk_en)

            self.stop_simulation()

        self.simulate([test])

    def test_cmd_start_pause(self):
        @instance
        def test():
            self.reset.next = self.reset.active
            yield self.clk.negedge

            self.reset.next = not self.reset.active
            self.rx_fifo_empty.next = True
            self.tx_fifo_full.next = False

            self.stop_simulation()

        self.simulate([test])


