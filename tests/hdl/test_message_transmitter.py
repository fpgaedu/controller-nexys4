from myhdl import (Signal, ResetSignal, intbv, always, instance, Simulation, 
        StopSimulation, delay, always_comb)
from unittest import TestCase

from fpgaedu import ControllerSpec
from fpgaedu.hdl import ClockGen, MessageTransmitter

class MessageTransmitterTestCase(TestCase):

    HALF_PERIOD = 5
    WIDTH_ADDR = 32
    WIDTH_DATA = 8

    def setUp(self):
        
        self.spec = ControllerSpec(self.WIDTH_ADDR, self.WIDTH_DATA)

        # Input signals
        self.clk = Signal(False)
        self.reset = ResetSignal(True, active=False, async=False)
        self.message = Signal(intbv(0)[self.spec.width_message:0])
        self.tx_fifo_full = Signal(False)
        self.transmit_next = Signal(False)
        # Output signals
        self.tx_fifo_data_write = Signal(intbv(0)[8:0])
        self.tx_fifo_enqueue = Signal(False)
        self.ready = Signal(False)

        self.clockgen = ClockGen(self.clk, self.HALF_PERIOD)
        self.transmitter = MessageTransmitter(spec=self.spec, clk=self.clk,
                reset=self.reset, tx_fifo_data_write=self.tx_fifo_data_write,
                tx_fifo_full=self.tx_fifo_full, 
                tx_fifo_enqueue=self.tx_fifo_enqueue, message=self.message,
                ready=self.ready, transmit_next=self.transmit_next)
 
    def simulate(self, test_logic, duration=None):
        sim = Simulation(self.clockgen, self.transmitter, *test_logic)
        sim.run(duration, quiet=False)

    def stop_simulation(self):
        raise StopSimulation()

    def test_transmit(self):

        @instance
        def test():
            yield delay(10)

            self.reset.next = self.reset.active
            yield self.clk.negedge

            self.reset.next = not self.reset.active
            yield self.clk.negedge
            self.assertTrue(self.ready)
            self.assertFalse(self.tx_fifo_enqueue)

            self.message.next = 0xF221244557D
            self.tx_fifo_full.next = False
            self.transmit_next.next = True
            yield self.clk.negedge
            self.assertFalse(self.ready)
            self.assertTrue(self.tx_fifo_enqueue)
            self.assertEquals(self.tx_fifo_data_write, self.spec.chr_start)

            yield self.clk.negedge
            self.assertFalse(self.ready)
            self.assertTrue(self.tx_fifo_enqueue)
            self.assertEquals(self.tx_fifo_data_write, 0x0F)

            yield self.clk.negedge
            self.assertFalse(self.ready)
            self.assertTrue(self.tx_fifo_enqueue)
            self.assertEquals(self.tx_fifo_data_write, 0x22)

            yield self.clk.negedge
            self.assertFalse(self.ready)
            self.assertTrue(self.tx_fifo_enqueue)
            self.assertEquals(self.tx_fifo_data_write, self.spec.chr_esc)

            self.tx_fifo_full.next = True
            yield self.clk.negedge
            yield self.clk.negedge
            yield self.clk.negedge
            yield self.clk.negedge
            yield self.clk.negedge
            self.assertFalse(self.ready)
            self.assertFalse(self.tx_fifo_enqueue)
            self.assertEquals(self.tx_fifo_data_write, self.spec.chr_esc)

            self.tx_fifo_full.next = False
            yield self.clk.negedge
            self.assertFalse(self.ready)
            self.assertTrue(self.tx_fifo_enqueue)
            self.assertEquals(self.tx_fifo_data_write, 0x12)

            yield self.clk.negedge
            self.assertFalse(self.ready)
            self.assertTrue(self.tx_fifo_enqueue)
            self.assertEquals(self.tx_fifo_data_write, 0x44)

            yield self.clk.negedge
            self.assertFalse(self.ready)
            self.assertTrue(self.tx_fifo_enqueue)
            self.assertEquals(self.tx_fifo_data_write, 0x55)

            yield self.clk.negedge
            self.assertFalse(self.ready)
            self.assertTrue(self.tx_fifo_enqueue)
            self.assertEquals(self.tx_fifo_data_write, 0x7D)

            yield self.clk.negedge
            self.assertFalse(self.ready)
            self.assertTrue(self.tx_fifo_enqueue)
            self.assertEquals(self.tx_fifo_data_write, 0x7D)

            yield self.clk.negedge
            self.assertFalse(self.ready)
            self.assertTrue(self.tx_fifo_enqueue)
            self.assertEquals(self.tx_fifo_data_write, self.spec.chr_stop)

            self.stop_simulation()

        self.simulate([test])


