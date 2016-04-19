from unittest import TestCase
from myhdl import (Signal, intbv, ResetSignal, instance, delay, Simulation,
        StopSimulation, now, bin)

from fpgaedu import ControllerSpec
from fpgaedu.hdl import ClockGen
from fpgaedu.hdl.nexys4 import BoardComponentRx

class BoardComponentRxTestCase(TestCase):

    HALF_PERIOD = 5
    UART_RX_BAUD_DIV = 8
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
        self.rx = Signal(False)
        self.rx_next = Signal(False)
        self.uart_rx_baud_tick = Signal(False)
        # Output signals
        self.rx_msg = Signal(intbv(0)[self.spec.width_message:0])
        self.rx_ready = Signal(False)

        self.clockgen = ClockGen(clk=self.clk, half_period=self.HALF_PERIOD)
        self.component_rx = BoardComponentRx(spec=self.spec, clk=self.clk,
                reset=self.reset, rx=self.rx, rx_msg=self.rx_msg, 
                rx_ready=self.rx_ready, rx_next=self.rx_next, 
                uart_rx_baud_tick=self.uart_rx_baud_tick, 
                uart_rx_baud_div=self.UART_RX_BAUD_DIV)

    def simulate(self, test_logic, duration=None):
        sim = Simulation(self.clockgen, self.component_rx, *test_logic)
        sim.run(duration, quiet=False)

    def stop_simulation(self):
        raise StopSimulation()

    def test_rx(self):

        

        @instance
        def monitor():
            yield self.rx_ready.posedge, delay(500000)
            yield delay(1)
            print(now())
            self.assertEquals(self.rx_msg, 0x0FFFFFFFFFFF)
            self.assertTrue(self.rx_ready)
            self.stop_simulation()

        @instance
        def stimulant():
            yield self.clk.negedge

            self.rx.next = self.LVL_IDLE
            self.reset.next = not self.reset.active
            self.rx_next.next = False
            self.uart_rx_baud_tick.next = False
            yield self.clk.negedge
            
            def baud_ticks(n_ticks):
                for _ in range(n_ticks):
                    for _ in range(5):
                        yield self.clk.negedge
                    self.uart_rx_baud_tick.next = True
                    yield self.clk.negedge
                    self.uart_rx_baud_tick.next = False
                    yield self.clk.negedge

            def transmit(char):

                yield baud_ticks(self.UART_RX_BAUD_DIV)
                self.rx.next = self.LVL_START
                yield baud_ticks(self.UART_RX_BAUD_DIV)

                indexes = range(8)[::-1]
                for i in indexes:
                    lvl = bin(char, width=8)[i] == '1'
                    self.rx.next = lvl
                    yield baud_ticks(self.UART_RX_BAUD_DIV)

                self.rx.next = self.LVL_STOP
                yield baud_ticks(self.UART_RX_BAUD_DIV)

            yield transmit(0x1)
            yield transmit(self.spec.chr_start)
            for i in range(8):
                yield transmit(0xFF)
            yield transmit(self.spec.chr_stop)

#            for i in range(8):
#                self.rx.next = self.LVL_START
#                for i in range(8):
#                    yield self.clk.negedge
#
#                self.rx.next = self.LVL_HIGH
#                for i in range(8*8):
#                    yield self.clk.negedge
#
#                self.rx.next = self.LVL_STOP
#                for i in range(8):
#                    yield self.clk.negedge


        self.simulate([monitor, stimulant])
