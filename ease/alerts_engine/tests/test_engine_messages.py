import pytest
from engine_tools.engine_messages import scan_seq_msg
import logging

logger = logging.getLogger(__name__)

def test_scan_seq_msg_init():
    """
    Ensure that :class:`~engine_messages.scan_seq_msg` can be instantiated
    without errors
    """
    try:
        msg = scan_seq_msg("test_code","test_content")
    except:
        pytest.fail("constructing new scan_seq_msg failed")

def test_scan_seq_msg_eq():
    """
    Ensure that :func:`engine_messages.scan_seq_msg.__eq__` properly recognizes
    identical messages
    """
    msg_A = scan_seq_msg("code","content")
    msg_B = scan_seq_msg("code","content")
    assert msg_A == msg_B, "Failure to report identical messages as equal"

    msg_A = scan_seq_msg("code","content0")
    msg_B = scan_seq_msg("code","content")
    assert msg_A != msg_B, "Failure to report different messages as unequal"

    msg_A = scan_seq_msg("code0","content")
    msg_B = scan_seq_msg("code","content")
    assert msg_A != msg_B, "Failure to report different messages as unequal"

def test_scan_seq_msg_end():
    msg = scan_seq_msg()
    assert msg.end == False, "Failure to report as a non-ending message"
    
    msg.set_end()
    assert msg.end == True, "Failure to report as a ending message"

