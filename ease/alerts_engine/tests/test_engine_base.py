import pytest
import asyncio
from engine_tools.engine_base import scan_sequence


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

'''
def test_scan_sequence_start():
    
    class test_scan(scan_sequence):
        async def operation(self):
            self.n = self.n + 1
    
    scanner = test_scan()
    scanner.delay= 0
    scanner.n = 0

    async def test_mgr():
        future = asyncio.Future()
        task = asyncio.ensure_future(scanner.regulator())
        await asyncio.sleep(.1)
        task.cancel()

    loop = asyncio.get_event_loop()
    
    loop.run_until_complete(test_mgr())
    assert scanner.n > 0, "intended operation never ran"
    '''


def test_scan_sequence_regulator_repeated_operation():

    class test_scan(scan_sequence):
        async def operation(self):
            print("running op")
            self.n = self.n + 1
    
    scanner = test_scan()
    scanner.delay= 0
    scanner.n = 0

    async def test_mgr():
        future = asyncio.Future()
        task = asyncio.ensure_future(scanner.regulator())
        await asyncio.sleep(1)
        task.cancel()

    loop = asyncio.get_event_loop()
    
    loop.run_until_complete(test_mgr())
    print("final n:",scanner.n)
    assert scanner.n > 0, "intended operation never ran"



def test_scan_sequence_regulator_termination():

    class test_scan(scan_sequence):
        async def operation(self):
            self.n = self.n + 1
    
    scanner = test_scan()
    scanner.delay = 0
    scanner.n = 0


    async def test_mgr():
        future = asyncio.Future()
        task = asyncio.ensure_future(scanner.regulator(future))
        await asyncio.sleep(.1)
        await scanner.queue.put("end")
        await asyncio.wait_for(future,timeout=1)
        assert future.result() == 'done'

    loop = asyncio.get_event_loop()
    
    loop.run_until_complete(test_mgr())
    assert scanner.n > 0, "intended operation has not run"
    


    
    


