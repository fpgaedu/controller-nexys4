from myhdl import (Signal, ResetSignal, intbv, Simulation, StopSimulation,
        instance, delay, now)
from unittest import TestCase
from fpgaedu.hdl import ClockGen, UartRx
from random import randint

class UartRxTestCase(TestCase):

    DATA_BITS = 8
    STOP_BITS = 1
    HALF_PERIOD = 1
    RX_DIV = 2

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
                self.rx_finish, self.rx_busy, self.rx_baud_tick, 
                data_bits=self.DATA_BITS, stop_bits=self.STOP_BITS,
                rx_div=self.RX_DIV)

    def simulate(self, test_logic, duration=None):
        sim = Simulation(self.clockgen, self.uart_rx, *test_logic)
        sim.run(duration, quiet=False)

    def stop_simulation(self):
        raise StopSimulation()

    def test_rx_receive(self):

        test_data = ['10101010', '00110011', '011001110']

        @instance
        def monitor():
            for data in test_data:
                yield self.rx_finish.posedge
                print(data)
                print('bingo! received %s' % bin(self.rx_data))
                self.assertEquals(self.rx_data, int(data, 2))

        @instance
        def test():
    
            self.rx.next = self.IDLE
            self.rx_baud_tick.next = False
            self.reset.next = False

            yield self.clk.negedge
            self.reset.next = True
            yield self.clk.negedge

            def baud_tick(n):
                for _ in range(n):
                    for _ in range(49):
                        yield self.clk.negedge
                    self.rx_baud_tick.next = True
                    yield self.clk.negedge
                    self.rx_baud_tick.next = False
                    yield self.clk.negedge

            for data in test_data:
                print('new iteration: now %s' % now())
                self.rx.next = self.START
                yield baud_tick(self.RX_DIV)
                for bit in data[::-1]:
                    self.rx.next = (bit == '1')
                    yield baud_tick(self.RX_DIV)
                self.rx.next = self.STOP
                yield baud_tick(self.RX_DIV)
                yield baud_tick(self.RX_DIV)
                    
            self.stop_simulation()

        self.simulate([test, monitor])
