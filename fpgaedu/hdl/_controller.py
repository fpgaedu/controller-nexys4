from myhdl import always_seq, always_comb

def Controller(clk, reset, rx_fifo_dout, rx_fifo_dequeue, rx_fifo_empty, 
        tx_fifo_din, tx_fifo_enqueue, tx_fifo_full, exp_addr, exp_din, 
        exp_dout, exp_wen, exp_reset, exp_clk):
    '''
    clk
        Clock input
    reset
        Reset input
    rx_fifo_dout
        Input signal reading the rx fifo's dout signal
    rx_fifo_dequeue
        Output pulse signal signalling the rx fifo to pop the current oldest item
    rx_fifo_empty
        Input signal indicating whether the rx fifo is empty
    tx_fifo_din
        Output signal setting the value to add to the tx fifo
    tx_fifo_enqueue
        Output pulse signal signallig the tx_fifo to add the value set on 
        tx_fifo_din to be pushed onto its queue
    tx_fifo_full
        Input signal indicating that the tx_fifo is full
    exp_addr
        Output signal setting the address for the experiment to be operated on
    exp_din
        Output signal setting the value to write to the experiment 
    exp_dout
        Input signal containing the data that is read from the experiment
    exp_wen
        Output pulse signal indicating to the experiment that the current 
        operation is a write operation
    exp_reset
        Output signal indicating to the experiment that it is to be reset to 
        its initial state
    exp_clk
        Output gated clock signal for the experiment


    The controller supports the following commands:

    read(address)
        Reads the value on the specified address. Responds with the requested
        value
    write(address, value)
        Writes the given value to the specified address. Responds to confirm if
        successfull, unsuccessfull
    reset()
        Resets the experiment state to its initial condition
    step(n)
        enables the experiment clock for n cycles
    start()
        the controller will switch to autonomous mode
    pause()
        the controller will return to manual mode
    status()
        request the controller status


    The controller will return the following responses to the PC:

    read success(address, value)
    read error - address out of range(address)
    read error - controller in autonomous mode
    write success(address, value)
    write error - address out of range(address)
    write error - controller in autonomous mode
    reset acknowledge
    step acknowledge(n)
    start acknowledge
    pause acknowledge
    status result(status)
        manual: status = 0
        autonomous: status = 1

    message layout
    
    31            24 23           16 15            8 7             0
     |----opcode---| |-----arg0----| |-----arg1----| |-----arg2----|
     |             | |             | |             | |             |
    |-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|


    command opcodes:
    0b00000000 0x00 Read
    0b00000001 0x01 Write 
    0b00000010 0x02 Reset
    0b00000011 0x03 Step
    0b00000100 0x04 Start 
    0b00000101 0x05 Start 

    response opcodes:
    0b10000000 0x80 Read success
    0b10000001 0x81 Read error - address out of range
    0b10000010 0x82 Read error - controller in autonomous mode
    0b10000011 0x83 Write success
    0b10000100 0x84 Write error - address out of range
    0b10000101 0x85 Read error - controller in autonomous mode
    0b10000110 0x86 Reset ack
    0b10000111 0x87 Start ack
    0b10001000 0x88 Start error - controller already in autonomous mode
    0b10001001 0x89 Pause ack
    0b10001010 0x8A Pause error - controller already in manual mode
    0b10001011 0x8B Status result
    
    '''
    pass
