from myhdl import (Signal, ResetSignal, intbv, Simulation, StopSimulation,
        instance, delay, now, traceSignals)
from math import ceil
import unittest
from unittest import TestCase
from random import randint

from fpgaedu.hdl import BaudGen, ClockGen


class BaudGenTestCase(TestCase):

    BAUDRATE = 230401  
    CLK_FREQ = 100000000
    RX_DIV = 16
    CLK_HALF_PERIOD = 1

    def setUp(self):
        self.clk = Signal(False)
        self.reset = ResetSignal(True, active=False, async=False)
        self.rx_tick = Signal(False)
        self.tx_tick = Signal(False)

        self.clockgen = ClockGen(self.clk, self.CLK_HALF_PERIOD)
        self.baudgen = BaudGen(self.clk, self.reset, self.rx_tick, 
                self.tx_tick, clk_freq=self.CLK_FREQ, baudrate=self.BAUDRATE,
                rx_div=self.RX_DIV)

    def simulate(self, test_logic, duration=None):

        sim = Simulation(self.clockgen, self.baudgen, test_logic)
        sim.run(duration, quiet=False)

    def stop_simulation(self):
        raise StopSimulation()

    def test_tx_tick(self):
        '''
        Test that a subsequent tx_tick is properly delayed
        '''

        delta_tick = int(ceil(self.CLK_FREQ / self.BAUDRATE))
        delta_tick = delta_tick * 2

        @instance
        def test():

            self.reset.next = False
            yield self.clk.negedge
            self.reset.next = True
            yield self.tx_tick.posedge
            prev_now = curr_now = now()

            # Test 5 subsequent cycles
            for j in range(5):
                yield self.tx_tick.posedge
                curr_now = now()
                delta_now = curr_now - prev_now
                delta = abs(delta_now - delta_tick)
                self.assertTrue(delta == 0, 
                        'delta = %s, should max 0 (0 clock cycles)' % delta)
                prev_now = curr_now

            self.stop_simulation()
        self.simulate(test)

    def test_rx_tick(self):
        '''
        test that a subsequent rx_tick has a maximum deviation of 1 clock
        cycle, due to float rounding
        '''

        delta_tick = self.CLK_FREQ / (self.BAUDRATE * self.RX_DIV)
        delta_tick = delta_tick * 2

        @instance
        def test():
            self.reset.next = False
            yield self.clk.negedge
            self.reset.next = True
            yield self.rx_tick.posedge
            prev_now = curr_now = now()
            # run 3 tx cycles = 3 * rx_div
            for i in range(3 * self.RX_DIV):
                yield self.rx_tick.posedge
                curr_now = now()
                delta_now = curr_now - prev_now
                delta = abs(delta_now - delta_tick)
                self.assertTrue(delta <= 2, 
                        'delta = %s, should max 2 (1 clock cycle)' % delta)
                prev_now = curr_now

            self.stop_simulation()
            
        self.simulate(test)


    def test_rx_tx_sync(self):
        '''
        Check that the tx_tick and rx_tick signals are in sync when tx_tick is 
        high. 
        '''

        tx_div = int(ceil(self.CLK_FREQ / self.BAUDRATE))

        @instance
        def test():
            for j in range(100):
                yield self.tx_tick.posedge
                self.assertTrue(self.tx_tick)
                self.assertEquals(self.rx_tick, self.tx_tick)
            
            self.stop_simulation()
            
        self.simulate(test)

if __name__ == '__main__':
    unittest.main()

