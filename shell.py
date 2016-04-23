import struct
import cmd, sys
import serial
from serial.tools.list_ports import comports
from fpgaedu import ControllerSpec

#BAUDRATE = 115200
BAUDRATE = 9600

class FpgaEduShell(cmd.Cmd):
    intro = 'Welcome to the fpgaedu shell'
    prompty = '(fpgaedu)'
    connection = None
    spec = ControllerSpec(32,8)

    def do_list_ports(self, arg):
        ports = comports()
        if len(ports) <= 0:
            print ('no com ports found on system')
        for port in ports:
            print(port.name)

    def postloop(self):
        self.do_disconnect()

    def do_connect(self, arg):
        try:
            self.connection = serial.Serial(arg, baudrate=BAUDRATE) 
            print('Started connection')
        except serial.SerialException:
            try:
                self.connection = serial.Serial('/dev/'+arg, baudrate=BAUDRATE)
            except serial.SerialException:
                print('Unable to open the specified port')

    def do_disconnect(self, arg):
        if self.connection is serial.Serial:
            self.connection.close()
            del self.connection

    def do_read(self, arg):
        self.write_addr_type_cmd(self.spec.opcode_cmd_read, 0, 0)
        self.read_res()

    def do_write(self, arg):
        pass

    def do_reset(self, arg):
        pass

    def do_step(self, arg):
        self.write_value_type_cmd(self.spec.opcode_cmd_step, 0)
        self.read_res()


    def do_start(self, arg):
        self.write_value_type_cmd(self.spec.opcode_cmd_start, 0)
        self.read_res()

    def do_pause(self, arg):
        self.write_value_type_cmd(self.spec.opcode_cmd_pause, 0)
        self.read_res()

    def do_status(self, arg):
        pass

    def write_addr_type_cmd(self, opcode, addr, data):
        cmd = struct.pack('>BBIBB', self.spec.chr_start, opcode,
                addr, data, self.spec.chr_stop)
        print(repr(cmd))
        self.connection.write(cmd)

    def write_value_type_cmd(self, opcode, value):
        cmd = struct.pack('>BBBIB', self.spec.chr_start, opcode, 0, value, self.spec.chr_stop)
        print(repr(cmd))
        self.connection.write(cmd)

    def read_res(self):
        if self.connection:
            self.connection.timeout = 1
            res = self.connection.read(99)
            print(repr(res))
        else:
            print('unable to read response: not connected')

def execute_cmd(cmd):
    spec = ControllerSpec(32,8)
    with serial.Serial('/dev/ttyUSB1', baudrate=BAUDRATE) as serial:
        cmd = struct.pack('>BBIBB', spec.chr_start, spec.opcode_cmd_start,
                0, 0, spec.chr_stop)
        #cmd = struct.pack('>BBIBBBB', spec.chr_start, spec.opcode_cmd_start,
        #        0, 0, spec.chr_stop, spec.chr_stop, spec.chr_stop)
        print(repr(cmd))
        serial.write(cmd)
        serial.timeout = 1
 
if __name__ == '__main__':
    FpgaEduShell().cmdloop()

