import asyncio 
import logging
from .engine_messages import ScanSeqMsg, update_msg, end_msg 

logger = logging.getLogger(__name__)
#logger.propagate = False

class ScanSequence:
    """
    ScanSequence is a base class for monitoring programs.

    This class lays out the basic tools for a repeated, time-regulated
    process that can be cancelled and altered asynchronously. This class is
    single threaded but its dependence on the asyncio libraries means that
    multiple instances of this class or subclasses can be run concurrently,
    CPU resources permitting. 

    The methods :func:`~engine_tools.engine_base.ScanSequence.start`,
    :func:`~engine_tools.engine_base.ScanSequence.end`, and 
    :func:`~engine_tools.engine_base.ScanSequence.send` are the recommended
    methods for controlling instances of this class. 
    
    Parameters
    ----------
    delay : float, optional
        specify a delay time between executions of the operation
            
    Attributes
    ----------
    delay : float
        This specifies the time between executions of the operation. 
    
    queue : asyncio.Queue()
        Queue of messages for the ScanSequence. Adding entries interrupts the
        waiting time and can prompt execution or termination depending on the
        message. The shortcut method 
        :func:`~engine_tools.engine_base.ScanSequence.send`

    persist : bool
        If true, continue to seek input or timeouts. False causes the regulator
        to terminate. 
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
        This should be overwritten in child classes. This is the method repeatedly
        evoked by :func:`~engine_tools.engine_base.ScanSequence.regulator`.
        """
        raise NotImplementedError
    
    async def wait_next(self):
        """
        block until either the delay time has been reached or a message has
        been received in the queue. 

        Returns
        -------
        message, None
            Data placed in the queue causing wait_next to return. If wait_next
            times out, None is returned.
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
        """
        This should be overwritten in child classes. Generates the message to
        be returned from wait_next if it completes due to a timeout. 
        
        Returns
        -------
        None
            By default, None is returned for timeout completion of 
            :func:`~engine_tools.engine_base.ScanSequence.wait_next`.
        """
        return None

    def end_message(self):
        """
        This should be overwritten in child classes. Generates the message to
        be sent when by the :func:`~engine_tools.engine_base.ScanSequence.end`.
        
        Returns
        -------
        str
            The end code returned is 'end', stored in
            :attr:`~engine_tools.engine_base.ScanSequence.end_code`
        """
        return self.end_code

    def send(self,message):
        """
        Shortcut method for placing messages in the queue.
        """
        return self.queue.put(message)

    async def update(self,message):
        """
        This should be overwritten in child classes. This operation is to be
        repeatedly carried out during normal operation. Raises a
        NotImplementedError if it has not been overwritten. 
        """
        raise NotImplementedError

    async def message_handler(self,message):
        """
        Contains decision making logic for handling messages. Strongly consider
        overwriting this method in child classes.
        
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
        """
        User friendly method for starting the regulator.

        Returns
        -------
        asyncio.task
            This is the task for the regulator process. 
        """
        logger.debug(self.queue.qsize())
        task = asyncio.ensure_future(self.regulator())
        return task

    async def end(self):
        """
        User friendly cancel method for cleanly terminating the regulator
        process.
        """
        await self.send(self.end_message())

    async def regulator(self,run_at_start=True):
        """
        The regulator schedules the regular calls to the operation method and
        listens for interruptions.
        
        Regulator is the core method of ScanSequence. This schedules the
        execution of the 
        :func:`~engine_tools.engine_base.ScanSequence.message_handler` 
        depending on input or timeouts from the queue. During
        normal operation, message_handler() is  run periodically. Messages 
        placed in the queue can interrupt this to prompt
        operations such as the operation running instantly or terminating. 

        Parameters
        ----------
        run_at_start : bool
            If true, run the message handler once prior to checking for queue
            messages or awaiting a timeout. 
            
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

class MsgScanSequence(ScanSequence):
    """
    MsgScanSequence is a child class of ScanSequence built for compatibility
    with the message class contained in
    :class:`~engine_tools.engine_messages.ScanSeqMsg`


    The methods :func:`~engine_tools.engine_base.ScanSequence.start`,
    :func:`~engine_tools.engine_base.ScanSequence.end`, and 
    :func:`~engine_tools.engine_base.ScanSequence.send` are the recommended
    methods for controlling instances of this class. 
    """
    async def message_handler(self,message):
        """
        Contains decision making logic for handling messages
        
        Parameters
        ----------
        message
            Variable of any type to be handled 
        """
        logger.debug("starting message_handler")
        if type(message) != ScanSeqMsg:
            print("TYPE:", type(message), "MESSAGE",message)

        if message.end:
            self.persist = False

        logger.debug("reached op if")
        if message.update:
            logger.debug("evoking op")
            logger.debug(str(self.operation))
            await self.operation()

    def timeout_message(self):
        """
        Generates the message to
        be returned from wait_next if it completes due to a timeout. 
        
        Returns
        -------
        :class:`~engine_tools.engine_messages.ScanSeqMsg`
            Return an update instance.

        """
        return update_msg()
   
    def end_message(self):
        """
        Generates the message to
        be sent when by the :func:`~engine_tools.engine_base.ScanSequence.end`.
        
        Returns
        -------
        :class:`~engine_tools.engine_messages.ScanSeqMsg`
            Return an end instance.
        """
        return end_msg()
