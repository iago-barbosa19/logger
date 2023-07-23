import os, datetime, inspect, traceback
from typing import Literal
from functools import wraps


class Log:

    _instance: Literal['Log'] = None
    INFO: int = 1
    DEBUG: int = 2
    WARN: int = 3
    CRITICAL: int = 4
    ERROR: int = 5
    
    def __init__(self: object, *, directory: str, file_name: str, opening_method: str = 'a+', encoding_method: str = 'utf-8', debug_level = 0):
        """
        Constructor method, it's not meant to be called directly.
        As a singleton class, it's necessary to call the get_logger method.
        As this class doesn't need more than one instance, and it's not really advised to use multiple instances of this class

        Args:
            self (object): The instance of object
            directory (str): Directory that the logger file is meant to be placed 
            file_name (str): The name that the logger file is meant to be named
            opening_method (str, optional): The opening method of the logger file. Defaults to 'a+'.
            encoding_method (str, optional): The encoding written method, the file will be written using this method as basis. Defaults to 'utf-8'.
            level (int, optional): Debug Level. Defaults to 0.
        """
        if not os.path.exists(directory):
            os.mkdir(directory)
        self.__directory = directory
        self.__file_name = file_name
        self.__opening_method = opening_method
        self.__encoding_method = encoding_method
        self.__level = debug_level

    @property
    def directory(self: Literal['Log']) -> str:
        """
        Returns the directory where the log is located.

        Args:
            self (object): Itself

        Returns:
            str: directory where it's located
        """
        return self.__directory

    @property
    def file_directory(self: Literal['Log']) -> str:
        """
        Returns the path where the log file is located

        Args:
            self (object): Itself

        Returns:
            str: path to the log file
        """
        return os.path.join(self.__directory, self.file_name)

    @property
    def file_name(self: Literal['Log']) -> str:
        """
        Returns the filename of the logger, in case it's needed.
        The filename it's updated when the day changes, so the lib 
        can create a new file when the day changes, keeping
        the log directory organized, and the log file compact
        

        Args:
            self (object): Itself

        Returns:
            str: File name
        """
        return '{current_date}_{received_name}.log'.format( current_date=datetime.datetime.now().strftime("%Y-%m-%d"),
                                                                        received_name=self.__file_name)
    
    @property
    def opening_method(self: Literal['Log']) -> str:
        """
        Returns the opening method of the log file, in case it's needed.

        Args:
            self (object): Itself

        Returns:
            str: Opening Method
        """
        return self.__opening_method

    @property
    def encoding_method(self: Literal['Log']) -> str:
        """
        Returns the encoding method of the log file, in case it's needed.
        Examples: utf-8, ascii, iso-8859-1
        
        Args:
            self (object): Itself

        Returns:
            str: The encoding method
        """
        return self.__encoding_method

    @property
    def level(self: Literal['Log']) -> int:
        return self.__level
    
    def __str__(self: Literal['Log']) -> str:
        """
        Returns all the informations about the current instance of Log object and file.

        Args:
            self (object): Itself

        Returns:
            str: Informations about current instance of the object. 
        """
        file_size = os.stat(self.__file_directory).st_size / (1024 * 1024)
        return f'Directory: {self.__directory} | File: {self.__file_name} | Opening Method: {self.__opening_method} | Encoding Method: {self.__encoding_method}\n File Weight (MB): {file_size}'

    @property
    def caller_module(self: Literal['Log']) -> str:
        """
        Get the file name from the archive where the Log was called.

        Args:
            self (object): Itself

        Returns:
            str: Caller module name
        """
        caller = inspect.stack()[3]
        module_caller = inspect.getmodule(caller[0])
        return f'{module_caller.__name__} : {caller.function}'

    def write_log(log_message_mounter: Literal['Function']) -> Literal['Function']:
        """
        Decorator function for functions: [info, debug, warn, critical, error]
        
        Parameters:
            function_to_execute: Literal['function'] -> The decorated function that's gonna be executed
            
        Returns:
            writer: Literal['function'] -> The function that's gonna be returned for "execution"
        """
        @wraps(log_message_mounter)
        def writer(self: object, message: str, exception_occurrence: Exception = None, /) -> None:
            """
            Method that writes messages on the log.
            For normal cases of [INFO, DEBUG, WARN] the exception_occurrence can be set on None
            In cases of [CRITICAL] if occurs an exception, or is raised an exception, you can pass it through exception_occurrence, so an 
            specific message can be mounted.
            In cases of [ERROR] You need to pass the exception through exception_occurrence, otherwise the message will be malformed and will only show the message 
            that was passed, and not the message and exception.
            
            You can pass only the exception exception_occurrence if you only want the exception on the log.

            Args:
                Positional arguments.
                self (object): The Log instance
                message (str): Message that will be written on log file
                exception_occurrence (Exception, optional): The Exception that occurred on code. Defaults to None.
            """
            if isinstance(message, Exception) or  exception_occurrence is not None and isinstance(exception_occurrence, Exception):
                message = self.assemble_exception_message(message, exception_occurrence)
            log_message, log_level_message = log_message_mounter(self, message)
            with open(self.file_directory, self.opening_method, encoding=self.__encoding_method) as file:
                file.write(log_message)
            self.__show_message_if_level_equals(log_level_message, log_message)
            
        return writer

    def assemble_exception_message(self: object, message: str, exception_occurrence: Exception) -> str:
        """
        The factory of message in case of 

        Args:
            self (object): _description_
            message (str): _description_
            exception_occurrence (Exception): _description_

        Returns:
            str: _description_
        """
        exception_traceback = traceback.TracebackException.from_exception(message if exception_occurrence is None else exception_occurrence)
        exception_traceback_stack =  exception_traceback.stack[0]
        exception_motive, exception_cause, localization_of_exception, exception_line  = exception_traceback._str, exception_traceback_stack.line, exception_traceback_stack.name, exception_traceback_stack.lineno
        return_value = f'{"" if exception_occurrence is None else f"{message} ---"} Motive: {exception_motive} | Cause: {exception_cause} | Line: {exception_line} | Localization of Exception: {localization_of_exception} |'
        return return_value
    
    @write_log
    def info(self, message: str) -> str:
        return f"| {datetime.datetime.now().strftime('%d/%m/%Y - %H:%M:%S')} --- File: {self.caller_module} [INFO] --- {message}\n", Log.INFO
        
    @write_log
    def debug(self: object, message: str) -> str:
        return f"| {datetime.datetime.now().strftime('%d/%m/%Y - %H:%M:%S')} --- File: {self.caller_module} [DEBUG] --- {message}\n", Log.DEBUG

    @write_log
    def warn(self: object, message: str) -> str:
        return f"| {datetime.datetime.now().strftime('%d/%m/%Y - %H:%M:%S')} --- File: {self.caller_module} [WARN] --- {message}\n", Log.WARN
    
    @write_log
    def critical(self: object, message: str) -> str:
        return f"| {datetime.datetime.now().strftime('%d/%m/%Y - %H:%M:%S')} --- File: {self.caller_module} [CRITICAL] --- {message}\n", Log.CRITICAL
            
    @write_log
    def error(self: object, message: str) -> str:
        return f"| {datetime.datetime.now().strftime('%d/%m/%Y - %H:%M:%S')} --- File: {self.caller_module} [ERROR] --- {message}\n", Log.ERROR
        
    def __show_message_if_level_equals(self:object, level_of_occurrence: int, message: str) -> None:
        """
        Check if the log message leve is the same as the debug level of the logger.

        Args:
            self (object): The instance of Log Object
            level_of_occurrence (int): The level of the occurrence message
            message (str): The Message content
        """
        if self.level <= level_of_occurrence:
            os.system(f'echo "{message}"')
            
    @classmethod
    def get_instance(self: Literal['Log'], logger_configs = None, **kwargs) -> Literal['Log']:
        """
        Singleton method to catch the only instance of the logger.
        
        Params:
            directory (str): The directory of the file.
            file_name (str): The file name of the file.
            opening_method (str): The method of opening of the Log File ['w+', 'a+']. Defaults to 'a+
            encoding_method (str): The method of encoding ['utf-8', 'iso-8859-3']. Defaults to 'utf-8'
            debug_level (CONSTANT): The debugging level of the logger. Defauls to INFO
            (Use the constants of the class, like INFO, DEBUG, WARN, CRITICAL AND ERROR).

        Returns:
            self._instance: Literal['Log instance'] -> The instance of the Log object
        """
        if self._instance is None:
            if logger_configs == None:
                logger_configs = kwargs
            directory, file_name, opening_method, encoding_method, debug_level = logger_configs.get('directory'), logger_configs.get('file_name'), logger_configs.get('opening_method'), logger_configs.get('encoding_method'), logger_configs.get('debug_level')
            self._instance =  self( directory = directory
                                    , file_name = file_name
                                    , opening_method = opening_method if opening_method is not None else 'a+'
                                    , encoding_method = encoding_method if encoding_method is not None else 'utf-8'
                                    , debug_level = debug_level if debug_level is not None else 0)
        return self._instance
    