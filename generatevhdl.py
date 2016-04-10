import os
from myhdl import toVHDL, Signal, ResetSignal, intbv
from fpgaedu import ControllerSpec
from fpgaedu.hdl import (BaudGen, UartRx, UartTx, BaudGenRxLookup, Rom, Fifo,
        Controller)

# Instance constants
_CLK_FREQ = 100000000
_UART_BAUDRATE = 9600
_UART_RX_DIV = 16
_UART_DATA_BITS = 8
_UART_STOP_BITS = 1
_WIDTH_DATA = 8
_WIDTH_ADDR = 32
_SPEC = ControllerSpec(_WIDTH_ADDR, _WIDTH_DATA)

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

_FIFO_DIN = Signal(intbv(0)[32:0])
_FIFO_DOUT = Signal(intbv(0)[32:0])
_FIFO_ENQUEUE = Signal(False)
_FIFO_DEQUEUE = Signal(False)
_FIFO_EMPTY = Signal(False)
_FIFO_FULL = Signal(False)

_TX_FIFO_DIN = Signal(intbv(0)[_SPEC.width_message:0])
_TX_FIFO_DOUT = Signal(intbv(0)[_SPEC.width_message:0])
_TX_FIFO_ENQUEUE = Signal(False)
_TX_FIFO_DEQUEUE = Signal(False)
_TX_FIFO_EMPTY = Signal(False)
_TX_FIFO_FULL = Signal(False)

_RX_FIFO_DIN = Signal(intbv(0)[_SPEC.width_message:0])
_RX_FIFO_DOUT = Signal(intbv(0)[_SPEC.width_message:0])
_RX_FIFO_ENQUEUE = Signal(False)
_RX_FIFO_DEQUEUE = Signal(False)
_RX_FIFO_EMPTY = Signal(False)
_RX_FIFO_FULL = Signal(False)

_EXP_ADDR = Signal(intbv(0)[_SPEC.width_addr:0])
_EXP_DIN = Signal(intbv(0)[_SPEC.width_data:0])
_EXP_DOUT = Signal(intbv(0)[_SPEC.width_data:0])
_EXP_WEN = Signal(False)
_EXP_RESET = Signal(False)
_EXP_CLK = Signal(False)

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

def _generate_fifo():
    _set_tovhdl_defaults('fifo')
    toVHDL(Fifo, _CLK, _RESET, _FIFO_DIN, _FIFO_ENQUEUE, _FIFO_DOUT,
            _FIFO_DEQUEUE, _FIFO_EMPTY, _FIFO_FULL)

def _generate_controller():
    _set_tovhdl_defaults('controller')
    toVHDL(Controller, spec=_SPEC, clk=_CLK, reset=_RESET, 
            rx_fifo_dout=_RX_FIFO_DOUT, rx_fifo_dequeue=_RX_FIFO_DEQUEUE,
            rx_fifo_empty=_RX_FIFO_EMPTY, tx_fifo_din=_TX_FIFO_DIN,
            tx_fifo_enqueue=_TX_FIFO_ENQUEUE, tx_fifo_full=_TX_FIFO_FULL,
            exp_addr=_EXP_ADDR, exp_din=_EXP_DIN, exp_dout=_EXP_DOUT, 
            exp_wen=_EXP_WEN, exp_reset=_EXP_RESET, exp_clk=_EXP_CLK)

if __name__ == '__main__':
    _create_output_directory()
    #_generate_rom()
    #_generate_baudgen_rx_lookup()
    _generate_controller()
    _generate_uart_rx()
    _generate_baudgen()
    _generate_fifo()
