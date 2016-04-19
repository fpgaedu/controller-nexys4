from myhdl import (Signal, intbv, ResetSignal, instance, Simulation, 
        StopSimulation, delay)
from unittest import TestCase
from fpgaedu import ControllerSpec
from fpgaedu.hdl import ClockGen
from fpgaedu.hdl.nexys4 import BoardComponentTx

class BoardComponentTxTestCase(TestCase):

    HALF_PERIOD = 5
    LVL_HIGH = True
    LVL_LOW = False
    LVL_START = LVL_LOW
    LVL_STOP = LVL_HIGH
    LVL_IDLE = LVL_HIGH

    def setUp(self):
        self.spec = ControllerSpec(width_addr=32, width_data=8)
        # Input signals
        self.clk = Signal(False)
        self.reset = ResetSignal(True, active=False, async=False)
        self.tx_next = Signal(False)
        self.tx_msg = Signal(intbv(0)[self.spec.width_message:0])
        self.uart_tx_baud_tick = Signal(False)
        # Output signals
        self.tx_ready = Signal(False)
        self.tx = Signal(False)

        self.clockgen = ClockGen(clk=self.clk, half_period=self.HALF_PERIOD)
        self.component_tx = BoardComponentTx(spec=self.spec, clk=self.clk,
                reset=self.reset, tx=self.tx, tx_msg=self.tx_msg, 
                tx_ready=self.tx_ready, tx_next=self.tx_next, 
                uart_tx_baud_tick=self.uart_tx_baud_tick)

    def simulate(self, test_logic, duration=None):
        sim = Simulation(self.clockgen, self.component_tx, *test_logic)
        sim.run(duration, quiet=False)

    def stop_simulation(self):
        raise StopSimulation()


    def test_tx(self):

        @instance
        def test():
            yield self.clk.negedge
            self.reset.next = self.reset.active
            yield self.clk.negedge

            self.reset.next = not self.reset.active
            yield self.clk.negedge
            self.assertTrue(self.tx_ready)
            
            for i in range(100):
                self.uart_tx_baud_tick.next = True
                yield self.clk.negedge
                self.uart_tx_baud_tick.next = False
                self.assertEquals(self.tx, self.LVL_IDLE)

            self.tx_msg.next = 0xFFFFFFFF
            self.tx_next.next = True
            yield self.clk.negedge
            self.assertFalse(self.tx_ready)
            
            self.tx_next.next = False

            self.uart_tx_baud_tick.next = True
            yield self.tx.negedge
            for i in range(220):
                yield self.clk.negedge

            self.stop_simulation()

        self.simulate([test])


