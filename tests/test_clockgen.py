from unittest import TestCase
from myhdl import Signal, Simulation, delay, instance, now, StopSimulation
from fpgaedu.hdl import ClockGen

class ClockGenTestCase(TestCase):

    def test_clockgen_basic(self):

        clk = Signal(False)
        half_period = 10
        clockgen = ClockGen(clk, half_period)

        @instance
        def test():
            for i in range(0, 100, 2):
                self.assertEquals(now(), i*half_period)
                yield clk.posedge
                self.assertEquals(now(), (i+1)*half_period)
                yield clk.negedge

            raise StopSimulation()


        sim = Simulation(clockgen, test)
        sim.run()

        
