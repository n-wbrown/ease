import pytest
from engine_tools.engine_messages import (
    scan_seq_msg, generic_msg, update_msg, end_msg
)
import logging
from time import sleep

logger = logging.getLogger(__name__)

def test_generic_msg_init():
    """
    Ensure that :class:`~engine_tools.engine_messages.generic_msg` can be
    instantiated without errors
    """
    try:
        msg = generic_msg("test_code","test_content")
    except:
        pytest.fail("constructing new scan_seq_msg failed")

def test_generic_msg_eq():
    """
    Ensure that :func:`engine_tools.engine_messages.generic_msg.__eq__`
    properly recognizes identical messages
    """
    msg_A = generic_msg("code","content")
    msg_B = generic_msg("code","content")
    assert msg_A == msg_B, "Failure to report identical messages as equal"

    msg_A = generic_msg("code","content0")
    msg_B = generic_msg("code","content")
    assert msg_A != msg_B, "Failure to report different messages as unequal"

    msg_A = generic_msg("code0","content")
    msg_B = generic_msg("code","content")
    assert msg_A != msg_B, "Failure to report different messages as unequal"

def test_generic_msg_end():
    """
    Ensure that the timestamp of the last change updates when a varialbe is
    set.
    """
    msg = generic_msg() 

    msg.code = "a"
    time1 = msg.last_change
    sleep(.01)
    msg.code = "b"
    time2 = msg.last_change
    assert time1 != time2, "Failure to change last_change when setting code"

    msg.content = "a"
    time1 = msg.last_change
    sleep(.01)
    msg.content = "b"
    time2 = msg.last_change
    assert time1 != time2, "Failure to change last_change when setting content"


def test_update_msg():
    """
    Ensure that the shortcut,
    :func:`~engine_tools.engine_messages.update_msg`, can be used for creating
    classes.
    """
    msg = update_msg()
    assert msg.update, "Failure to be an update message"

def test_end_msg():
    """
    Ensure that the shortcut,
    :func:`~engine_tools.engine_messages.end_msg`, can be used for creating
    classes.
    """
    msg = end_msg()
    assert msg.end, "Failure to be an end message"

def test_scan_seq_msg_end():
    """
    Ensure that the special end message uses the
    :func:`~engine_tools.engine_messages.scan_seq_msg.end` property and  
    :func:`~engine_tools.engine_messages.scan_seq_msg.set_end` function.  
    """
    msg = scan_seq_msg()
    assert msg.end == False, "Failure to report as a non-ending message"
    
    msg.set_end()
    assert msg.end == True, "Failure to report as a ending message"

def test_scan_seq_msg_update():
    """
    Ensure that the special end message uses the
    :func:`~engine_tools.engine_messages.scan_seq_msg.update` property and  
    :func:`~engine_tools.engine_messages.scan_seq_msg.set_update` function.  
    """
    msg = scan_seq_msg()
    assert msg.update == False, "Failure to report as a non-ending message"
    
    msg.set_update()
    assert msg.update == True, "Failure to report as a ending message"

