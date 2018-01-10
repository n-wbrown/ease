import pytest
import asyncio
from engine_tools.engine_base import ScanSequence
from engine_tools.engine_messages import end_msg, update_msg
import logging 

logger = logging.getLogger(__name__)
#logger.propagate = False
def test_ScanSequence_init():
    """
    Ensure :class:`~engine_tools.engine_base.ScanSequence` can be
    instantiated without errors.
    """
    try:
        scanner = ScanSequence()
    except:
        pytest.fail("constructing new ScanSequence failed")

@pytest.mark.parametrize("msg", [1.2,{"abc":"def"},set([1,2,3])])
def test_ScanSequence_wait_next(msg):
    """
    Ensure :func:`~engine_tools.engine_base.ScanSequence.wait_next` can handle
    interruptions and timeouts

    This test is broken into three separate sections

    1. Ensure that uninterrupted delays can be handled properly 
    2. Ensure that interruption produces the desired message
    3. Ensure that interruption is viable even with no delay

    Test parameterization makes sue that the message content is type-agnostic.
    """
    scanner = ScanSequence()
    q = scanner.queue

    async def test_mgr():
        # ensure that delays timeout properly 
        scanner.delay = .1
        task = asyncio.ensure_future(scanner.wait_next())
        try:
            result = await asyncio.wait_for(task,timeout=.2)
        except asyncio.TimeoutError:
            pytest.fail("normal timeout took too long to complete")
        
        assert result == None, "normal timeout returned wrong value"

        #ensure that interruption is possible
        scanner.delay = 100
        task = asyncio.ensure_future(scanner.wait_next())
        await scanner.queue.put(msg)
        try:
            result = await asyncio.wait_for(task,timeout=.2)
        except asyncio.TimeoutError:
            pytest.fail("interruption test took too long to complete")

        assert result == msg, "interruption test returned wrong value"
        
        #ensure that interruption is possible even with 0 delay
        scanner.delay = 0
        await scanner.queue.put(msg)
        task = asyncio.ensure_future(scanner.wait_next())
        try:
            result = await asyncio.wait_for(task,timeout=.2)
        except asyncio.TimeoutError:
            pytest.fail("0-delay interruption test  took too long to complete")
        
        assert result == msg, ("0-delay interruption test returns wrong value")

    loop = asyncio.get_event_loop()    
    loop.run_until_complete(test_mgr())

def test_ScanSequence_regulator_repeated_operation(test_scan):
    """
    Ensure :func:`~engine_tools.engine_base.ScanSequence.regulator` properly
    organizes the run cycle by checking for input and scheduling the operation
    """
    
    scanner = test_scan()

    async def test_mgr():
        task = asyncio.ensure_future(scanner.regulator())
        await asyncio.sleep(.1)
        task.cancel()

    loop = asyncio.get_event_loop()
    loop.run_until_complete(test_mgr())
    logger.debug("final n: " +str(scanner.n))
    assert scanner.n > 0, "intended operation never ran"

@pytest.mark.parametrize("m", ([0]*9)+[.01,.02,.03,.04,.05,.1,.2,.3,.4])
def test_ScanSequence_regulator_termination(test_scan, m):
    """
    Ensure :func:`~engine_tools.engine_base.ScanSequence.regulator` properly
    terminates when the end code is sent.

    Parameterization tests various delay times. 0 Time delays have erred
    unreliably in some builds hence the redundant tests.
    """
    scanner = test_scan()
    scanner.delay = m


    async def test_mgr():
        task = asyncio.ensure_future(scanner.regulator())
        await asyncio.sleep(.01)
        #scanner.queue.put_nowait(scanner.end_code)
        await scanner.queue.put(scanner.end_code)
        logger.debug("put complete " + str(scanner.queue.qsize()))
        try:
            await asyncio.wait_for(task,timeout=.1)
        except asyncio.TimeoutError:
            pytest.fail("Failed to end")

    loop = asyncio.get_event_loop()
    loop.run_until_complete(test_mgr())
    assert scanner.n > 0, "intended operation has not run"
    
def test_ScanSequence_end(test_scan):
    """
    Ensure :func:`~engine_tools.engine_base.ScanSequence.end` properly
    terminates the regulator. 
    """
    scanner = test_scan()

    async def test_mgr():
        task = asyncio.ensure_future(scanner.regulator())
        await asyncio.sleep(.01)
        await scanner.end()
        try:
            await asyncio.wait_for(task,timeout=1)
        except asyncio.TimeoutError:
            pytest.fail("Failed to cancel")

    loop = asyncio.get_event_loop()
    loop.run_until_complete(test_mgr())
    assert scanner.n > 0, "intended operation has not run"

