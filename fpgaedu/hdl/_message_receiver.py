from myhdl import (enum, always_comb, always_seq, Signal, intbv, always)

def MessageReceiver(spec, clk, reset, rx_fifo_data_read, rx_fifo_empty, 
        rx_fifo_dequeue, message, message_ready, receive_next):

    '''
    Input signals:
        clk
        reset
        rx_fifo_data_read
        rx_fifo_empty
        receive_next
    Output signals:
        rx_fifo_dequeue
        message
        message_ready
    '''

    state_t = enum('READ_START', 'READ_DATA', 'READ_STOP', 'READY')

    state_reg = Signal(state_t.READ_START)
    state_next = Signal(state_t.READ_START)
    esc_reg = Signal(False)
    esc_next = Signal(False)
    message_reg = Signal(intbv(0)[spec.width_message_bytes*8:0])
    message_next = Signal(intbv(0)[spec.width_message_bytes*8:0])
    byte_count_reg = Signal(intbv(0)[spec.width_message_bytes:0])
    byte_count_next = Signal(intbv(0)[spec.width_message_bytes:0])
    index_low = Signal(intbv(0, min=0, max=8*spec.width_message_bytes+1))

    @always_seq(clk.posedge, reset=reset)
    def register_logic():
        state_reg.next = state_next
        esc_reg.next = esc_next
        message_reg.next = message_next
        byte_count_reg.next = byte_count_next

    @always_comb
    def index_logic():
        index_low.next = 8*spec.width_message_bytes - byte_count_reg*8 -8

    @always_comb
    def next_state_logic():
        state_next.next = state_reg
        message_next.next = message_reg
        byte_count_next.next = byte_count_reg

        esc_next.next = not rx_fifo_empty and rx_fifo_data_read == spec.chr_esc

        if state_reg == state_t.READ_START:
            if rx_fifo_data_read == spec.chr_start and not rx_fifo_empty and \
                    not esc_reg:
                state_next.next = state_t.READ_DATA
        elif state_reg == state_t.READ_DATA:
            if not esc_reg and rx_fifo_data_read == spec.chr_start:
                byte_count_next.next = 0
            elif not esc_reg and rx_fifo_data_read == spec.chr_stop:
                byte_count_next.next = 0
                state_next.next = state_t.READ_START
            elif (not esc_reg and not rx_fifo_empty and rx_fifo_data_read != \
                    spec.chr_esc) or (esc_reg and not rx_fifo_empty):
                byte_count_next.next = (byte_count_reg + 1) % \
                        spec.width_message_bytes
                message_next.next[index_low+0] = rx_fifo_data_read[0]
                message_next.next[index_low+1] = rx_fifo_data_read[1]
                message_next.next[index_low+2] = rx_fifo_data_read[2]
                message_next.next[index_low+3] = rx_fifo_data_read[3]
                message_next.next[index_low+4] = rx_fifo_data_read[4]
                message_next.next[index_low+5] = rx_fifo_data_read[5]
                message_next.next[index_low+6] = rx_fifo_data_read[6]
                message_next.next[index_low+7] = rx_fifo_data_read[7]
                if byte_count_reg == spec.width_message_bytes-1:
                    state_next.next = state_t.READ_STOP
        elif state_reg == state_t.READ_STOP:
            if rx_fifo_data_read == spec.chr_stop and not rx_fifo_empty and \
                    not esc_reg:
                state_next.next = state_t.READY
        elif state_reg == state_t.READY:
            if receive_next:
                state_next.next = state_t.READ_START

    @always_comb
    def output_logic():
        message.next = message_reg[spec.width_message:0]
       
        message_ready.next = state_reg == state_t.READY

        if state_reg == state_t.READY: 
            rx_fifo_dequeue.next = False
        else:
            rx_fifo_dequeue.next = not rx_fifo_empty

    return register_logic, next_state_logic, output_logic, index_logic

