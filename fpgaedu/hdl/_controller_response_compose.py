from myhdl import always_comb

def ControllerResponseCompose(spec, opcode_res, addr, data, nop, cycle_count,
        tx_ready, tx_next, tx_msg):
    '''
    opcode_res:
        input signal
    addr:
        input signal
    data:
        input signal
    nop:
        input signal
    tx_ready:
        input signal
    tx_next:
        output signal
    '''

    @always_comb
    def output_logic():
        tx_next.next = False
        tx_msg.next = 0

        if tx_ready and not nop:
            tx_next.next = True

        # set response opcode
        tx_msg.next[spec.index_opcode_high+1:spec.index_opcode_low] = \
                opcode_res

        if (opcode_res == spec.opcode_res_read_success or 
                opcode_res == spec.opcode_res_write_success):
            # addr-type response message
            tx_msg.next[spec.index_addr_high+1:spec.index_addr_low] = addr
            tx_msg.next[spec.index_data_high+1:spec.index_data_low] = data
        elif (opcode_res == spec.opcode_res_read_error_mode or 
                opcode_res == spec.opcode_res_write_error_mode):
            # addr-type response message
            tx_msg.next[spec.index_addr_high+1:spec.index_addr_low] = addr
            tx_msg.next[spec.index_data_high+1:spec.index_data_low] = 0
        elif (opcode_res == spec.opcode_res_step_success):
            tx_msg.next[spec.index_value_high+1:spec.index_value_low] = \
                    cycle_count + 1
        elif (opcode_res == spec.opcode_res_start_success or
                opcode_res == spec.opcode_res_pause_success or
                opcode_res == spec.opcode_res_status):
            tx_msg.next[spec.index_value_high+1:
                    spec.index_value_low] = cycle_count
        else:
            tx_msg.next[spec.index_value_high+1:
                    spec.index_value_low] = 0

    return output_logic
    
    
