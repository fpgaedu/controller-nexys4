from myhdl import (Signal, ResetSignal, intbv, Simulation, StopSimulation,
        instance, delay, now, traceSignals)
from math import ceil
import unittest
from unittest import TestCase
from random import randint

from fpgaedu.hdl import Fifo, ClockGen


class FifoTestCase(TestCase):
    
    CLK_HALF_PERIOD = 5
    DATA_WIDTH = 32
    DEPTH = 2

    def setUp(self):
        self.clk = Signal(False)
        self.reset = ResetSignal(True, active=False, async=False)
        self.din = Signal(intbv(0)[self.DATA_WIDTH:0])
        self.enqueue = Signal(False)
        self.dout = Signal(intbv(0)[self.DATA_WIDTH:0])
        self.dequeue = Signal(False)
        self.empty = Signal(False)
        self.full = Signal(False)

        self.clockgen = ClockGen(self.clk, self.CLK_HALF_PERIOD)
        self.fifo = Fifo(self.clk, self.reset, self.din, self.enqueue, 
                self.dout, self.dequeue, self.empty, self.full, 
                data_width=self.DATA_WIDTH, depth=self.DEPTH)

    def simulate(self, test_logic, duration=None):

        sim = Simulation(self.clockgen, self.fifo, test_logic)
        sim.run(duration, quiet=False)

    def stop_simulation(self):
        raise StopSimulation()


    def test_fifo(self):

        @instance
        def test():
            self.reset.next = False
            yield self.clk.negedge

            self.reset.next = True
            yield self.clk.negedge
            self.assertEquals(self.dout, 0)
            self.assertTrue(self.empty)
            self.assertFalse(self.full)

            self.din.next = 34
            self.enqueue.next = True
            yield self.clk.negedge
            self.assertEquals(self.dout, 34)
            self.assertFalse(self.empty)
            self.assertFalse(self.full)

            self.enqueue.next = False
            for i in range(40):
                yield self.clk.negedge

            self.din.next = 23
            self.enqueue.next = True
            yield self.clk.negedge
            self.assertEquals(self.dout, 34)
            self.assertFalse(self.empty)
            self.assertTrue(self.full)

            self.enqueue.next = False
            self.assertEquals(self.dout, 34)
            yield self.clk.negedge

            self.dequeue.next = True
            yield self.clk.negedge
            self.dequeue.next = False
            self.assertEquals(self.dout, 23)
            self.assertFalse(self.empty)
            self.assertFalse(self.full)

            self.dequeue.next = True
            yield self.clk.negedge
            self.assertEquals(self.dout, 0)
            self.assertTrue(self.empty)
            self.assertFalse(self.full)

            self.dequeue.next = False
            yield self.clk.negedge
            self.assertEquals(self.dout, 0)
            self.assertTrue(self.empty)
            self.assertFalse(self.full)

            self.stop_simulation()
            
        self.simulate(test)

