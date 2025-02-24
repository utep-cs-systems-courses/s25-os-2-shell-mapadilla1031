#!/usr/bin/env python3
import os
import sys
import re

def shell_prompt():
    return "$ "

def fork_and_execute(command, args):
    pid = os.fork()
    
    if pid < 0:  # if pid < 0, fork failed
        os.write(2, ("The fork failed, returning %d\n" % pid).encode())
        sys.exit(1)
        
    elif pid == 0:  # if pid = 0, Child process
        path = "/usr/local/bin:/usr/bin:/bin"
        
        for dir in re.split(":", path):
            program = "%s/%s" % (dir, command)#run command in each directory path
            try:
                os.execve(program, [command] + args, os.environ)
            except FileNotFoundError:
                pass
                
        os.write(2, f"{command}: The command was not found\n".encode())
        sys._exit(1)
        
    else:  
        return os.wait()#return to parent process

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

        if command == "exit":
            sys.exit(0)
            
        fork_and_execute(command, args)
if __name__ == "__main__":
    main()