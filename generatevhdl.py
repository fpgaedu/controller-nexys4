import os
from myhdl import toVHDL, Signal, ResetSignal, intbv
from fpgaedu.hdl import BaudGen, UartRx, UartTx, BaudGenRxLookup, Rom

# Instance constants
_BAUDRATE = 9600
_CLK_FREQ = 50000000
_RX_DIV = 16

# toVHDL() constants
_STD_LOGIC_PORTS = True
_OUTPUT_DIRECTORY = './vhdl/'

# Signals
_CLK = Signal(False)
_RESET = ResetSignal(True, active=False, async=False)
_RX_TICK = Signal(False)
_TX_TICK = Signal(False)

_RX_LOOKUP_ADDR = Signal(intbv(0, min=0, max=_RX_DIV))
_RX_LOOKUP_DOUT = Signal(intbv(0, min=0, max=16))

def _create_output_directory():
    if not os.path.exists(_OUTPUT_DIRECTORY):
        os.makedirs(_OUTPUT_DIRECTORY)

def _set_tovhdl_defaults(name, directory=_OUTPUT_DIRECTORY):
    toVHDL.std_logic_ports = True
    toVHDL.name = name
    toVHDL.directory = directory 

def _generate_rom():
    _set_tovhdl_defaults('rom')
    content = (0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15)
    toVHDL(Rom, _RX_LOOKUP_DOUT, _RX_LOOKUP_ADDR, content)

def _generate_baudgen_rx_lookup():
    _set_tovhdl_defaults('baudgen_rx_lookup')
    toVHDL(BaudGenRxLookup, _RX_LOOKUP_DOUT, _RX_LOOKUP_ADDR)

def _generate_baudgen():
    _set_tovhdl_defaults('baudgen')
    toVHDL(BaudGen, _CLK, _RESET, _RX_TICK, _TX_TICK, clk_freq=_CLK_FREQ,
            baudrate=_BAUDRATE, rx_div=_RX_DIV)

if __name__ == '__main__':
    _create_output_directory()
    #_generate_rom()
    #_generate_baudgen_rx_lookup()
    _generate_baudgen()


