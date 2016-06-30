import types

from . exceptions import ProcedureNotFoundError
from . messages.call import Call


class RpcProxy:

    def __init__(self, client):
        self.client = client

    def __getattr__(self, name):
        from . registry import Registry
        procedures = [v[1] for v in Registry.registration_map.values()]
        if name in procedures:

            def wrapper(*args, **kwargs):
                message = Call(procedure=name, args=args, kwargs=kwargs)
                message.construct()
                self.client.logger.info(message)
                self.client.send_message(message)
                response = self.client.receive_message()
                results = response[3]
                result = results[0]
                return result

            return wrapper

        raise ProcedureNotFoundError(name)


def register_rpc(*args, **kwargs):
    assert isinstance(args[0], types.FunctionType)
    wrapped = args[0]

    def decorator(fn, *args, **kwargs):
        fn.rpc = True
        return fn

    return decorator(wrapped, args=(), kwargs={})


rpc = register_rpc
