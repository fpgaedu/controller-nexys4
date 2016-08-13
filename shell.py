#!/usr/bin/env python3

import struct
import cmd, sys
import serial
from serial.tools.list_ports import comports
from fpgaedu import ControllerSpec
import argparse

#BAUDRATE = 115200
BAUDRATE = 9600

class FpgaEduArgumentError(Exception):
    pass

class FpgaEduArgumentParser(argparse.ArgumentParser):
    def error(self, message=None):
        self.print_usage()
        raise FpgaEduArgumentError()

class FpgaEduShell(cmd.Cmd):
    intro = 'Welcome to the fpgaedu shell'
    prompty = '(fpgaedu)'
    connection = None
    spec = ControllerSpec(1,8)

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
        readparser = FpgaEduArgumentParser()
        readparser.add_argument('addr', type=int)
        try:
            n = readparser.parse_args(arg.split())
        except FpgaEduArgumentError as err:
            return
        
        self.write_addr_type_cmd(self.spec.opcode_cmd_read, n.addr, 0)
        self.read_res()

    def do_write(self, arg):
        writeparser = FpgaEduArgumentParser()
        writeparser.add_argument('addr', type=int)
        writeparser.add_argument('data', type=int)
        try:
            n = writeparser.parse_args(arg.split())
        except FpgaEduArgumentError as err:
            return
        
        self.write_addr_type_cmd(self.spec.opcode_cmd_write, n.addr, n.data)
        self.read_res()

        pass

    def do_reset(self, arg):
        self.write_value_type_cmd(self.spec.opcode_cmd_reset, 0)
        self.read_res()

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
        self.write_value_type_cmd(self.spec.opcode_cmd_status, 0)
        self.read_res()

    def write_addr_type_cmd(self, opcode, addr, data):
        cmd = struct.pack('>BBIBB', self.spec.chr_start, opcode,
                addr, data, self.spec.chr_stop)
        print('sending address-type command')
        print(repr(cmd))
        self.connection.write(cmd)

    def write_value_type_cmd(self, opcode, value):
        cmd = struct.pack('>BBIBB', self.spec.chr_start, opcode, 0, value, self.spec.chr_stop)
        print('sending value-type command')
        print(repr(cmd))
        self.connection.write(cmd)

    def read_res(self):
        message = [None for i in range(6)]
        if self.connection:
            self.connection.timeout = 0.1
            esc = False
            message = bytes(0)
            

            #read start byte
            while True:
                res = self.connection.read(1)
                if not esc and res == bytes([self.spec.chr_start]):
                    break
                if not esc and res == bytes([self.spec.chr_esc]):
                    esc = True
                else:
                    esc = False
            #read message bytes
            while True:
                res = self.connection.read(1)
                if not esc and res == bytes([self.spec.chr_start]):
                    message = bytes(0) 
                elif not esc and res == bytes([self.spec.chr_stop]):
                    break
                else:
                    message += res

                if not esc and res == bytes([self.spec.chr_esc]):
                    esc = True
                else:
                    esc = False

            print(repr(message))

            opcode = int.from_bytes(message[0:1], byteorder='big')
            addr = int.from_bytes(message[1:5], byteorder='big')
            data = int.from_bytes(message[5:6], byteorder='big')
            value = int.from_bytes(message[1:6], byteorder='big')

            if opcode == self.spec.opcode_res_read_success:
                print('read success: addr=%s, data=%s' % (addr, data))
            elif opcode == self.spec.opcode_res_read_error_mode:
                print('read error: controller in autonomous mode')
            elif opcode == self.spec.opcode_res_write_success:
                print('write success: addr=%s, data=%s' % (addr, data))
            elif opcode == self.spec.opcode_res_write_error_mode:
                print('write error: controller in autonomous mode')
            elif opcode == self.spec.opcode_res_reset_success:
                print('reset success')
            elif opcode == self.spec.opcode_res_step_success:
                print('step success: cycle count=%s' % value)
            elif opcode == self.spec.opcode_res_step_error_mode:
                print('step error: controller in autonomous mode')
            elif opcode == self.spec.opcode_res_start_success:
                print('start success: cycle count at start=%s' % value)
            elif opcode == self.spec.opcode_res_start_error_mode:
                print('start error: already in autonomous mode')
            elif opcode == self.spec.opcode_res_pause_success:
                print('pause success: cycle_count=%s' % value)
            elif opcode == self.spec.opcode_res_pause_error_mode:
                print('pause error: already in manual mode')
            elif opcode == self.spec.opcode_res_status:
                print('status: cycle count=%s' % value)
        else:
            print('unable to read response: not connected')


 
if __name__ == '__main__':
    FpgaEduShell().cmdloop()

