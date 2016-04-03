import os
from myhdl import toVHDL, Signal, ResetSignal, intbv
from fpgaedu.hdl import (BaudGen, UartRx, UartTx, BaudGenRxLookup, Rom)

# Instance constants
_CLK_FREQ = 100000000
_UART_BAUDRATE = 9600
_UART_RX_DIV = 16
_UART_DATA_BITS = 8
_UART_STOP_BITS = 1

# toVHDL() constants
_STD_LOGIC_PORTS = True
_OUTPUT_DIRECTORY = './vhdl/'

# Signals
_CLK = Signal(False)
_RESET = ResetSignal(True, active=False, async=False)

_UART_RX = Signal(False)
_UART_RX_TICK = Signal(False)
_UART_RX_DATA = Signal(intbv(0)[_UART_DATA_BITS:0])
_UART_RX_FINISH = Signal(False)
_UART_RX_BUSY = Signal(False)
_UART_RX_BAUD_TICK = Signal(False)

_UART_TX = Signal(False)
_UART_TX_TICK = Signal(False)
_UART_TX_DATA = Signal(intbv(0)[_UART_DATA_BITS:0])

def _create_output_directory():
    if not os.path.exists(_OUTPUT_DIRECTORY):
        os.makedirs(_OUTPUT_DIRECTORY)

def _set_tovhdl_defaults(name, directory=_OUTPUT_DIRECTORY):
    toVHDL.std_logic_ports = True
    toVHDL.name = name
    toVHDL.directory = directory 

def _generate_baudgen_rx_lookup():
    _set_tovhdl_defaults('baudgen_rx_lookup')
    toVHDL(BaudGenRxLookup, _RX_LOOKUP_DOUT, _RX_LOOKUP_ADDR)

def _generate_uart_rx():
    _set_tovhdl_defaults('uart_rx')
    toVHDL(UartRx, _CLK, _RESET, _UART_RX, _UART_RX_DATA, _UART_RX_FINISH, 
            _UART_RX_BUSY, _UART_RX_BAUD_TICK, data_bits=_UART_DATA_BITS, 
            stop_bits=_UART_STOP_BITS, rx_div=_UART_RX_DIV)

def _generate_baudgen():
    _set_tovhdl_defaults('baudgen')
    toVHDL(BaudGen, _CLK, _RESET, _UART_RX_TICK, _UART_TX_TICK, 
            clk_freq=_CLK_FREQ,
            baudrate=_UART_BAUDRATE, rx_div=_UART_RX_DIV)

if __name__ == '__main__':
    _create_output_directory()
    #_generate_rom()
    #_generate_baudgen_rx_lookup()
    _generate_uart_rx()
    _generate_baudgen()


