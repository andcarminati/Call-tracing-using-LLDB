#!/usr/bin/env python

#----------------------------------------------------------------------
from __future__ import print_function

import lldb
import os
import shlex
import sys

code_to_count=dict()

if __name__ == '__main__':

    if(len(sys.argv) != 2):
        print('Simple program tracer')
        print('\tOnly one param neccessary, the program name or path!')
        sys.exit(-1)


    lldb.debugger = lldb.SBDebugger.Create()
    # Create a new debugger instance
    debugger = lldb.SBDebugger.Create()

    # Name of the executable as first and single param
    exe = sys.argv[1]

    # When we step or continue, don't return from the function until the process
    # stops. We do this by setting the async mode to false.
    debugger.SetAsync(False)

    # Create a target from a file and arch
    print("Creating a target for '%s': " % exe, end=' ')
    target = debugger.CreateTargetWithFileAndArch(exe, lldb.LLDB_ARCH_DEFAULT)

    if target:
        print('created!')

        module = target.GetModuleAtIndex(0)

        # For all symbols in the module
        for s in module:
            if s.GetType() == lldb.eSymbolTypeCode:
                # Add a breakpoint (except for the functions starting with dot)
                if(not s.GetName().startswith('.')):
                    bp = target.BreakpointCreateByName(s.GetName(), target.GetExecutable().GetFilename())
                    # Insert and entry in the map to track the number of calls
                    code_to_count[s.GetName()] = 0

        # Launch the process. Since we specified synchronous mode, we won't return
        # from this function until we hit a breakpoint
        process = target.LaunchSimple(None, None, os.getcwd())

        if process:
            thread = process.GetThreadAtIndex(0)
            # Interate while the process stops at a breakpoint
            while(process.GetState() == lldb.eStateStopped):
                frame = thread.GetFrameAtIndex(0)
                if frame:
                    # Take the function name
                    fname = frame.GetFunctionName()
                    if fname:
                        # We do have a function
                        # Check if we need to clear the name
                        if(fname.startswith('::') & fname.endswith('()')):
                            fname = fname[2:-2]
                        # Increment the counter in the map
                        code_to_count[fname] = code_to_count[fname]+1
                process.Continue()
        else:
            print('Proccess creation failure!')

    # Print all itens in the map
    for keys,values in code_to_count.items():
        print ('function %s : %s calls' % (keys, values))

    lldb.SBDebugger.Terminate()



