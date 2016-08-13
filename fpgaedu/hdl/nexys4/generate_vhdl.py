import os, sys, argparse
from myhdl import toVHDL, toVerilog, Signal, ResetSignal, intbv
from fpgaedu import ControllerSpec
from fpgaedu.hdl.nexys4 import BoardComponent

_UART_BAUDRATE = 9600
# NEXYS 4 board reset signal is active-low
_RESET_ACTIVE = False

def _parse_args():
    '''
    Parses the command line arguments.
    '''
    parser = argparse.ArgumentParser(description='Generates digilent nexys \
            board component vhdl source files.')
    parser.add_argument('-o', '--outputDir', required=True, 
            help='The source file output directory.');
    parser.add_argument('-a', '--addressWidth', required=True, type=int)
    parser.add_argument('-d', '--dataWidth', required=True, type=int)
    parser.add_argument('-t', '--topLevel', required=True, 
            help='The output top-level file\'s file name.')
    parser.add_argument('-r', '--resetActive', required=True, type=bool,
            help='Whether the experiment setup reset is active-high ("True") or \
                    active-low ("False").')
    
    return parser.parse_args()

def _generate_vhdl(output_dir, width_addr, width_data, top_level_file_name, \
        exp_reset_active):
    toVHDL.std_logic_ports = True
    toVHDL.name = os.path.splitext(top_level_file_name)[0]
    toVHDL.directory = output_dir 
    toVHDL.use_clauses = \
'''
Library UNISIM;
use UNISIM.vcomponents.all;

use work.pck_myhdl_090.all;
'''
    
    spec = ControllerSpec(width_addr, width_data)

    clk = Signal(False)
    reset = ResetSignal(not _RESET_ACTIVE, active=_RESET_ACTIVE, async=False)
    rx = Signal(False)
    tx = Signal(False)
    exp_addr = Signal(intbv(0)[width_addr:0])
    exp_din = Signal(intbv(0)[width_data:0])
    exp_dout = Signal(intbv(0)[width_data:0])
    exp_wen = Signal(False)
    exp_reset = Signal(False)
    exp_clk = Signal(False)

    toVHDL(BoardComponent, spec=spec, clk=clk, reset=reset,
            rx=rx, tx=tx, exp_addr=exp_addr, exp_data_write=exp_din, 
            exp_data_read=exp_dout, 
            exp_wen=exp_wen, exp_reset=exp_reset, exp_clk=exp_clk, 
            exp_reset_active=exp_reset_active, baudrate=_UART_BAUDRATE)

if __name__ == '__main__':
    args = _parse_args()

    _generate_vhdl(args.outputDir, args.addressWidth, args.dataWidth, 
            args.topLevel, args.resetActive)

