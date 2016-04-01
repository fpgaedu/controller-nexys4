from myhdl import (Signal, ResetSignal, intbv, Simulation, StopSimulation,
        instance, delay)
from math import ceil
import unittest
from unittest import TestCase
from random import randint

from fpgaedu.hdl import ClockGen, UartTx

class UartTxTestCase(TestCase):

    DATA_BITS = 8
    STOP_BITS = 1
    HALF_PERIOD = 10

    HIGH = True
    LOW = False
    START = LOW
    STOP = HIGH
    IDLE = HIGH

    def setUp(self):
        
        self.clk = Signal(False)
        self.reset = ResetSignal(True,active=False,async=True)
        self.tx = Signal(False)
        self.tx_start = Signal(False)
        self.tx_busy = Signal(False)
        self.tx_data = Signal(intbv(0)[self.DATA_BITS:0])
        self.baud_tick = Signal(False)

        self.clockgen = ClockGen(self.clk, self.HALF_PERIOD)

        self.uart_tx = UartTx(self.clk, self.reset, self.tx, self.tx_data, 
                self.tx_start, self.tx_busy, self.baud_tick)

    def tearDown(self):
        del self.clk
        del self.reset
        del self.tx
        del self.tx_start
        del self.tx_busy
        del self.tx_data
        del self.baud_tick
        del self.clockgen
        del self.uart_tx

    def simulate(self, test_logic, duration=None):
        sim = Simulation(self.clockgen, self.uart_tx, test_logic)
        sim.run(duration, quiet=False)

    def stop_simulation(self):
        raise StopSimulation()


    def test_initial_state(self):

        @instance
        def test():
            yield delay(1)
            self.assertEquals(self.tx, True)
            self.assertEquals(self.tx_busy, False)
            self.stop_simulation()

        self.simulate(test)

    def test_idle_behaviour(self):

        @instance
        def test():
            yield self.clk.negedge
            self.assertEquals(self.tx, bool(self.IDLE))
            yield self.clk.negedge
            self.assertEquals(self.tx, bool(self.IDLE))

            self.stop_simulation()

        self.simulate(test)

    def test_transmit(self):

        @instance
        def test():

            yield self.clk.negedge

            #test_data = ['01001010']
            test_data = ['01001010', '11001111', '11110111']
            
            for test_data_str in test_data:
                print(test_data_str)
                #check that uart is ready
                self.assertFalse(self.tx_busy)
                self.assertEquals(self.tx, self.IDLE)

                self.tx_data.next = int(test_data_str, 2)
                self.tx_start.next = True
                yield self.clk.negedge

                self.assertTrue(self.tx_busy)
                self.assertEquals(self.tx, self.IDLE)

                yield self.clk.negedge
                self.tx_start.next = False

                self.assertEquals(self.tx, self.IDLE)
                
                self.baud_tick.next = True
                yield self.clk.negedge
                self.baud_tick.next = False
                self.assertEquals(self.tx, self.START)

                # test that the tx signal remains stable over a random
                # number of cycles when baud_tick is low
                for _ in range(randint(20,100)):
                    yield self.clk.negedge
                    self.assertEquals(self.tx, self.START)

                #Test data transmission 
                for test_data_chr in test_data_str[::-1]:
                    self.baud_tick.next = True
                    yield self.clk.negedge
                    self.baud_tick.next = False

                    def strtolvl(s):
                        if s == '0':
                            return self.LOW
                        elif s == '1':
                            return self.HIGH

                    self.assertEquals(self.tx, strtolvl(test_data_chr))

                    # test that the tx signal remains stable over a random
                    # number of cycles when baud_tick is low
                    for _ in range(randint(20,100)):
                        yield self.clk.negedge
                        self.assertEquals(self.tx, strtolvl(test_data_chr))

                self.baud_tick.next = True
                yield self.clk.negedge
                self.baud_tick.next = False
                self.assertEquals(self.tx, self.STOP)

                # test that the tx signal remains stable over a random
                # number of cycles when baud_tick is low
                for _ in range(randint(20,100)):
                    yield self.clk.negedge
                    self.assertEquals(self.tx, self.STOP)
                    self.assertTrue(self.tx_busy)

                self.baud_tick.next = True
                yield self.clk.negedge

                self.assertEquals(self.tx, self.IDLE)

                self.baud_tick.next = False
                yield self.clk.negedge
                self.assertFalse(self.tx_busy)
                self.assertEquals(self.tx, self.IDLE)

            self.stop_simulation()

        self.simulate(test)

