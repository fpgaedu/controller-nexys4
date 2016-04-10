from myhdl import always_seq, always_comb, enum, Signal, intbv

def Controller(spec, clk, reset, rx_fifo_dout, rx_fifo_dequeue, rx_fifo_empty, 
        tx_fifo_din, tx_fifo_enqueue, tx_fifo_full, exp_addr, exp_din, 
        exp_dout, exp_wen, exp_reset, exp_clk_en):
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
    exp_clk_en
        Output clock enable signal for the experiment

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

    address-type message layout
    
    47            40 39             \   \    8 7             0
     |----opcode---| |----address---/   /----| |-----data----|
     |             | |              \   \    | |             |
    |-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-/   /-|-|-|-|-|-|-|-|-|-|-|
                                    \   \

    value-type message layout

    47            40 39                           \   \      0
     |----opcode---| |----value-------------------/   /------|
     |             | |                            \   \      |
    |-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-/   /-|-|-|-|
                                                  \   \
    '''

    state_t = enum('CYCLE_NONE', 'CYCLE_ONE', 'CYCLE_N', 'CYCLE')

    state_reg = Signal(state_t.CYCLE_NONE)
    state_next = Signal(state_t.CYCLE_NONE)
    count_reg = Signal(intbv(0)[spec.width_value-1:0])
    count_next = Signal(intbv(0)[spec.width_value-1:0])
    countdown_reg = Signal(intbv(0)[spec.width_value-1:0])
    countdown_next = Signal(intbv(0)[spec.width_value-1:0])

    clk_en_reg = Signal(False)
    clk_en_next = Signal(False)

    cmd_message = rx_fifo_dout
    cmd_opcode = Signal(intbv(0)[spec.width_opcode-1:0])
    cmd_addr = Signal(intbv(0)[spec.width_addr-1:0])
    cmd_data = Signal(intbv(0)[spec.width_data-1:0])
    cmd_value = Signal(intbv(0)[spec.width_value-1:0])

    response = Signal(intbv(0)[spec.width_message-1:0])

    @always_comb
    def split_cmd():
        cmd_opcode.next = cmd_message[spec.index_opcode_high+1:
                spec.index_opcode_low]
        cmd_addr.next = cmd_message[spec.index_addr_high+1:
                spec.index_addr_low]
        cmd_data.next = cmd_message[spec.index_data_high+1:
                spec.index_data_low]
        cmd_value.next = cmd_message[spec.index_value_high+1:
                spec.index_value_low]

    @always_comb
    def rx_fifo_output_logic():
        '''
        Drives the rx_fifo_dequeue signal
        '''
        if rx_fifo_empty:
            rx_fifo_dequeue.next = False
        elif tx_fifo_full:
            rx_fifo_dequeue.next = False
        else:
            rx_fifo_dequeue.next = True

    @always_comb
    def tx_fifo_output_logic():
        '''
        Drives the tx_fifo_din and tx_fifo_enqueue signal
        '''
        if cmd_opcode == spec.opcode_cmd_read:
            response.next[spec.index_opcode_high+1:spec.index_opcode_low] = \
                    spec.opcode_res_read_success
            response.next[spec.index_addr_high+1:spec.index_addr_low] = \
                    cmd_addr
            response.next[spec.index_data_high+1:spec.index_data_low] = \
                    exp_dout

#        elif cmd_opcode == OPCODE_CMD_WRITE:
#            response.next[index_opcode_high:index_opcode_low] = \
#                    OPCODE_RES_WRITE_SUCCESS
#            response.next[index_addr_high:index_addr_low] = cmd_addr
#            response.next[index_data_high:index_data_low] = exp_dout
#
#        elif cmd_opcode == OPCODE_CMD_RESET:
#            response.next[index_opcode_high:index_opcode_low] = \
#                    OPCODE_RES_RESET_SUCCESS
#            response.next[index_value_high:index_value_low] = 0
#
#        elif cmd_opcode == CMD_STEP:
#            response.next[index_opcode_high:index_opcode_low] = \
#                    OPCODE_RES_STEP_SUCCESS
#            response.next[index_value_high:index_value_low] = 0
#
#        elif cmd_opcode == CMD_START:
#            response.next[index_opcode_high:index_opcode_low] = \
#                    OPCODE_RES_START_SUCCESS
#            response.next[index_value_high:index_value_low] = 0
#
#        elif cmd_opcode == CMD_PAUSE:
#            response.next[index_opcode_high:index_opcode_low] = \
#                    OPCODE_RES_PAUSE_SUCCESS
#            response.next[index_value_high:index_value_low] = 0
#
#        elif cmd_opcode == CMD_STATUS:
#            response.next[index_opcode_high:index_opcode_low] = \
#                    OPCODE_RES_STATUS
#            response.next[index_value_high:index_value_low] = 0

    return split_cmd, tx_fifo_output_logic

