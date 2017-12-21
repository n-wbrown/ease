import asyncio 




class scan_sequence:
    """
    scan_sequence is a base class for monitoring programs.

    This class lays out the basic tools for a repeated, time-regulated
    process that can be cancelled and altered asynchronously 
    """
    end_code = "end"
    upd_code = "upd"
    end_msg = "done"
    '''
    def __new__(cls):
        #msg_maps = {None:cls.operation}
        return __new__(cls)
    '''
    def __init__(self,delay=0):
        self.delay = delay
        self.queue = asyncio.Queue()
        self.persist = True


    async def operation(self):
        """
        operation is intended to be overwritten in submodules. This is the
        repeated method evoked by regulator
        """
        raise NotImplementedError


    async def wait_next(self):
        """
        block until either the delay time has been reached or a message has
        been received in the queue. Return message or none 
        """ 
        # if the delay is 0, checking the q. will always take longer and so
        # must be manually checked 
        if not self.queue.empty():
            msg = True
            message = await self.queue.get()
        else:
            msg = False
        
        done = set()
        running = set()
        if not msg:
            done, running = await asyncio.wait(
                [self.queue.get(),asyncio.sleep(self.delay)],
                return_when = asyncio.FIRST_COMPLETED
            )
            completed = done.pop() 
            message = completed.result()

        #cleanly cancel which ever coro is still running (if any)
        for r in running:
            r.cancel()

        return message

    async def update(self,message):
        raise NotImplementedError


    async def message_handler(self,message):
        print("starting message_handler")
        if message == self.end_code:
            self.persist = False
        print("reached op if")
        if message == None:
            print("evoking op")
            print(self.operation)
            await self.operation()

    async def start(self):
        task = asyncio.ensure_future(self.regulator)
        return task

    async def cancel(self):
        self.queue.put(self.end_code)

    async def regulator(self):
        """
        regulator schedules the regular calls to the operation method and
        listens for interruptions.
        """
        running = set()
        done = set()
        while self.persist:
            print('running loop')
            message = await self.wait_next()
            print('in-loop message:',message)
            await self.message_handler(message)
