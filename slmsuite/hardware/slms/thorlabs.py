"""
subclass for Thorlab SLM hardware control in :mod:`slmsuite`.
Outlines which SLM superclass functions must be implemented.

@author Saroj B Chand

"""
import os
import ctypes
import warnings
import sys
import time
import numpy as np
import select
sys.path.append('c:/Users/Saroj Chand/Documents/dioptric/servers/inputs')
from slmsuite.hardware.slms.slm import SLM
from Thorlabs_EXULUS_PythonSDK.Thorlabs_EXULUS_Python_SDK.EXULUS_COMMAND_LIB import*
from Thorlabs_EXULUS_PythonSDK.Thorlabs_EXULUS_CGHDisplay.Thorlabs_EXULUS_CGHDisplay import*

DEFAULT_SDK_PATH = "C:/Users/Saroj Chand/Documents/dioptric/servers/inputs/Thorlabs_EXULUS_PythonSDK"


class ThorSLM(SLM):
    """
    Template for implementing a new SLM subclass. Replace :class:`Template`
    with the desired subclass name. :class:`~slmsuite.hardware.slms.slm.SLM` is the
    superclass that sets the requirements for :class:`Template`.
    """
    def __init__(self, serialNumber):
        """
        Initializes an instance of a Meadowlark SLM.

        Caution
        ~~~~~~~
        :class:`.Meadowlark` defaults to 8 micron SLM pixel size
        (:attr:`.SLM.dx_um` = :attr:`.SLM.dy_um` = 8).
        This is valid for most Meadowlark models, but not true for all!

        Arguments
        ---------
        verbose : bool
            Whether to print extra information.
        sdk_path : str
            Path of the Blink SDK folder. Stored in :attr:`sdk_path`.
        lut_path : str OR None
            Passed to :meth:`load_lut`.
        kwargs
            See :meth:`.SLM.__init__` for permissible options.
        """
        hdl = EXULUSOpen(serialNumber,38400,3)
        if(hdl < 0):
            print("Connect ",serialNumber, "fail")
            return -1
        else:
            print("Connect ",serialNumber, "successfully")

        result = EXULUSIsOpen(serialNumber)
        if(result < 0):
            print("Open failed ")
        else:
            print("EXULUS is open ")
        
        print("-----------------Get EXULUS device information----------------")

        code=[0]
        codeList={6:"Acknowledge", 9:"Not Acknowledge", 187:"SPI_Busy"}
        result = EXULUSCheckCommunication(hdl,code) 
        if(result < 0):
            print("Get device parameters failed ")
        else:
            print("Device parameters: ", codeList.get(code[0]))    
            

        # Check for the SLM parameters and save them
        width = 1920
        height = 1080
        # Instantiate the superclass
        super().__init__(
        width,
        height,
        bitdepth=8,
        dx_um=8,
        dy_um=8,
        )

        # Create SLM window
        self.hdl = CghDisplayCreateWindow(2, 1920, 1080, "SLM window")
        if self.hdl < 0:
            print("Create window failed")
            return -1
        else:
            print("SLM Window is Create and Current screen is 2")

        result = CghDisplaySetWindowInfo(self.hdl, 1920, 1080, 1)
        if result < 0:
            print("Set Window Info failed")
        else:
            print("Set Window Info successfully")
            
        # Show the window
        buffer_phase = None
        result = CghDisplayShowWindow(self.hdl,buffer_phase)
        if result < 0:
            print("Show failed")
        else:
            print("Show successfully")
        time.sleep(1)
        

    @staticmethod
    def info(verbose=True):
        """
        Discovers all SLMs detected by an SDK.
        Useful for a user to identify the correct serial numbers / etc.

        Parameters
        ----------
        verbose : bool
            Whether to print the discovered information.

        Returns
        --------
        list of str
            List of serial numbers or identifiers.
        """
        raise NotImplementedError()
        serial_list = get_serial_list()     # TODO: Fill in proper function.
        return serial_list
    
    def _write_hw(self, phase):
        """Low-level hardware interface to write ``phase`` data onto the SLM."""
        matrix = phase.astype(c_ubyte)
        flattened_matrix = matrix.flatten()
        c = ctypes.cast(flattened_matrix.ctypes.data, ctypes.POINTER(ctypes.c_ubyte))
        
        # Display the phase
        result = CghDisplayShowWindow(self.hdl,c)

        # if result < 0:
        #     print("Show failed")
        # else:
        #     print("Show successfully")
        time.sleep(1)

        # Ask before closing the SLM display
        # user_input = input("Press Enter to close SLM display... ")
        # if user_input:
        #     print("Window closing aborted by user")
        #     return -1

        # CghDisplayCloseWindow(hdl)
        # return 0

    def show_window(self, c):
        """Show window on SLM display."""
        return CghDisplayShowWindow(self.hdl, c)  

    def close_display(self):
        """Close SLM display."""
        if self.hdl:
            CghDisplayCloseWindow(self.hdl)

    def close_connection(self):
        """Close SLM connection."""
        if self.hdl:
            EXULUSClose(self.serialNumber)

        # TODO: Insert code here to write raw phase data to the SLM.