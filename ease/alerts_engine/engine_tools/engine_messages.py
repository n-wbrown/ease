import datetime

class generic_msg:
    """
    Class for communicating with running scan sequences. Alterations to core
    attributes :attr:`~engine_tools.engine_messages.scan_seq_msg.code` and 
    attributes :attr:`~engine_tools.engine_messages.scan_seq_msg.content` are
    timestamped.

    Attributes
    ----------
    code
        Header for message, includes header type.

    content
        Contains message information.

    end
        Returns true if the end code is being used 
        
    """
    i_last_change = None
    
    def __init__(self, code=None, content=None):
        self.code = code
        self.content = content

    def __eq__(self,other):
        if type(self) == type(other):
            if self.code == other.code and self.content == other.content:
                return True 
            else:
                return False
        else:
            return False
    
    def _get_code(self):
        return self._code

    def _set_code(self, value):
        self._code = value
        self._last_change = datetime.datetime.now()

    def _del_code(self):
        del self._code
        self._last_change = datetime.datetime.now()

    code = property(_get_code, _set_code, _del_code)
    
    def _get_content(self):
        return self._content

    def _set_content(self, value):
        self._content = value
        self._last_change = datetime.datetime.now()

    def _del_content(self):
        del self._content
        self._last_change = datetime.datetime.now()

    content = property(_get_content, _set_content, _del_code)
    
    @property
    def last_change(self):
        """
        Return the timestamp of the last change
        
        Returns
        -------
        datetime.datetime
            Timestamp of last change
        
        """
        return self._last_change 


class scan_seq_msg(generic_msg):

    end_code = "scan_seq_msg END_CODE"
    update_code = "scan_seq_msg UPDATE_CODE"

    @property
    def end(self):
        """
        Return true if the end code is being used 
        
        Returns
        -------
        bool
            True if this is an ending message 
        """
        if self.code == self.end_code:
            return True
        return False

    def set_end(self):
        """
        Set this message to the ending code
        """
        self.code = self.end_code
    
    @property
    def update(self):
        """
        Return true if the update code is being used 
        
        Returns
        -------
        bool
            True if this is an update message 
        """
        if self.code == self.update_code:
            return True
        return False

    def set_update(self):
        """
        Set this message to the update code
        """
        self.code = self.update_code
