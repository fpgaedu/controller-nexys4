from myhdl import (always_comb)

def ControllerControl(spec, opcode_cmd, opcode_res, rx_fifo_empty, 
        cycle_autonomous, rx_fifo_dequeue, 
        tx_fifo_full, nop, exp_wen):
    '''
    opcode_cmd:
        input signal
    opcode_res:
        output signal defining the output opcode
    rx_fifo_empty:
        intput signal
    rx_fifo_dequeue:
        output signal
    tx_fifo_full:
        input signal
    nop:
        output signal indicating that no operation is to be executed this cycle
    exp_wen:
        output signal for 
    '''
    
    @always_comb
    def output_logic():

        rx_fifo_dequeue.next = False
        nop.next = True
        exp_wen.next = False
        opcode_res.next = 0

        if not rx_fifo_empty and not tx_fifo_full:
            rx_fifo_dequeue.next = True
            nop.next = False
            if opcode_cmd == spec.opcode_cmd_write and not cycle_autonomous:
                exp_wen.next = True

        if opcode_cmd == spec.opcode_cmd_read and not cycle_autonomous:
            opcode_res.next = spec.opcode_res_read_success
        elif opcode_cmd == spec.opcode_cmd_read and cycle_autonomous:
            opcode_res.next = spec.opcode_res_read_error_mode
        elif opcode_cmd == spec.opcode_cmd_write and not cycle_autonomous:
            opcode_res.next = spec.opcode_res_write_success
        elif opcode_cmd == spec.opcode_cmd_write and cycle_autonomous:
            opcode_res.next = spec.opcode_res_write_error_mode
        elif opcode_cmd == spec.opcode_cmd_reset:
            opcode_res.next = spec.opcode_res_reset_success
        elif opcode_cmd == spec.opcode_cmd_step and not cycle_autonomous:
            opcode_res.next = spec.opcode_res_step_success
        elif opcode_cmd == spec.opcode_cmd_step and cycle_autonomous:
            opcode_res.next = spec.opcode_res_step_error_mode
        elif opcode_cmd == spec.opcode_cmd_start and not cycle_autonomous:
            opcode_res.next = spec.opcode_res_start_success
        elif opcode_cmd == spec.opcode_cmd_start and cycle_autonomous:
            opcode_res.next = spec.opcode_res_start_error_mode
        elif opcode_cmd == spec.opcode_cmd_pause and cycle_autonomous:
            opcode_res.next = spec.opcode_res_pause_success
        elif opcode_cmd == spec.opcode_cmd_pause and not cycle_autonomous:
            opcode_res.next = spec.opcode_res_pause_error_mode
        elif opcode_cmd == spec.opcode_cmd_status:
            opcode_res.next = spec.opcode_res_status

    return output_logic
