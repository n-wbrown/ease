import asyncio 
import logging
from .engine_messages import scan_seq_msg, update_msg, end_msg 

logger = logging.getLogger(__name__)
#logger.propagate = False

class scan_sequence:
    """
    scan_sequence is a base class for monitoring programs.

    This class lays out the basic tools for a repeated, time-regulated
    process that can be cancelled and altered asynchronously. This class is
    single threaded but its dependence on the asyncio libraries means that
    multiple insntances of this class or subclasses can be run together on a
    single thread, CPU resources permitting. 

    Attributes
    ----------
    delay : float, optional
        This specifies the time between executions of the operation. Can be 
    """
    
    end_code = "end"
    upd_code = "upd"
    end_msg = "done"
    
    def __init__(self,delay=0):
        """
        Parameters
        ----------
        delay : float, optional
            specify a delay time between executions of the operation
        """
        self.delay = delay
        self.queue = asyncio.Queue()
        self.persist = True


    async def operation(self):
        """
        This should be overwritten in submodules. This is the method repeatedly
        evoked by :func:`~engine_tools.engine_base.scan_sequence.regulator`.
        """
        raise NotImplementedError
    
    async def wait_next(self):
        """
        block until either the delay time has been reached or a message has
        been received in the queue. Return message or none 
        """ 
        message = None
        z = self.queue.qsize()
        qtask = asyncio.ensure_future(self.queue.get())
        
        try:
            await asyncio.wait_for(qtask,timeout=self.delay)
            message = qtask.result()
        except asyncio.TimeoutError:
            #message = None
            message = self.timeout_message()
        
        return message

    def timeout_message(self):
        return None

    def end_message(self):
        return self.end_code

    async def update(self,message):
        raise NotImplementedError

    async def message_handler(self,message):
        """
        Contains decision making logic for handling messages
        
        Parameters
        ----------
        message
            Variable of any type to be handled 
        """
        logger.debug("starting message_handler")

        if message == self.end_code:
            self.persist = False

        logger.debug("reached op if")
        if message == None:
            logger.debug("evoking op")
            logger.debug(str(self.operation))
            await self.operation()

    def start(self):
        logger.debug(self.queue.qsize())
        task = asyncio.ensure_future(self.regulator())
        return task

    async def end(self):
        """
        Soft cancel method for cleanly terminating 
        """
        await self.queue.put(self.end_message())

    async def regulator(self,run_at_start=True):
        """
        regulator schedules the regular calls to the operation method and
        listens for interruptions.
        """
        running = set()
        done = set()
        if run_at_start:
            await self.message_handler(self.timeout_message())

        while self.persist:
            logger.debug('running loop')
            message = await self.wait_next()
            logger.debug('in-loop message:'+str(message))
            await self.message_handler(message)

class MsgScanSequence(scan_sequence):
    async def message_handler(self,message):
        """
        Contains decision making logic for handling messages
        
        Parameters
        ----------
        message
            Variable of any type to be handled 
        """
        logger.debug("starting message_handler")
        if type(message) != scan_seq_msg:
            print("TYPE:", type(message), "MESSAGE",message)

        if message.end:
            self.persist = False

        logger.debug("reached op if")
        if message.update:
            logger.debug("evoking op")
            logger.debug(str(self.operation))
            await self.operation()

    def timeout_message(self):
        return update_msg()
   
    def end_message(self):
        return end_msg()
