import asyncio 
import logging
from .engine_messages import scan_seq_msg 

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
            message = None
        
        return message

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
        message_identified = False

        if message == self.end_code:
            message_identified = True
            self.persist = False

        logger.debug("reached op if")
        if message == None:
            message_identified = True
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
        await self.queue.put(self.end_code)

    async def regulator(self,run_at_start=True):
        """
        regulator schedules the regular calls to the operation method and
        listens for interruptions.
        """
        running = set()
        done = set()
        if run_at_start:
            await self.message_handler(None)

        while self.persist:
            logger.debug('running loop')
            message = await self.wait_next()
            logger.debug('in-loop message:'+str(message))
            await self.message_handler(message)
