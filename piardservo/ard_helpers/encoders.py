import abc

class Encoder(abc.ABC):

    @abc.abstractmethod
    def encode_data(self, data):
        pass

class CommaDelimitedEncoder(Encoder):
    """
    comma delimited data to serial encoding from python to arduino
    
    """
    
    def __init__(self, 
                 begin_message = '<',
                 end_message = '>',
                 begin_system_message = '[',
                 serial_format = 'utf-8',
                ):
        
        self.begin_message = begin_message
        self.end_message = end_message
        self.serial_format = serial_format
        
    def encode_data(self, data):
        """
        takes angle a list of data and converts to message to send to 
        the arduino. example
        
        >>> CDE = CommaDelimitedEncoder()
        >>> data = [1,3,4]
        >>> CDE.encode_data(data)
        b'<1,3,4>
    
        """
        encoded_message = self.begin_message
        l = len(data)
        for i, msg in enumerate(data):
            encoded_message += str(msg)
            if i < l-1: 
                encoded_message += ','
  
        encoded_message += self.end_message
        return encoded_message.encode(self.serial_format)
    
    def encode_system_message(self, data):
        """
        placeholder for future iterations
        """
        pass


class TwoByteEncoder(Encoder):

    def __init__(self,
                 begin_message = 16,
                 end_message = 17
                 ):

        self.begin_message = begin_message
        self.end_message = end_message

    def encode_data(self, data):

        _message = [0, self.begin_message]

        for pos, i in data:
            foo1 = pos << 5
            foo1 += i
            n1 = foo1 >> 8
            n2 = foo1 & 255
            _message += [n1, n2]

        _message.append(self.end_message)
        return bytes(_message)





    