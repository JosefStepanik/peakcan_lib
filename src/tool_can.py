#!/usr/bin/env python3

# tool_can.py
# ~~~~~~~~~~~~
#
# Module with own function for communicating with CAN devices.
#
# ~~~~~~~~~~~~
#
# ------------------------------------------------------------------
# Author : Josef Stepanik
# Last change: 2023-09-23
#
# Language: Python 3
# ------------------------------------------------------------------
#
# Copyright (C) 2022-2023 IQS Group  
# Info at http://www.iqsgroup.cz
# 

from PCANBasic import *        ## PCAN-Basic library import
from loguru import logger
import time

class NewPCANBasic(PCANBasic):
    def __init__(self, PcanHandle=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.occupied = False
        self.sleeptime = 0.1
        self.PcanHandle = PcanHandle
        
    def create_can_msg(self, address, command):
        '''
        Create can message object.
        '''
        msgCanMessage = TPCANMsg()
        msgCanMessage.ID = address
        msgCanMessage.LEN = 8
        msgCanMessage.MSGTYPE = PCAN_MESSAGE_STANDARD.value
        for i in range(8):
            msgCanMessage.DATA[i] = command[i]
        return msgCanMessage
        
    def write_message(self, address, command):
        """
        Function for writing messages on CAN devices
    
        Returns:
            A TPCANStatus error code
        """
        ## Sends a CAN message with extended ID, and 8 data bytes
        
        timeout = 3  # Timeout in seconds
        start_time = time.time()

        try:
            result = None
            while self.occupied:
                if time.time() - start_time >= timeout:
                    logger.debug('Timeout: Unable to acquire CAN device.')
                    return None
                logger.debug('Wait for release CAN device.')
                time.sleep(self.sleeptime)
            self.occupied = True
            self.Reset(self.PcanHandle)
            command_message = self.create_can_msg(address, command)
            result = self.Write(self.PcanHandle, command_message)
            if PCAN_ERROR_OK == result:
                self.occupied = False
                logger.info('Write command {} with ID {} was successfull.'.format(self.get_data_string(command_message.DATA, command_message.MSGTYPE), address))
            else:
                logger.error('Write command {} with ID {} was not successfull.'.format(self.get_data_string(command_message.DATA, command_message.MSGTYPE), address))
                raise Exception('Write command was not successfull.')
        except Exception as err:
            logger.error("Write command was with error: {}!".format(err))
        finally:
            self.occupied = False
        return result
    
    def read_messages(self):
        """
        Function for reading PCAN-Basic messages
        
        Returns:
            A tuple variable response
        """
        result = PCAN_ERROR_OK
    
        # We read at least one time the queue looking for messages. If a message is found, we look again trying to find more. If the queue is empty or an error occurr, we get out from the while statement.
        while (not (result & PCAN_ERROR_QRCVEMPTY)):
            response = self.read_message(self.PcanHandle)
            result = response[0]
            if result != PCAN_ERROR_OK and result != PCAN_ERROR_QRCVEMPTY:
                self.show_status(result)
        return response
    
    def read_message(self):
        """
        Function for reading CAN messages on normal CAN devices
    
        Returns:
            A TPCANStatus error code
        """
        timeout = 3  # Timeout in seconds
        start_time = time.time()
        try:
            while self.occupied:
                if time.time() - start_time >= timeout:
                    logger.debug('Timeout: Unable to acquire CAN device.')
                    return None
                time.sleep(self.sleeptime)
            self.occupied = True
            result = self.Read(self.PcanHandle)
            if result[0] == PCAN_ERROR_OK:
                self.occupied = False
        except Exception as err:
            logger.error("Read command was with error: {}!".format(err))
            raise
        finally:
            self.occupied = False
        return result
    
    ## Sent command and read response 
    def write_read(self, address, command):
        result = None
        while self.occupied:
            logger.debug('Wait for release CAN device.')
            time.sleep(self.sleeptime)
        self.occupied = True
        try:
            self.Reset(self.PcanHandle)
            command_message = self.create_can_msg(address, command)
            if PCAN_ERROR_OK == self.Write(self.PcanHandle, command_message):
                logger.debug("Command {} sent with ID {}.".format(self.get_data_string(command_message.DATA, command_message.MSGTYPE), address))
                time.sleep(self.sleeptime)
                result = self.Read(self.PcanHandle)
                logger.debug("Response for command {} is {}.".format(self.get_data_string(command_message.DATA, command_message.MSGTYPE), self.get_data_string(result[1].DATA, result[1].MSGTYPE)))
        except Exception as err:
            logger.error("Write/read command was with error: {}!".format(err))
            raise
        finally:
            self.occupied = False
        return result

    def show_status(self, status):
        """
        Shows formatted status
    
        Parameters:
            status = Will be formatted
        """
        print("=====================================================================================")
        print(self.get_formatted_error(status))
        print("=====================================================================================")
    
    def format_channel_name(self, handle):
        """
        Gets the formated text for a PCAN-Basic channel handle
    
        Parameters:
            handle = PCAN-Basic Handle to format
    
        Returns:
            The formatted text for a channel
        """
        handleValue = handle.value
        if handleValue < 0x100:
            devDevice = TPCANDevice(handleValue >> 4)
            byChannel = handleValue & 0xF
        else:
            devDevice = TPCANDevice(handleValue >> 8)
            byChannel = handleValue & 0xFF
    
        return ('%s %s (%.2Xh)' % (self.get_device_name(devDevice.value),byChannel,handleValue))
    
    def get_formatted_error(self, error):
        """
        Help Function used to get an error as text
    
        Parameters:
            error = Error code to be translated
    
        Returns:
            A text with the translated error
        """
        ## Gets the text using the GetErrorText API function. If the function success translated error is returned.
        ## If it fails, a text describing the current error is returned.
        stsReturn = self.GetErrorText(error,0x09)
        if stsReturn[0] != PCAN_ERROR_OK:
            return "An error occurred. Error-code's text ({0:X}hcouldn'tberetrieved".format(error)
        else:
            message = str(stsReturn[1])
            return message.replace("'","",2).replace("b","",1)
        
    def get_data_string(self, data, msgtype):
        """
        Gets the data of a CAN message as a string
    
        Parameters:
            data = Array of bytes containing the data to parse
            msgtype = Type flags of the message the data belong
    
        Returns:
            A string with hexadecimal formatted data bytes of a CAN message
        """
        if (msgtype & PCAN_MESSAGE_RTR.value) == PCAN_MESSAGE_RTR.value:
            return "Remote Request"
        else:
            strTemp = "["
            for x in data:
                strTemp += '%.2X ' % x
            strTemp = strTemp[:-1] + ']'    
            return strTemp
        
    def process_message_can(self, msg, itstimestamp):
        """
        Processes a received CAN message
        
        Parameters:
            msg = The received PCAN-Basic CAN message
            itstimestamp = Timestamp of the message as TPCANTimestamp structure
        """
        microsTimeStamp = itstimestamp.micros + 1000 * itstimestamp.millis+0x10000000 * 1000 *  itstimestamp.millis_overflow
        
        print("Type: " + self.get_type_string(msg.MSGTYPE))
        print("ID: " + self.get_id_string(msg.ID, msg.MSGTYPE))
        print("Length: " + str(msg.LEN))
        print("Time: " + self.get_time_string(microsTimeStamp))
        print("Data: " + self.get_data_string(msg.DATA,msg.MSGTYPE))
        print("----------------------------------------------------------")
    
    def get_id_string(self, id, msgtype):
        """
        Gets the string representation of the ID of a CAN message
    
        Parameters:
            id = Id to be parsed
            msgtype = Type flags of the message the Id belong
    
        Returns:
            Hexadecimal representation of the ID of a CAN message
        """
        if (msgtype & PCAN_MESSAGE_EXTENDED.value) == PCAN_MESSAGE_EXTENDED.value:
            return '%.2X' %id
        else:
            return '%.3Xh' %id
    
    def get_time_string(self, time):
        """
        Gets the string representation of the timestamp of a CAN message,inmilliseconds
    
        Parameters:
            time = Timestamp in microseconds
    
        Returns:
            String representing the timestamp in milliseconds
        """
        fTime = time / 1000.0
        return '%.1f' %fTime
    
    def get_type_string(self, msgtype):  
        """
        Gets the string representation of the type of a CAN message
    
        Parameters:
            msgtype = Type of a CAN message
    
        Returns:
            The type of the CAN message as string
        """
        if (msgtype & PCAN_MESSAGE_STATUS.value) == PCAN_MESSAGE_STATUS.value:
            return 'STATUS'
        
        if (msgtype & PCAN_MESSAGE_ERRFRAME.value) == PCAN_MESSAGE_ERRFRAME.value:
            return 'ERROR'        
        
        if (msgtype & PCAN_MESSAGE_EXTENDED.value) == PCAN_MESSAGE_EXTENDED.value:
            strTemp = 'EXT'
        else:
            strTemp = 'STD'
    
        if (msgtype & PCAN_MESSAGE_RTR.value) == PCAN_MESSAGE_RTR.value:
            strTemp += '/RTR'
        else:
            if (msgtype > PCAN_MESSAGE_EXTENDED.value):
                strTemp += ' ['
                if (msgtype & PCAN_MESSAGE_FD.value) == PCAN_MESSAGE_FD.value:
                    strTemp += ' FD'
                if (msgtype & PCAN_MESSAGE_BRS.value) == PCAN_MESSAGE_BRS.value:                
                    strTemp += ' BRS'
                if (msgtype & PCAN_MESSAGE_ESI.value) == PCAN_MESSAGE_ESI.value:
                    strTemp += ' ESI'
                strTemp += ' ]'
                
        return strTemp
    
    def show_current_configuration(self):
            """
            Shows/prints the configured paramters
            """
            print("Parameter values used")
            print("----------------------")
            print("* PCANHandle: " + self.format_channel_name(self.self.PcanHandle))
            print("* Bitrate: " + self.convert_bitrate_to_string(self.bitrate))
            print("")
    
    def get_device_name(self, handle):
        """
        Gets the name of a PCAN device
    
        Parameters:
            handle = PCAN-Basic Handle for getting the name
    
        Returns:
            The name of the handle
        """
        switcher = {
            PCAN_NONEBUS.value: "PCAN_NONEBUS",
            PCAN_PEAKCAN.value: "PCAN_PEAKCAN",
            PCAN_DNG.value: "PCAN_DNG",
            PCAN_PCI.value: "PCAN_PCI",
            PCAN_USB.value: "PCAN_USB",
            PCAN_VIRTUAL.value: "PCAN_VIRTUAL",
            PCAN_LAN.value: "PCAN_LAN"
        }
    
        return switcher.get(handle,"UNKNOWN")