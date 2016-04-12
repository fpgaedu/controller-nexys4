from myhdl import always_comb

def ControllerResponseCompose(spec, opcode_res, addr, data, nop, cycle_count,
        tx_fifo_full, tx_fifo_enqueue, tx_fifo_data_write):
    '''
    opcode_res:
        input signal
    addr:
        input signal
    data:
        input signal
    nop:
        input signal
    tx_fifo_full:
        input signal
    tx_fifo_enqueue:
        output signal
    tx_fifo_dequeue:
        output signal
    '''

    @always_comb
    def output_logic():
        tx_fifo_enqueue.next = False
        tx_fifo_data_write.next = 0

        if not tx_fifo_full and not nop:
            tx_fifo_enqueue.next = True

        # set response opcode
        tx_fifo_data_write.next[spec.index_opcode_high+1:
                spec.index_opcode_low] = opcode_res

        if (opcode_res == spec.opcode_res_read_success or 
                opcode_res == spec.opcode_res_write_success):
            # addr-type response message
            tx_fifo_data_write.next[spec.index_addr_high+1:
                    spec.index_addr_low] = addr
            tx_fifo_data_write.next[spec.index_data_high+1:
                    spec.index_data_low] = data
        elif (opcode_res == spec.opcode_res_read_error_mode or 
                opcode_res == spec.opcode_res_write_error_mode):
            # addr-type response message
            tx_fifo_data_write.next[spec.index_addr_high+1:
                    spec.index_addr_low] = addr
            tx_fifo_data_write.next[spec.index_data_high+1:
                    spec.index_data_low] = 0
        elif (opcode_res == spec.opcode_res_step_success):
            tx_fifo_data_write.next[spec.index_value_high+1:
                    spec.index_value_low] = cycle_count + 1
        elif (opcode_res == spec.opcode_res_start_success or
                opcode_res == spec.opcode_res_pause_success or
                opcode_res == spec.opcode_res_status):
            tx_fifo_data_write.next[spec.index_value_high+1:
                    spec.index_value_low] = cycle_count
        else:
            tx_fifo_data_write.next[spec.index_value_high+1:
                    spec.index_value_low] = 0

    return output_logic
    
    
