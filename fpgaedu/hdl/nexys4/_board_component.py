from myhdl import Signal, intbv, always_comb

from fpgaedu import ControllerSpec
from fpgaedu.hdl import (Controller, UartRx, UartTx, BaudGen, Fifo,
        MessageReceiver, MessageTransmitter)
from fpgaedu.hdl.nexys4 import ClockEnableBuffer

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

    uart_rx_busy = Signal(False)
    uart_rx_data = Signal(intbv(0)[_DATA_BITS:0])
    uart_rx_finish = Signal(False)

    uart_tx_data = Signal(intbv(0)[_DATA_BITS:0])
    uart_tx_start = Signal(False)
    uart_tx_busy = Signal(False)

    rx_fifo_empty = Signal(False)
    rx_fifo_full = Signal(False)
    rx_fifo_dequeue = Signal(False)
    rx_fifo_dout = Signal(intbv(0)[_DATA_BITS:0])
    rx_fifo_din = Signal(intbv(0)[_DATA_BITS:0])
    rx_fifo_enqueue = Signal(False)

    tx_fifo_empty = Signal(False)
    tx_fifo_full = Signal(False)
    tx_fifo_enqueue = Signal(False)
    tx_fifo_din = Signal(intbv(0)[_DATA_BITS:0])
    tx_fifo_dout = Signal(intbv(0)[_DATA_BITS:0])
    tx_fifo_dequeue = Signal(False)

    message_rx_data = Signal(intbv(0)[spec.width_message:0])
    message_rx_ready = Signal(False)
    message_rx_recv_next = Signal(False)

    message_tx_data = Signal(intbv(0)[spec.width_message:0])
    message_tx_ready = Signal(False)
    message_tx_trans_next = Signal(False)

    controller = Controller(spec=spec, clk=clk, reset=reset, 
            rx_fifo_data_read=message_rx_data, 
            rx_fifo_dequeue=message_rx_recv_next, 
            rx_fifo_empty=message_rx_ready,
            tx_fifo_data_write=message_tx_data, 
            tx_fifo_enqueue=message_tx_trans_next, 
            tx_fifo_full= message_tx_ready,
            exp_addr=exp_addr, exp_data_write=exp_data_write, 
            exp_data_read=exp_data_read, exp_wen=exp_wen, exp_reset=exp_reset, 
            exp_clk_en=exp_clk_en, exp_reset_active=exp_reset_active)

    uart_rx = UartRx(clk=clk, reset=reset, rx=rx, rx_data=uart_rx_data, 
            rx_finish=uart_rx_finish, rx_busy=uart_rx_busy, 
            rx_baud_tick=rx_baud_tick, data_bits=_DATA_BITS, 
            stop_bits=_STOP_BITS, rx_div=_RX_DIV)

    uart_tx = UartTx(clk=clk, reset=reset, tx=tx, tx_data=uart_tx_data, 
            tx_start=uart_tx_start, tx_busy=uart_tx_busy,
            baud_tick=tx_baud_tick, data_bits=_DATA_BITS, 
            stop_bits=_STOP_BITS)

    baudgen = BaudGen(clk=clk, reset=reset, rx_tick=rx_baud_tick, 
            tx_tick=tx_baud_tick, baudrate=baudrate, rx_div=_RX_DIV)

    fifo_rx = Fifo(clk=clk, reset=reset, din=rx_fifo_din, 
            enqueue=rx_fifo_enqueue, dout=rx_fifo_dout, 
            dequeue=rx_fifo_dequeue, empty=rx_fifo_empty, full=rx_fifo_full, 
            data_width=spec.width_data, depth=_RX_FIFO_DEPTH)

    fifo_tx = Fifo(clk=clk, reset=reset, din=tx_fifo_din, 
            enqueue=tx_fifo_enqueue, dout=tx_fifo_dout, 
            dequeue=tx_fifo_dequeue, empty=tx_fifo_empty, full=tx_fifo_full, 
            data_width=spec.width_data, depth=_TX_FIFO_DEPTH)

    message_receiver = MessageReceiver(spec=spec, clk=clk, reset=reset,
            rx_fifo_data_read=rx_fifo_dout, rx_fifo_empty=rx_fifo_empty, 
            rx_fifo_dequeue=rx_fifo_dequeue, message=message_rx_data, 
            message_ready=message_rx_ready, receive_next=message_rx_recv_next)

    message_transmitter = MessageTransmitter(spec=spec, clk=clk, reset=reset,
            tx_fifo_data_write=tx_fifo_din, tx_fifo_full=tx_fifo_full, 
            tx_fifo_enqueue=tx_fifo_enqueue, message=message_tx_data, 
            ready=message_tx_ready, transmit_next=message_tx_trans_next)

    clock_enable_buffer = ClockEnableBuffer(clk_in=clk, clk_out=exp_clk, 
            clk_en=exp_clk_en)

    @always_comb
    def fifo_to_uart_tx():
        uart_tx_data.next = tx_fifo_dout
        uart_tx_start.next = (not tx_fifo_empty and not uart_tx_busy)
        tx_fifo_dequeue.next = (not tx_fifo_empty and not uart_tx_busy)

    @always_comb
    def uart_rx_to_fifo():
        rx_fifo_enqueue.next = uart_rx_finish
        rx_fifo_din.next = uart_rx_data

    return (controller, uart_rx, uart_tx, baudgen, fifo_rx, fifo_tx,
            message_receiver, message_transmitter, clock_enable_buffer,
            fifo_to_uart_tx, uart_rx_to_fifo)

