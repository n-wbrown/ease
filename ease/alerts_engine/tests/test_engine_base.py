import pytest
import asyncio
from engine_tools.engine_base import scan_sequence


def test_scan_sequence_init():
    try:
        scanner = scan_sequence()
    except:
        pytest.fail("constructing new scan_sequence failed")


def test_scan_sequence_regulator_repeated_operation():

    class test_scan(scan_sequence):
        async def operation(self):
            self.n = self.n + 1
    
    scanner = test_scan()
    scanner.delay= 0
    scanner.n = 0

    async def mgr():
        future = asyncio.Future()
        task = asyncio.ensure_future(scanner.regulator(future))
        await asyncio.sleep(.1)
        task.cancel()

    loop = asyncio.get_event_loop()
    
    loop.run_until_complete(mgr())
    assert scanner.n > 0, "intended operation has not run"



def test_scan_sequence_regulator_termination():

    class test_scan(scan_sequence):
        async def operation(self):
            self.n = self.n + 1
    
    scanner = test_scan()
    scanner.delay = 0
    scanner.n = 0


    async def mgr():
        future = asyncio.Future()
        task = asyncio.ensure_future(scanner.regulator(future))
        await asyncio.sleep(.1)
        await scanner.queue.put("end")
        await asyncio.wait_for(future,timeout=1)
        assert future.result() == 'done'

    loop = asyncio.get_event_loop()
    
    loop.run_until_complete(mgr())
    assert scanner.n > 0, "intended operation has not run"
    


    
    


