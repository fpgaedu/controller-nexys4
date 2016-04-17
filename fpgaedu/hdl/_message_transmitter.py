from myhdl import (enum, always_comb, always_seq, Signal, intbv, always)

def MessageTransmitter(spec, clk, reset, tx_fifo_data_write, tx_fifo_full, 
        tx_fifo_enqueue, message, ready, transmit_next):
    '''
    Input signals:
        clk
        reset
        message
        tx_fifo_full
        transmit_next
    Output signals:
        tx_fifo_data_write
        tx_fifo_enqueue
        ready
    '''

    state_t = enum('IDLE', 'TRANSMIT_START', 'TRANSMIT_STOP', 'TRANSMIT_DATA')
    
    state_reg = Signal(state_t.IDLE)
    state_next = Signal(state_t.IDLE)
    prev_esc_reg = Signal(False)
    prev_esc_next = Signal(False)
    message_reg = Signal(intbv(0)[spec.width_message_bytes*8:0])
    message_next = Signal(intbv(0)[spec.width_message_bytes*8:0])
    byte_count_reg = Signal(intbv(0)[spec.width_message_bytes:0])
    byte_count_next = Signal(intbv(0)[spec.width_message_bytes:0])
    
    dout = Signal(intbv(0)[8:0])
    esc = Signal(False)

    @always_seq(clk.posedge, reset=reset)
    def register_logic():
        state_reg.next = state_next
        prev_esc_reg.next = prev_esc_next
        message_reg.next = message_next
        byte_count_reg.next = byte_count_next

    @always_comb
    def next_state_logic():
        state_next.next = state_reg
        prev_esc_next.next = prev_esc_reg
        message_next.next = message_reg
        byte_count_next.next = byte_count_reg

        if state_reg == state_t.IDLE:
            if transmit_next:
                state_next.next = state_t.TRANSMIT_START
                message_next.next[8*spec.width_message_bytes:spec.width_message] = 0
                message_next.next[spec.width_message:0] = message
        elif state_reg == state_t.TRANSMIT_START:
            if not tx_fifo_full:
                byte_count_next.next = 0
                state_next.next = state_t.TRANSMIT_DATA
        elif state_reg == state_t.TRANSMIT_DATA:
            if not tx_fifo_full and esc and not prev_esc_reg:
                prev_esc_next.next = True
            elif not tx_fifo_full and (not esc or (esc and prev_esc_reg)):
                byte_count_next.next = (byte_count_reg+1) % \
                        spec.width_message_bytes
                prev_esc_next.next = False
                if byte_count_reg == spec.width_message_bytes - 1:
                    state_next.next = state_t.TRANSMIT_STOP
        elif state_reg == state_t.TRANSMIT_STOP:
            if not tx_fifo_full:
                state_next.next = state_t.IDLE

    @always_comb
    def dout_logic():
        index_high = 8*spec.width_message_bytes-byte_count_reg*8
        index_low = 8*spec.width_message_bytes-byte_count_reg*8-8
        dout.next = message_reg[index_high:index_low]
        
    @always_comb
    def esc_logic():
        esc.next = (dout == spec.chr_start or dout == spec.chr_esc or 
                dout == spec.chr_stop)

    @always_comb
    def output_logic():
        tx_fifo_enqueue.next = (state_reg != state_t.IDLE and not tx_fifo_full)
        ready.next = (state_reg == state_t.IDLE)

        if state_reg == state_t.IDLE:
            tx_fifo_data_write.next = 0
        elif state_reg == state_t.TRANSMIT_START:
            tx_fifo_data_write.next = spec.chr_start
        elif state_reg == state_t.TRANSMIT_DATA:
            if not esc or (esc and prev_esc_reg):
                tx_fifo_data_write.next = dout
            else:
                tx_fifo_data_write.next = spec.chr_esc
        elif state_reg == state_t.TRANSMIT_STOP:
            tx_fifo_data_write.next = spec.chr_stop

    return (register_logic, next_state_logic, output_logic, dout_logic, 
            esc_logic)

