from myhdl import Signal, intbv
from fpgaedu.hdl import UartRx, Fifo, MessageReceiver

def BoardComponentRx(spec, clk, reset, rx, rx_msg, rx_ready, rx_next, 
        uart_rx_baud_tick, uart_rx_baud_div=8):
    '''
    clk
        Clock input
    reset
        Reset input
    rx
        rx input
    rx_msg
        Output which exposes the received message
    rx_ready
        Output indicating that a message has been received successfully,
        and is ready to be read the message is output on recv_data
    rx_next
        Input signalling the component to start receiving the next message
    '''

    uart_rx_data = Signal(intbv(0)[8:0])
    uart_rx_finish = Signal(False)
    uart_rx_busy = Signal(False)

    fifo_rx_dout = Signal(intbv(0)[8:0])
    fifo_rx_dequeue = Signal(False)
    fifo_rx_empty = Signal(False)
    fifo_rx_full = Signal(False)
    
    uart_rx = UartRx(clk=clk, reset=reset, rx=rx, rx_data=uart_rx_data, 
            rx_finish=uart_rx_finish, rx_busy=uart_rx_busy,
            rx_baud_tick=uart_rx_baud_tick, data_bits=8, stop_bits=1,
            rx_div=uart_rx_baud_div)

    fifo_rx = Fifo(clk=clk, reset=reset, din=uart_rx_data, dout=fifo_rx_dout,
            enqueue=uart_rx_finish, dequeue=fifo_rx_dequeue,
            empty=fifo_rx_empty, full=fifo_rx_full, data_width=8,
            depth=12)

    receiver = MessageReceiver(spec=spec, clk=clk, reset=reset, 
            rx_fifo_data_read=fifo_rx_dout, rx_fifo_empty=fifo_rx_empty,
            rx_fifo_dequeue=fifo_rx_dequeue, message=rx_msg, 
            message_ready=rx_ready, receive_next=rx_next)

    return uart_rx, fifo_rx, receiver


