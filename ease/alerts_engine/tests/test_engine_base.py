import pytest
import asyncio
from engine_tools.engine_base import scan_sequence
import logging 

logger = logging.getLogger(__name__)
logger.propagate = False
def test_scan_sequence_init():
    try:
        scanner = scan_sequence()
    except:
        pytest.fail("constructing new scan_sequence failed")


@pytest.mark.parametrize("msg", [1.2,{"abc":"def"},set([1,2,3])])
def test_scan_sequence_wait_next(msg):
    scanner = scan_sequence()
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
            result = await asyncio.wait_for(task,timeout=2)
        except asyncio.TimeoutError:
            pytest.fail("interruption test took too long to complete")

        assert result == msg, "interruption test returned wrong value"
        
        #ensure that interruption is possible even with 0 delay
        scanner.delay = 0
        await scanner.queue.put(msg)
        task = asyncio.ensure_future(scanner.wait_next())
        try:
            result = await asyncio.wait_for(task,timeout=2)
        except asyncio.TimeoutError:
            pytest.fail("0-delay interruption test  took too long to complete")
        
        assert result == msg, ("0-delay interruption test returns wrong value")

    loop = asyncio.get_event_loop()    
    loop.run_until_complete(test_mgr())

def test_scan_sequence_regulator_repeated_operation(test_scan):
    scanner = test_scan

    async def test_mgr():
        task = asyncio.ensure_future(scanner.regulator())
        await asyncio.sleep(.1)
        task.cancel()

    loop = asyncio.get_event_loop()
    loop.run_until_complete(test_mgr())
    logger.debug("final n: " +str(scanner.n))
    assert scanner.n > 0, "intended operation never ran"

@pytest.mark.parametrize("m", ([0]*9)+[.01,.02,.03,.04,.05,.1,.2,.3,.4])
def test_scan_sequence_regulator_termination(test_scan,m):
    scanner = test_scan
    scanner.delay = m


    async def test_mgr():
        task = asyncio.ensure_future(scanner.regulator())
        await asyncio.sleep(.01)
        #scanner.queue.put_nowait(scanner.end_code)
        await scanner.queue.put(scanner.end_code)
        print("put complete",scanner.queue.qsize())
        try:
            await asyncio.wait_for(task,timeout=1)
        except asyncio.TimeoutError:
            pytest.fail("Failed to end")

    loop = asyncio.get_event_loop()
    loop.run_until_complete(test_mgr())
    assert scanner.n > 0, "intended operation has not run"
    
def test_scan_sequence_cancel(test_scan):
    scanner = test_scan

    async def test_mgr():
        task = asyncio.ensure_future(scanner.regulator())
        await asyncio.sleep(.01)
        await scanner.cancel()
        try:
            await asyncio.wait_for(task,timeout=1)
        except asyncio.TimeoutError:
            pytest.fail("Failed to cancel")

    loop = asyncio.get_event_loop()
    loop.run_until_complete(test_mgr())
    assert scanner.n > 0, "intended operation has not run"

def test_scan_sequence_start(test_scan):
    scanner = test_scan

    async def test_mgr():
        #task = asyncio.ensure_future(scanner.regulator())
        print(scanner.queue.qsize())
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