def test_ScanSequence_start(test_scan):
    """
    Ensure :func:`~engine_tools.engine_base.ScanSequence.start` properly
    initiates the regulator. 
    """
    scanner = test_scan()

    async def test_mgr():
        #task = asyncio.ensure_future(scanner.regulator())
        task = scanner.start()
        await asyncio.sleep(.01)
        await scanner.queue.put(scanner.end_code)
        try:
            await asyncio.wait_for(task,timeout=1)
        except asyncio.TimeoutError:
            pytest.fail("Failed to end")
    
    loop = asyncio.get_event_loop()
    loop.run_until_complete(test_mgr())
    assert scanner.n > 0, "intended operation has not run"

def test_ScanSequence_send(test_scan):
    """
    Ensure :func:`~engine_tools.engine_base.ScanSequence.send` shortcut 
    properly adds messages to the queue.  
    """
    scanner = test_scan()

    async def test_mgr():
        task = asyncio.ensure_future(scanner.regulator())
        await asyncio.sleep(.01)
        await scanner.send(scanner.end_code)
        try:
            await asyncio.wait_for(task,timeout=1)
        except asyncio.TimeoutError:
            pytest.fail("Failed to send ending codes")

    loop = asyncio.get_event_loop()
    loop.run_until_complete(test_mgr())
    assert scanner.n > 0, "intended operation has not run"

def test_ScanSequence_regulator_parallel(test_scan):
    """
    Ensure multiple scanners can operate in parallel.
    """ 
    n = 100
    scanners = []
    for i in range(n):
        scanners.append(test_scan())
        scanners[i].delay = 1 

    async def test_mgr():
        tasks = []
        for i in range(n):
            tasks.append(scanners[i].start())
        await asyncio.sleep(.1)
        for i in range(n):
            await scanners[i].end()
         
            try:
                await asyncio.wait_for(tasks[i],timeout=.1)
            except asyncio.TimeoutError:
                pytest.fail("Failed to end")
    
    loop = asyncio.get_event_loop()
    loop.run_until_complete(test_mgr())
    for i in range(n):
        assert scanners[i].n > 0, "intended operation has not run"

def test_ScanSequence_arbitrary_message(test_scan):
    """
    Ensure that arbitrary message types can be passed 
    """
    scanner = test_scan()
    
    class g:
        pass

    async def test_mgr():
        task = scanner.start()
        await asyncio.sleep(.01)
        await scanner.queue.put(g())
        await asyncio.sleep(.01)
        await scanner.queue.put(scanner.end_code)
        try:
            await asyncio.wait_for(task,timeout=1)
        except asyncio.TimeoutError:
            pytest.fail("Failed to end")
    
    loop = asyncio.get_event_loop()
    loop.run_until_complete(test_mgr())
    assert scanner.n > 0, "intended operation has not run"

def test_ScanSequence_complete(test_scan):
    """
    Ensure that the combined features work.
    """
    scanner = test_scan()

    async def test_mgr():
        task = scanner.start()
        await asyncio.sleep(.01)
        await scanner.end()
        try:
            await asyncio.wait_for(task,timeout=1)
        except asyncio.TimeoutError:
            pytest.fail("Failed to end")
        
    loop = asyncio.get_event_loop()
    loop.run_until_complete(test_mgr())
    assert scanner.n > 0, "intended operation has not run"

def test_MsgScanSequence_termination(test_msgscan):
    """
    Ensure that manually sending the end message works.
    """
    scanner = test_msgscan()

    async def test_mgr():
        task = scanner.start()
        await asyncio.sleep(.01)
        await scanner.queue.put(end_msg())
        try:
            await asyncio.wait_for(task,timeout=1)
        except asyncio.TimeoutError:
            pytest.fail("Failed to end")
        
    loop = asyncio.get_event_loop()
    loop.run_until_complete(test_mgr())
    assert scanner.n > 1, "intended operation has not run"

def test_MsgScanSequence_end(test_msgscan):
    """
    Ensure :func:`~engine_tools.engine_base.MsgScanSequence.end` properly
    terminates the regulator. 
    """
    scanner = test_msgscan()

    async def test_mgr():
        task = scanner.start()
        await asyncio.sleep(.01)
        await scanner.end()
        try:
            await asyncio.wait_for(task,timeout=1)
        except asyncio.TimeoutError:
            pytest.fail("Failed to end")
        
    loop = asyncio.get_event_loop()
    loop.run_until_complete(test_mgr())
    assert scanner.n > 1, "intended operation has not run"



