import pytest
from engine_tools.engine_base import ScanSequence, MsgScanSequence
import logging

logger = logging.getLogger(__name__)
logger.propagate = False

@pytest.fixture(scope='function')
def test_scan():
    """
    Pytest fixture for creating instances of the ScanSequence class with a
    delay of zero and an operation that increments an integer.
    """
    class test_scan(ScanSequence):
        def __init__(self):
            super().__init__(self)
            self.n=0
            self.delay=0

        async def operation(self):
            self.n = self.n + 1
            logger.debug("n: " + str( self.n))
            
    return test_scan

@pytest.fixture(scope='function')
def test_msgscan():
    """
    Pytest fixture for creating instances of the MsgScanSequence class with a
    delay of zero and an operation that increments an integer.
    """
    class test_msgscan(MsgScanSequence):
        def __init__(self):
            super().__init__(self)
            self.n=0
            self.delay=0

        async def operation(self):
            self.n = self.n + 1
            logger.debug("n: " + str( self.n))
            
    return test_msgscan
