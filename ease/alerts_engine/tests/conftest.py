import pytest
from engine_tools.engine_base import scan_sequence
import logging

logger = logging.getLogger(__name__)
logger.propagate = False
@pytest.fixture(scope='function')
def test_scan():
    class test_scan(scan_sequence):
        def __init__(self):
            super().__init__(self)
            self.n=0
            self.delay=0

        async def operation(self):
            self.n = self.n + 1
            logger.debug("n: " + str( self.n))
            
    return test_scan
