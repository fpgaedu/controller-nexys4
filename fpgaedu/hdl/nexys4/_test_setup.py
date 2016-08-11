from myhdl import Signal, intbv
from fpgaedu.hdl.nexys4 import BoardComponent
from fpgaedu.hdl.testexperiment._wrapper_composition import WrapperComposition

def TestSetup(spec, clk, reset, rx, tx):
    
    exp_addr = Signal(intbv(0)[spec.width_addr:0])
    exp_din = Signal(intbv(0)[spec.width_data:0])
    exp_dout = Signal(intbv(0)[spec.width_data:0])
    exp_wen = Signal(False)
    exp_reset = Signal(False)
    exp_clk = Signal(False)

    board_component = BoardComponent(spec, clk, reset, rx, tx, 
            exp_addr, exp_din, exp_dout, exp_wen, exp_reset, exp_clk, 
            exp_reset_active=True, baudrate=9600)
#    test_experiment = TestExperiment(exp_clk, exp_reset, exp_addr, exp_din, 
#            exp_dout, exp_wen)
    wrapper = WrapperComposition(clk=clk, exp_clk=exp_clk, exp_reset=exp_reset,
            din=exp_din, dout=exp_dout, addr=exp_addr, wen=exp_wen)

    return board_component, wrapper
