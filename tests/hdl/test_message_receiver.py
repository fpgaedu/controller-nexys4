from myhdl import (Signal, ResetSignal, intbv, always, instance, Simulation, 
        StopSimulation, delay, always_comb)
from unittest import TestCase

from fpgaedu import ControllerSpec
from fpgaedu.hdl import ClockGen, MessageReceiver

class MessageReceiverTestCase(TestCase):

    HALF_PERIOD = 5
    WIDTH_ADDR = 32
    WIDTH_DATA = 8

    def setUp(self):
        
        self.spec = ControllerSpec(self.WIDTH_ADDR, self.WIDTH_DATA)

        # Input signals
        self.clk = Signal(False)
        self.reset = ResetSignal(True, active=False, async=False)
        self.rx_fifo_data_read = Signal(intbv(0)[8:0])
        self.rx_fifo_empty = Signal(False)
        self.receive_next = Signal(False)
        # Output signals
        self.message = Signal(intbv(0)[self.spec.width_message:0])
        self.rx_fifo_dequeue = Signal(False)
        self.message_ready = Signal(False)

        self.clockgen = ClockGen(self.clk, self.HALF_PERIOD)
        self.receiver = MessageReceiver(spec=self.spec, clk=self.clk, 
                reset=self.reset, rx_fifo_data_read=self.rx_fifo_data_read,
                rx_fifo_empty=self.rx_fifo_empty, 
                rx_fifo_dequeue=self.rx_fifo_dequeue,
                message=self.message, message_ready=self.message_ready,
                receive_next=self.receive_next)


    def simulate(self, test_logic, duration=None):
        sim = Simulation(self.clockgen, self.receiver, *test_logic)
        sim.run(duration, quiet=False)

    def stop_simulation(self):
        raise StopSimulation()

    def test_message(self):
        
        @instance
        def test():
            yield self.clk.negedge

            self.reset.next = self.reset.active
            yield self.clk.negedge

            self.reset.next = not self.reset.active
            self.receive_next.next = False
            self.rx_fifo_empty.next = True
            self.rx_fifo_data_read.next = 0
            yield self.clk.negedge
            self.assertFalse(self.rx_fifo_dequeue)
            self.assertFalse(self.message_ready)

            self.rx_fifo_empty.next = False
            self.rx_fifo_data_read.next = 0
            yield self.clk.negedge
            self.assertTrue(self.rx_fifo_dequeue)
            self.assertFalse(self.message_ready)

            self.rx_fifo_empty.next = False
            self.rx_fifo_data_read.next = self.spec.chr_start
            yield self.clk.negedge
            self.assertTrue(self.rx_fifo_dequeue)
            self.assertFalse(self.message_ready)

            self.rx_fifo_empty.next = False
            self.rx_fifo_data_read.next = 0x01
            yield self.clk.negedge
            self.assertTrue(self.rx_fifo_dequeue)
            self.assertFalse(self.message_ready)

            self.rx_fifo_empty.next = False
            self.rx_fifo_data_read.next = 0x02
            yield self.clk.negedge
            self.assertTrue(self.rx_fifo_dequeue)
            self.assertFalse(self.message_ready)

            self.rx_fifo_empty.next = False
            self.rx_fifo_data_read.next = 0x03
            yield self.clk.negedge
            self.assertTrue(self.rx_fifo_dequeue)
            self.assertFalse(self.message_ready)

            self.rx_fifo_empty.next = False
            self.rx_fifo_data_read.next = self.spec.chr_esc
            yield self.clk.negedge
            self.assertTrue(self.rx_fifo_dequeue)
            self.assertFalse(self.message_ready)

            self.rx_fifo_empty.next = False
            self.rx_fifo_data_read.next = self.spec.chr_start
            yield self.clk.negedge
            self.assertTrue(self.rx_fifo_dequeue)
            self.assertFalse(self.message_ready)

            self.rx_fifo_empty.next = False
            self.rx_fifo_data_read.next = 0x05
            yield self.clk.negedge
            self.assertTrue(self.rx_fifo_dequeue)
            self.assertFalse(self.message_ready)

            self.rx_fifo_empty.next = False
            self.rx_fifo_data_read.next = 0xFF
            yield self.clk.negedge
            self.assertTrue(self.rx_fifo_dequeue)
            self.assertFalse(self.message_ready)

            self.rx_fifo_empty.next = False
            self.rx_fifo_data_read.next = self.spec.chr_stop
            yield self.clk.negedge
            self.assertFalse(self.rx_fifo_dequeue)
            self.assertTrue(self.message_ready)
            

            self.stop_simulation()

        self.simulate([test])


