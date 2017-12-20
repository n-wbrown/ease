import asyncio 




class scan_sequence:
    """
    scan_sequence is a base class for monitoring programs.

    This class lays out the basic tools for a repeated, time-regulated
    process that can be cancelled and altered asynchronously 
    """
    def __init__(self,delay=0):
        self.delay = delay
        self.queue = asyncio.Queue()


    async def operation(self):
        """
        operation is intended to be overwritten in submodules. This is the
        repeated method evoked by regulator
        """
        raise NotImplementedError

    async def regulator(self,future):
        """
        regulator schedules the regular calls to the operation method and
        listens for interruptions.
        """
        running = set()
        done = set()
        while True:
            """
            try:
                message = self.queue.get_nowait()
            except asyncio.QueueEmpty:
                message = None
            """
            
            done = set()
            running = set()
            try:
                message = self.queue.get_nowait() 
            except asyncio.QueueEmpty:
                message = None
            if not message:
                done, running = await asyncio.wait(
                    [self.queue.get(),asyncio.sleep(self.delay)],
                    return_when = asyncio.FIRST_COMPLETED
                )
            for r in running:
                r.cancel()

            #done should be a single length set
            result = done.pop()
            if result.result() == "end":
                future.set_result("done")
                break
            
            await self.operation()
