#!/usr/bin/env python3
import os
import sys
import re

def shell_prompt():
    return os.environ.get('PS1', '$ ')#shell prompt PS1 or $ 

def fork_and_execute(command, args):
    pid = os.fork()
    
    if pid < 0:  # The fork failed
        os.write(2, f"Fork has failed with error code:  {pid}\n".encode())
        sys.exit(1)
        
    elif pid == 0:  # The child process
        for dir in os.environ['PATH'].split(':'):
            program = "%s/%s" % (dir, command)  #string formatting
            try:
                os.execve(program, [command] + args, os.environ)
            except FileNotFoundError:
                pass  
        os.write(2, f"{command}: command not found\n".encode())
        sys._exit(1)
        
    else:  #The parent process
        childPidCode = os.wait()
        if childPidCode[1] != 0:  
            os.write(2, f"Program terminated with exit code: {childPidCode[1] >> 8}.\n".encode())#Shift right by 8 bits to get the actual exit code
        return childPidCode[1]

def main():
    while True:
        os.write(1, shell_prompt().encode())
        user_input = sys.stdin.readline()
        
        if not user_input:
            sys.exit(0)
            
        user_input = user_input.strip()
        if not user_input:
            continue
            
        parts = user_input.split()
        command = parts[0]
        args = parts[1:]
        
        if command == "cd":#cd command functionality
            try:
                if args:
                    target_directory = args[0]#use the first one as the target directory
                else:
                    target_directory = os.environ['HOME']#otherwise use HOME ENV
                os.chdir(target_directory)# Change to the target directory
            except Exception as e:
                os.write(2, f"cd: {str(e)}\n".encode())
            continue
    
        if command == "exit":
            sys.exit(0)
            
        fork_and_execute(command, args)

if __name__ == "__main__":
    main()