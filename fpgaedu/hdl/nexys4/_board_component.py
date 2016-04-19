from myhdl import Signal, intbv, always_comb

from fpgaedu import ControllerSpec
from fpgaedu.hdl import (Controller, UartRx, UartTx, BaudGen, Fifo,
        MessageReceiver, MessageTransmitter)
from ._clock_enable_buffer import ClockEnableBuffer
from ._board_component_tx import BoardComponentTx
from ._board_component_rx import BoardComponentRx
#from fpgaedu.hdl.nexys4 import (ClockEnableBuffer, BoardComponentRx, 
#        BoardComponentTx)

_CLK_FREQ = 100000000
_RX_DIV = 8

_TX_FIFO_DEPTH = 16
_RX_FIFO_DEPTH = 16

_DATA_BITS=8
_STOP_BITS=1

def BoardComponent(spec, clk, reset, rx, tx,
        exp_addr, exp_data_write, exp_data_read, exp_wen, exp_reset, 
        exp_clk, exp_reset_active=True, baudrate=9600):

    tx_baud_tick = Signal(False)
    rx_baud_tick = Signal(False)
    exp_clk_en = Signal(False)

    #uart_rx_busy = Signal(False)
    #uart_rx_data = Signal(intbv(0)[_DATA_BITS:0])
    #uart_rx_finish = Signal(False)

    #uart_tx_data = Signal(intbv(0)[_DATA_BITS:0])
    #uart_tx_start = Signal(False)
    #uart_tx_busy = Signal(False)

    #rx_fifo_empty = Signal(False)
    #rx_fifo_full = Signal(False)
    #rx_fifo_dequeue = Signal(False)
    #rx_fifo_dout = Signal(intbv(0)[_DATA_BITS:0])
    #rx_fifo_din = Signal(intbv(0)[_DATA_BITS:0])
    #rx_fifo_enqueue = Signal(False)

    #tx_fifo_empty = Signal(False)
    #tx_fifo_full = Signal(False)
    #tx_fifo_enqueue = Signal(False)
    #tx_fifo_din = Signal(intbv(0)[_DATA_BITS:0])
    #tx_fifo_dout = Signal(intbv(0)[_DATA_BITS:0])
    #tx_fifo_dequeue = Signal(False)

    message_rx_data = Signal(intbv(0)[spec.width_message:0])
    message_rx_ready = Signal(False)
    message_rx_recv_next = Signal(False)

    message_tx_data = Signal(intbv(0)[spec.width_message:0])
    message_tx_ready = Signal(False)
    message_tx_trans_next = Signal(False)

    controller = Controller(spec=spec, clk=clk, reset=reset, 
            rx_msg=message_rx_data, 
            rx_next=message_rx_recv_next, 
            rx_ready=message_rx_ready,
            tx_msg=message_tx_data, 
            tx_next=message_tx_trans_next, 
            tx_ready= message_tx_ready,
            exp_addr=exp_addr, exp_data_write=exp_data_write, 
            exp_data_read=exp_data_read, exp_wen=exp_wen, exp_reset=exp_reset, 
            exp_clk_en=exp_clk_en, exp_reset_active=exp_reset_active)

    component_rx = BoardComponentRx(spec=spec, clk=clk, reset=reset, rx=rx,
            rx_msg=message_rx_data, rx_ready=message_rx_ready, 
            rx_next=message_rx_recv_next, uart_rx_baud_tick=rx_baud_tick,
            uart_rx_baud_div=_RX_DIV)

    component_tx = BoardComponentTx(spec=spec, clk=clk, reset=reset, tx=tx,
            tx_msg=message_tx_data, tx_ready=message_tx_ready,
            tx_next=message_tx_trans_next, uart_tx_baud_tick=tx_baud_tick)

    baudgen = BaudGen(clk=clk, reset=reset, rx_tick=rx_baud_tick, 
            tx_tick=tx_baud_tick, baudrate=baudrate, rx_div=_RX_DIV)

    clock_enable_buffer = ClockEnableBuffer(clk_in=clk, clk_out=exp_clk, 
            clk_en=exp_clk_en)


    return (controller, baudgen, clock_enable_buffer, component_rx, 
            component_tx)

