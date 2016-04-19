from myhdl import Signal, intbv, always_comb
from fpgaedu.hdl import UartTx, Fifo, MessageTransmitter

def BoardComponentTx(spec, clk, reset, tx, tx_msg, tx_ready, tx_next, 
        uart_tx_baud_tick):
    '''
    clk
        Clock input
    reset
        Reset input
    tx
        uart tx output
    tx_msg
        Input on which the output message data can be set
    tx_ready
        Output indicating that the component is ready to transmit the next
        message
    tx_next
        Input signal instructing the component to transmit the message 
        as set on tx_msg
    '''
    
    uart_tx_data = Signal(intbv(0)[8:0])
    uart_tx_start = Signal(False)
    uart_tx_busy = Signal(False)

    fifo_tx_din = Signal(intbv(0)[8:0])
    fifo_tx_enqueue = Signal(False)
    fifo_tx_dout = Signal(intbv(0)[8:0])
    fifo_tx_dequeue = Signal(False)
    fifo_tx_empty = Signal(False)
    fifo_tx_full = Signal(False)

    uart_tx = UartTx(clk=clk, reset=reset, tx=tx, tx_data=uart_tx_data, 
            tx_start=uart_tx_start, tx_busy=uart_tx_busy, 
            baud_tick=uart_tx_baud_tick, data_bits=8, stop_bits=1)

    fifo_tx = Fifo(clk=clk, reset=reset, din=fifo_tx_din, 
            enqueue=fifo_tx_enqueue, dout=fifo_tx_dout, 
            dequeue=fifo_tx_dequeue, empty=fifo_tx_empty, full=fifo_tx_full,
            data_width=8, depth=12)

    transmitter = MessageTransmitter(spec=spec, clk=clk, reset=reset,
            tx_fifo_data_write=fifo_tx_din, tx_fifo_full=fifo_tx_full,
            tx_fifo_enqueue=fifo_tx_enqueue, message=tx_msg, 
            ready=tx_ready, transmit_next=tx_next)

    @always_comb
    def fifo_to_uart_logic():
        uart_tx_data.next = fifo_tx_dout
        uart_tx_start.next = (not uart_tx_busy and not fifo_tx_empty)
        fifo_tx_dequeue.next = (not uart_tx_busy and not fifo_tx_empty)

    return uart_tx, fifo_tx, transmitter, fifo_to_uart_logic


