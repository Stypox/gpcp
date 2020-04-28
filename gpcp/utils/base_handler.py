import enum
from .filters import command

class BaseHandler:


    class FunctionType(enum.Enum):
        command = 0
        unknown = 1

    def __init__(self):
        pass

    @classmethod
    def loadHandlers(cls):
        """loads all handlers in a BaseHandler derivated object"""

        if hasattr(cls, "commandFunctions") and isinstance(cls.commandFunctions, dict):
            return # already loaded
        cls.commandFunctions = {}
        cls.unknownCommandFunction = None

        #get all function with a __gpcp_metadata__ value
        functionMapRaw = [func for func in [getattr(cls, func) for func in dir(cls)]
                          if callable(func) and hasattr(func, "__gpcp_metadata__")]

        for func in functionMapRaw:
            # func.__gpcp_metadata__ = (<functionType>, ...)
            functionType = func.__gpcp_metadata__[0]

            if functionType == cls.FunctionType.command:
                # func.__gpcp_metadata__ = (command, <command trigger>, <return type>
                #   [<param 1 type>, < param 2 type>, ...])
                command, returnType, argumentTypes = func.__gpcp_metadata__[1:]

                if command in cls.commandFunctions:
                    raise ValueError(f"command {command} already registered and"
                                     + f" mapped to {cls.commandFunctions[command]}")
                cls.commandFunctions[command] = (func, returnType, argumentTypes)

            elif functionType == cls.FunctionType.unknown:
                # func.__gpcp_metadata__ = (unknown,)
                if cls.unknownCommandFunction is not None:
                    raise ValueError(f"handler for unknown commands already registered"
                                     + f" and mapped to {cls.unknownCommandFunction}")
                cls.unknownCommandFunction = func

            else:
                raise ValueError(f"invalid __gpcp_metadata__ for function"
                                 + f" {func}: {func.__gpcp_metadata__}")

    def handleData(self, command):
        parts = command.split()
        commandIdentifier = parts[0].decode(ENCODING)

        try:
            function, returnType, argumentTypes = self.commandFunctions[commandIdentifier]
        except KeyError:
            if self.unknownCommandFunction is None:
                return b"Unknown command" # TODO some other type of error handling
            return self.unknownCommandFunction(commandIdentifier, parts[1:])

        # convert parameters from `bytes` to the types of `function` arguments
        arguments = []
        for i in range(len(parts) - 1):
            arguments.append(argumentTypes[i].fromBytes(parts[i+1]))

        # convert the return value to `bytes` from the specified type
        returnValue = function(self, commandIdentifier, *arguments)
        return returnType.toBytes(returnValue)

    @command
    def requestCommands(self)
        """requests the commands list from the server and returns it."""
        return list( [command for command in self.commandFunctions.keys()] )
