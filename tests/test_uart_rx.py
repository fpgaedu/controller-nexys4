from myhdl import (Signal, ResetSignal, intbv, Simulation, StopSimulation,
        instance, delay)
from unittest import TestCase
from fpgaedu.hdl import ClockGen, UartRx

class UartRxTestCase(TestCase):

    DATA_BITS = 8
    STOP_BITS = 1
    HALF_PERIOD = 10

    HIGH = True
    LOW = False
    START = LOW
    STOP = HIGH
    IDLE = HIGH

    def setUp(self):
        self.clk = Signal(True)
        self.reset = ResetSignal(True, active=False, async=False)
        self.rx = Signal(False)
        self.rx_data = Signal(intbv(0)[self.DATA_BITS:0])
        self.rx_finish = Signal(False)
        self.rx_busy = Signal(False)
        self.rx_baud_tick = Signal(False)

        self.clockgen = ClockGen(self.clk, self.HALF_PERIOD)
        self.uart_rx = UartRx(self.clk, self.reset, self.rx, self.rx_data, 
                self.rx_finish, self.rx_busy, self.rx_baud_tick)
        
    def simulate(self, test_logic, duration=None):
        sim = Simulation(self.clockgen, self.uart_rx, test_logic)
        sim.run(duration, quiet=False)

    def stop_simulation(self):
        raise StopSimulation()

    def test_rx_receive(self):

        @instance
        def test():
            yield self.clk.negedge
            self.assertFalse(self.rx_busy)
            self.assertFalse(self.rx_finish)

            self.stop_simulation()

        self.simulate(test)

