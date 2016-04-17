from myhdl import Signal, intbv
from fpgaedu.hdl import TestExperiment, nexys4

def TestSetup(spec, clk, reset, rx, tx):
    
    exp_addr = Signal(intbv(0)[spec.width_addr:0])
    exp_din = Signal(intbv(0)[spec.width_data])
    exp_dout = Signal(intbv(0)[spec.width_data])
    exp_wen = Signal(False)
    exp_reset = Signal(False)
    exp_clk = Signal(False)

    board_component = nexys4.BoardComponent(spec, clk, reset, rx, tx, 
            exp_addr, exp_din, exp_dout, exp_wen, exp_reset, exp_clk, 
            exp_reset_active=True, baudrate=9600)
    test_experiment = TestExperiment(clk, reset, addr, din, dout, wen)


