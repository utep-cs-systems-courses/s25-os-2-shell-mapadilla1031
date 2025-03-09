#!/usr/bin/env python3
import os
import sys
import re

def shell_prompt():
    return os.environ.get('PS1', '$ ')  # shell prompt PS1 or $ 

def fork_and_execute(command, args):
    pid = os.fork()
    
    if pid < 0:  # The fork failed
        os.write(2, f"Fork has failed with error code:  {pid}\n".encode())
        sys.exit(1)
        
    elif pid == 0:  # The child process
        for dir in os.environ['PATH'].split(':'):
            program = "%s/%s" % (dir, command)  # formatting string correctly
            try:
                os.execve(program, [command] + args, os.environ)
            except FileNotFoundError:
                pass  
        os.write(2, f"{command}: command not found\n".encode())
        sys._exit(1)
        
    else:  # The parent process
        childPidCode = os.wait()
        if childPidCode[1] != 0:  
            os.write(2, f"Program terminated with exit code: {childPidCode[1] >> 8}.\n".encode())  # Shift right by 8 bits to get the actual exit code
        return childPidCode[1]

def do_a_pipe(first_command, second_command):
    # Create pipe
    pr, pw = os.pipe()
    for fd in (pr, pw):
        os.set_inheritable(fd, True)
    
    # Fork first child for first command
    pid1 = os.fork()
    
    if pid1 < 0:  # Fork failed
        os.write(2, b"Fork has failed\n")
        return
    
    elif pid1 == 0:  # First child - will execute first command
        # Redirect stdout to pipe write end
        os.close(1)                  # Close stdout
        os.dup2(pw, 1)               # Make pipe-write be stdout
        os.close(pr)                 # Close pipe-read
        os.close(pw)                 # Close original pipe-write
        
        # Parse and execute the first command
        parts = first_command.split()
        command = parts[0]
        args = parts[1:]
        
        # Execute the command
        for dir in os.environ['PATH'].split(':'):
            program = "%s/%s" % (dir, command)
            try:
                os.execve(program, [command] + args, os.environ)
            except FileNotFoundError:
                pass
        
        os.write(2, f"{command}: command not found\n".encode())
        sys._exit(1)
    
    # Fork second child for second command
    pid2 = os.fork()
    
    if pid2 < 0:  # Fork failed
        os.write(2, b"Forking has failed\n")
        return
    
    elif pid2 == 0:  # Second child - will execute second command
        # Redirect stdin from pipe read end
        os.close(0)                  # Close stdin
        os.dup2(pr, 0)               # Make pipe-read be stdin
        os.close(pr)                 # Close original pipe-read
        os.close(pw)                 # Close pipe-write
        
        
        parts = second_command.split()# Parse and execute the second command
        command = parts[0]
        args = parts[1:]
        
        # Execute the command
        for dir in os.environ['PATH'].split(':'):
            program = "%s/%s" % (dir, command)
            try:
                os.execve(program, [command] + args, os.environ)
            except FileNotFoundError:
                pass
        
        os.write(2, f"{command}: command not found\n".encode())
        sys._exit(1)
    
    # Parent process
    os.close(pr)                     # Close pipe-read
    os.close(pw)                     # Close pipe-write
    
    # Wait for both children to finish - this is crucial!
    childPidCode1 = os.wait()
    childPidCode2 = os.wait()
    
def main():
    while True:
        os.write(1, shell_prompt().encode())
        user_input = sys.stdin.readline()
        
        if not user_input:
            sys.exit(0)
            
        user_input = user_input.strip()
        if not user_input:
            continue
        
        if '|' in user_input:  # pipe if needed 
            pipe_commands = user_input.split('|', 1)
            do_a_pipe(pipe_commands[0].strip(), pipe_commands[1].strip())
            continue
            
        parts = user_input.split()
        command = parts[0]
        args = parts[1:]
        
        if command == "cd":  # cd here.
            try:
                if args:
                    target_directory = args[0]  # use the first one as the target directory
                else:
                    target_directory = os.environ['HOME']  # otherwise use HOME ENV
                os.chdir(target_directory)  # Change to the target directory
            except Exception as e:
                os.write(2, f"cd: {str(e)}\n".encode())
            continue
    
        if command == "exit":
            sys.exit(0)
            
        fork_and_execute(command, args)

if __name__ == "__main__":
    main()