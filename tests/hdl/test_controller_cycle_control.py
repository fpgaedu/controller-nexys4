from myhdl import (Signal, ResetSignal, intbv, always, instance, Simulation, 
        StopSimulation, delay)
from unittest import TestCase
from fpgaedu import ControllerSpec
from fpgaedu.hdl import ClockGen
from fpgaedu.hdl._controller_cycle_control import ControllerCycleControl

class ControllerCycleControlTestCase(TestCase):

    WIDTH_ADDR = 32
    WIDTH_DATA = 8
    HALF_PERIOD = 5

    def setUp(self):

        self.spec = ControllerSpec(self.WIDTH_ADDR, self.WIDTH_DATA)
        #input signals
        self.clk = Signal(False)
        self.reset = ResetSignal(True, active=False, async=False)
        self.start = Signal(False)
        self.pause = Signal(False)
        self.step = Signal(False)
        #output signals
        self.autonomous = Signal(False)
        self.cycle_count = Signal(intbv(0)[self.spec.width_value:0])
        self.exp_clk_en = Signal(False)
        #instances
        self.clockgen = ClockGen(self.clk, self.HALF_PERIOD)
        self.cycle_control = ControllerCycleControl(spec=self.spec,
                clk=self.clk, reset=self.reset, start=self.start, 
                pause=self.pause, step=self.step, 
                cycle_autonomous=self.autonomous,
                cycle_count=self.cycle_count, exp_clk_en=self.exp_clk_en)

    def simulate(self, test_logic, duration=None):
        sim = Simulation(self.clockgen, self.cycle_control, test_logic)
        sim.run(duration, quiet=False)

    def stop_simulation(self):
        raise StopSimulation()

    def test_cycle_control_step(self):

        @instance
        def test_method():
            self.reset.next = False
            yield self.clk.negedge

            self.reset.next = True
            self.start.next = False
            self.pause.next = False
            self.step.next =  False
            yield self.clk.posedge
            self.assertFalse(self.autonomous)
            self.assertEquals(self.cycle_count, 0)
            self.assertFalse(self.exp_clk_en)
            self.step.next = True

            yield self.clk.negedge
            yield delay(1)
            self.assertFalse(self.autonomous)
            self.assertEquals(self.cycle_count, 1)
            self.assertTrue(self.exp_clk_en)

            yield self.clk.posedge
            yield delay(1)
            self.step.next = False

            yield self.clk.negedge
            yield delay(1)
            self.assertFalse(self.autonomous)
            self.assertEquals(self.cycle_count, 1)
            self.assertFalse(self.exp_clk_en)

            yield self.clk.posedge
            yield delay(1)
            self.step.next = True

            yield self.clk.negedge
            yield delay(1)
            self.assertFalse(self.autonomous)
            self.assertEquals(self.cycle_count, 2)
            self.assertTrue(self.exp_clk_en)

            yield self.clk.posedge
            yield delay(1)
            self.step.next = False

            yield self.clk.negedge
            yield delay(1)
            self.assertFalse(self.autonomous)
            self.assertEquals(self.cycle_count, 2)
            self.assertFalse(self.exp_clk_en)

            self.stop_simulation()

        self.simulate(test_method)


    def test_cycle_control_start_pause(self):

        @instance
        def test():
            self.reset.next = False

            yield self.clk.negedge
            yield self.clk.posedge
            self.reset.next = True
            self.start.next = False
            self.pause.next = False
            self.step.next = False

            yield self.clk.negedge
            yield delay(1)
            self.assertFalse(self.autonomous)
            self.assertEquals(self.cycle_count, 0)
            self.assertFalse(self.exp_clk_en)

            yield self.clk.posedge
            yield delay(1)
            self.start.next = True

            yield self.clk.negedge
            yield delay(1)
            self.assertTrue(self.autonomous)
            self.assertEquals(self.cycle_count, 1)
            self.assertTrue(self.exp_clk_en)

            yield self.clk.posedge
            yield delay(1)
            self.start.next = False

            yield self.clk.negedge
            yield delay(1)
            self.assertTrue(self.autonomous)
            self.assertEquals(self.cycle_count, 2)
            self.assertTrue(self.exp_clk_en)

            yield self.clk.negedge
            yield delay(1)
            self.assertTrue(self.autonomous)
            self.assertEquals(self.cycle_count, 3)
            self.assertTrue(self.exp_clk_en)

            yield self.clk.posedge
            yield delay(1)
            self.pause.next = True

            yield self.clk.negedge
            yield delay(1)
            self.assertFalse(self.autonomous)
            self.assertEquals(self.cycle_count, 3)
            self.assertFalse(self.exp_clk_en)

            yield self.clk.posedge
            yield delay(1)
            self.pause.next = False

            yield self.clk.negedge
            yield delay(1)
            self.assertFalse(self.autonomous)
            self.assertEquals(self.cycle_count, 3)
            self.assertFalse(self.exp_clk_en)

            yield self.clk.posedge
            yield delay(1)
            self.start.next = True

            yield self.clk.negedge
            yield delay(1)
            self.assertTrue(self.autonomous)
            self.assertEquals(self.cycle_count, 4)
            self.assertTrue(self.exp_clk_en)

            yield self.clk.posedge
            yield delay(1)
            self.start.next = False

            yield self.clk.negedge
            yield delay(1)
            self.assertTrue(self.autonomous)
            self.assertEquals(self.cycle_count, 5)
            self.assertTrue(self.exp_clk_en)

            self.stop_simulation()
             
        self.simulate(test)
