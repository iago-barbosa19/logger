import os, datetime, inspect, traceback
from typing import Literal
from functools import wraps
from yaml import load, Loader, dump, Dumper


class Log:

    _instance: Literal['Log'] = None
    DEBUG: int = 1
    INFO: int = 2
    WARN: int = 3
    ERROR: int = 4
    CRITICAL: int = 5
    
    def __init__(self, *, directory: str, file_name: str, opening_method: str = 'a+', encoding_method: str = 'utf-8', logger_level = 1, size_limit = 512):
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
            size_limit (int, optional): Maximum size for the archive in MegaBytes. Defaults to 512.
        """
        if not os.path.exists(directory):
            os.mkdir(directory)
        self.__directory = directory
        self.__file_name = file_name
        self.__opening_method = opening_method
        self.__encoding_method = encoding_method
        self.__level = logger_level
        self.__size_limit = size_limit

    @property
    def directory(self) -> str:
        """
        Returns the directory where the log is located.

        Args:
            self (object): Itself

        Returns:
            str: directory where it's located
        """
        return self.__directory

    @property
    def file_directory(self) -> str:
        """
        Returns the path where the log file is located

        Args:
            self (object): Itself

        Returns:
            str: path to the log file
        """
        return os.path.join(self.__directory, self.file_name)

    @property
    def file_name(self) -> str:
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
    def opening_method(self) -> str:
        """
        Returns the opening method of the log file, in case it's needed.

        Args:
            self (object): Itself

        Returns:
            str: Opening Method
        """
        return self.__opening_method

    @property
    def encoding_method(self) -> str:
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
    def level(self) -> int:
        return self.__level

    @property
    def file_size(self) -> int:
        if os.path.exists(self.file_directory):
            return os.stat(self.file_directory).st_size / (1024 * 1024)
        return 0
    
    def __str__(self) -> str:
        """
        Returns all the informations about the current instance of Log object and file.

        Args:
            self (object): Itself

        Returns:
            str: Informations about current instance of the object. 
        """
        file_size = os.stat(self.file_directory).st_size / (1024 * 1024)
        return f'Directory:{self.__directory}|File:{self.__file_name}|Opening Method:{self.__opening_method}|Encoding Method:{self.__encoding_method}|File Weight (MB):{file_size}'

    @property
    def caller_module(self) -> str:
        """
        Get the file name from the archive where the Log was called.

        Args:
            self (object): Itself

        Returns:
            str: Caller module name
        """
        caller = inspect.stack()[4]
        module_caller = inspect.getmodule(caller[0])
        return f'{module_caller.__name__} : {caller.function}'

    def write_log(log_message_mounter):
        """
        Decorator function for functions: [info, debug, warn, critical, error]
        
        Parameters:
            function_to_execute: Literal['function'] -> The decorated function that's gonna be executed
            
        Returns:
            writer: Literal['function'] -> The function that's gonna be returned for "execution"
        """
        @wraps(log_message_mounter)
        def writer(self, message_to_log: str, exception_occurrence: Exception = None, /) -> None:
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
            self.__split_file_if_necessary()
            messages = self.__get_messages(message_to_log, exception_occurrence)
            self.__write_messages_in_file(messages, log_message_mounter)
        return writer
        
    def __split_file_if_necessary(self) -> None:
        if self.file_size >= self.__size_limit:
            self.__split_file()
    
    def __split_file(self) -> None:
        file_splitted_name = f'{self.__file_name}-1'
        os.rename(self.directory, os.path.join(self.__directory, file_splitted_name))
    
    def __get_messages(self, message_to_log: str, exception_occurrence: Exception = None) -> list:
        values_to_return = []
        if isinstance(message_to_log, Exception) or  exception_occurrence is not None and isinstance(exception_occurrence, Exception):
            values_to_return.extend(self.__assemble_exception_message(message_to_log, exception_occurrence))
        else:
            values_to_return.append(message_to_log)
        return values_to_return

    def __write_messages_in_file(self, messages: list, log_message_mounter) -> None:
        for message in messages:
            log_message, log_level_message = log_message_mounter(self, message)
            if self.level <= log_level_message:
                with open(self.file_directory, self.opening_method, encoding=self.__encoding_method) as file:
                    file.write(log_message)
            self.__show_message_if_level_equals(log_level_message, log_message)
        
    def __assemble_exception_message(self, message: str, exception_occurrence: Exception) -> str:
        """
        The factory of message in case of 

        Args:
            self (object): _description_
            message (str): _description_
            exception_occurrence (Exception): _description_

        Returns:
            str: _description_
        """
        values_to_return = []
        exception_complete_traceback = traceback.TracebackException.from_exception(message if exception_occurrence is None else exception_occurrence)
        # exception_traceback_stack =  exception_traceback.stack[0]
        for exception_traceback in exception_complete_traceback.stack:
            exception_motive, exception_cause, localization_of_exception, exception_line  = exception_complete_traceback._str, exception_traceback.line, exception_traceback.name, exception_traceback.lineno
            values_to_return.append(f'{"" if exception_occurrence is None else f"{message} ---"} Motive: {exception_motive} | Cause: {exception_cause} | Line: {exception_line} | Localization of Exception: {localization_of_exception} |')
        return values_to_return
    
    @write_log
    def info(self, message: str) -> str:
        return f"| {datetime.datetime.now().strftime('%d/%m/%Y - %H:%M:%S.%f')} --- File: {self.caller_module} [INFO] --- {message}\n", Log.INFO
        
    @write_log
    def debug(self, message: str) -> str:
        return f"| {datetime.datetime.now().strftime('%d/%m/%Y - %H:%M:%S.%f')} --- File: {self.caller_module} [DEBUG] --- {message}\n", Log.DEBUG

    @write_log
    def warn(self, message: str) -> str:
        return f"| {datetime.datetime.now().strftime('%d/%m/%Y - %H:%M:%S.%f')} --- File: {self.caller_module} [WARN] --- {message}\n", Log.WARN
    
    @write_log
    def critical(self, message: str) -> str:
        return f"| {datetime.datetime.now().strftime('%d/%m/%Y - %H:%M:%S.%f')} --- File: {self.caller_module} [CRITICAL] --- {message}\n", Log.CRITICAL
            
    @write_log
    def error(self, message: str) -> str:
        return f"| {datetime.datetime.now().strftime('%d/%m/%Y - %H:%M:%S.%f')} --- File: {self.caller_module} [ERROR] --- {message}\n", Log.ERROR
        
    def __show_message_if_level_equals(self, level_of_occurrence: int, message: str) -> None:
        """
        Check if the log message leve is the same as the debug level of the logger.

        Args:
            self (object): The instance of Log Object
            level_of_occurrence (int): The level of the occurrence message
            message (str): The Message content
        """
        if self.level <= level_of_occurrence:
            os.system(f'echo "{message}"')

    @staticmethod
    def __get_logger_level(logger_level: int) -> None:
        """
        Get the logger level and set it to the Log instance.
        
        Args:
            logger_level (int): The logger level that's gonna be set on the Log instance
        """
        if logger_level in ['DEBUG', 'INFO', 'WARN', 'ERROR', 'CRITICAL']:
            if logger_level == 'DEBUG':
                return Log.DEBUG
            elif logger_level == 'INFO':
                return Log.INFO
            elif logger_level == 'WARN':
                return Log.WARN
            elif logger_level == 'ERROR':
                return Log.ERROR
            elif logger_level == 'CRITICAL':
                return Log.CRITICAL
        return None
    
    def __get_settings__() -> dict:
        logger_settings = load(open('./log_settings.yml', 'r').read(), Loader=Loader)
        return logger_settings.get('directory'), logger_settings.get('file_name'), logger_settings.get('opening_method'), logger_settings.get('encoding_method'), logger_settings.get('log_level'), logger_settings.get('size_limit')
    
    @classmethod
    def get_logger(cls):
        """
        Singleton method to catch the instance of the logger or create the first instance.
        If it's the first instance, then the logger will get his settings from logg_config.yml
        
        Returns:
            self._instance: Literal['Log instance'] -> The instance of the Log object
        """
        if cls._instance is None:
            directory, file_name, opening_method, encoding_method, logger_level, size_limit = cls.__get_settings__()
            logger_level = Log.__get_logger_level(logger_level)
            cls._instance =  cls( directory = directory
                                    , file_name = file_name
                                    , opening_method = opening_method if opening_method is not None else 'a+'
                                    , encoding_method = encoding_method if encoding_method is not None else 'utf-8'
                                    , logger_level = logger_level if logger_level is not None else 1
                                    , size_limit = size_limit if size_limit is not None else 512
                                    )
        return cls._instance
