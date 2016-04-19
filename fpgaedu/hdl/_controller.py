from myhdl import always, always_seq, always_comb, enum, Signal, intbv

from fpgaedu import ControllerSpec
from fpgaedu.hdl._controller_control import ControllerControl
from fpgaedu.hdl._controller_cycle_control import ControllerCycleControl
from fpgaedu.hdl._controller_response_compose import ControllerResponseCompose

def Controller(spec, clk, reset, rx_msg, rx_next, rx_ready, tx_msg, tx_next, 
        tx_ready, exp_addr, exp_data_write, exp_data_read, exp_wen, exp_reset, 
        exp_clk_en, exp_reset_active=False):
    '''
    spec
        the controller specification
    clk
        Clock input
    reset
        Reset input
    rx_*
        rx_signals
    tx_*
        tx signals
    exp_addr
        Output signal setting the address for the experiment to be operated on
    exp_data_write
        Output signal setting the value to write to the experiment 
    exp_data_read
        Input signal containing the data that is read from the experiment
    exp_wen
        Output pulse signal indicating to the experiment that the current 
        operation is a write operation
    exp_reset
        Output signal indicating to the experiment that it is to be reset to 
        its initial state
    exp_clk_en
        Output clock enable signal for the experiment

    '''

    # Pipeline registers
    ex_res_opcode_res_reg = Signal(intbv(0)[spec.width_opcode:0])
    ex_res_opcode_res_next = Signal(intbv(0)[spec.width_opcode:0])
    ex_res_nop_reg = Signal(True)
    ex_res_nop_next = Signal(True)
    ex_res_cycle_count_reg = Signal(intbv(0)[spec.width_value:0])
    ex_res_cycle_count_next = Signal(intbv(0)[spec.width_value:0])
    ex_res_addr_reg = Signal(intbv(0)[spec.width_addr:0])
    ex_res_addr_next = Signal(intbv(0)[spec.width_addr:0])

    #internal signals
    cycle_autonomous = Signal(False)
    cycle_start = Signal(False)
    cycle_pause = Signal(False)
    cycle_step = Signal(False)
    
    cmd_message = rx_msg
    cmd_opcode = Signal(intbv(0)[spec.width_opcode-1:0])
    cmd_addr = Signal(intbv(0)[spec.width_addr-1:0])
    cmd_data = Signal(intbv(0)[spec.width_data-1:0])

    # EX stage instances
    control = ControllerControl(spec=spec, opcode_cmd=cmd_opcode, reset=reset,
            opcode_res=ex_res_opcode_res_next, rx_ready=rx_ready,
            cycle_autonomous=cycle_autonomous, rx_next=rx_next,
            tx_ready=tx_ready, nop=ex_res_nop_next,
            exp_wen=exp_wen, exp_reset=exp_reset, cycle_start=cycle_start, 
            cycle_pause=cycle_pause, cycle_step=cycle_step,
            exp_reset_active=exp_reset_active)

    cycle_control = ControllerCycleControl(spec=spec, clk=clk, reset=reset,
            start=cycle_start, pause=cycle_pause, step=cycle_step, 
            cycle_autonomous=cycle_autonomous, 
            cycle_count=ex_res_cycle_count_next, exp_clk_en=exp_clk_en)

    # RES stage instances
    res_compose = ControllerResponseCompose(spec=spec, 
            opcode_res=ex_res_opcode_res_reg,
            addr=ex_res_addr_reg, data=exp_data_read,
            nop=ex_res_nop_reg, cycle_count=ex_res_cycle_count_reg,
            tx_ready=tx_ready, tx_next=tx_next, tx_msg=tx_msg)

    @always_seq(clk.posedge, reset)
    def pipeline_register_logic():
        ex_res_opcode_res_reg.next = ex_res_opcode_res_next
        ex_res_nop_reg.next = ex_res_nop_next
        ex_res_cycle_count_reg.next = ex_res_cycle_count_next
        ex_res_addr_reg.next = ex_res_addr_next

    @always_comb
    def pipeline_next_state_logic():
        ex_res_addr_next.next = cmd_addr

    @always_comb
    def experiment_setup_connections():
        exp_addr.next = cmd_addr
        exp_data_write.next = cmd_data

    @always_comb
    def split_cmd():
        cmd_opcode.next = cmd_message[spec.index_opcode_high+1:
                spec.index_opcode_low]
        cmd_addr.next = cmd_message[spec.index_addr_high+1:
                spec.index_addr_low]
        cmd_data.next = cmd_message[spec.index_data_high+1:
                spec.index_data_low]

    return (control, cycle_control, res_compose, split_cmd, 
            experiment_setup_connections, pipeline_register_logic, 
            pipeline_next_state_logic)


