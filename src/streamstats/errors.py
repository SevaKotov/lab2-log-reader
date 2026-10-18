class Stream_Stats_Error(Exception):
    pass

class InvalidTimestampError(Stream_Stats_Error):
    pass

class Invalid_Format(Stream_Stats_Error):
    pass

class Invalid_Event(Stream_Stats_Error):
    pass

class Invalid_Path(Stream_Stats_Error):
    pass

class Invalid_Command(Stream_Stats_Error):
    pass