import asyncio, inspect, textwrap, traceback, sys, socket, re
from typing import Union
from .network import RobotNetwork


class Robot:
    
    def __init__(self, id: int = None):
        """
        Constructing a robot instance with the passed in id and namespace.
        :param id: Optional. The robot's ID. If the program is running on an robotics
        lab's Raspberry Pi, it is automatically calculated.
        """
        hostname=socket.gethostname()
        match=re.fullmatch(r'^choate-robotics-rpi-(\d{2})$',hostname)
        if match:
            self.id=int(match.group(1))
        else:
            if isinstance(id,int):
                self.id=id
            else:
                raise ValueError("ID cannot be calculated. Please specify an ID.")
            
        self.network = RobotNetwork(self)
        self._event_loop = asyncio.get_event_loop()
        self._should_stop = asyncio.Event()
        self._exit_code=0
        self._ignore_exceptions=False
        
    def run(self, namespace: dict, looping_interval: float = 0.05, ignore_exceptions=False):
        """
        Runs the main event loop. This function must be called only once.
        It should be placed on the last line of the robot's script because
        this function does not return.
        
        :param dict namespace: The global namespace (technically, the namespace \
        that contains :func:`setup()` and :func:`loop()`) the robot program. \
        This is what makes all the magic happen. If you have \
        no idea what it is, use :func:`globals()`.
        :param float looping_interval: Looping interval \
        in seconds. Defaults to :code`0.05` (that is, the loop runs 20 times per \
        second). This argument has no effect if loop is a coroutine function.
        :param bool ignore_exceptions: Whether or not the robot should continue\
        running if an exception occurs when the loop is running. Note that it\
        does not mean the program will continue executing the next line, but\
        will run the next iteration of loop instead. Defaults to :code:`False`.\
        It is dangerous to enable and use only if you are confident that your\
        program can recover from unhandled exceptions. Regardless of this value,\
        KeyboardInterrupt (ctrl-c) will always shutdown the robot.
        """
        
        self.__globals = namespace
        self._looping_interval = looping_interval
        self._ignore_exceptions=ignore_exceptions
        
        self._setup = self.__globals.get('setup', lambda: None)
        if asyncio.iscoroutinefunction(self._setup):
            print('Setup function must not be async')
            sys.exit(1)
        self._run_setup()
        
        self._on_message = self.__globals.get('on_message', lambda m: None)
        self._on_shutdown = self.__globals.get('on_shutdown', lambda: None)
        self._loop = self.__globals.get('loop', lambda: None)
        
        if asyncio.iscoroutinefunction(self._loop):
            asyncio.ensure_future(self._run_loop_async())
        else:
            self._event_loop.call_soon(self._run_loop)
            
        asyncio.ensure_future(self._poll())
        
        try:
            self._event_loop.set_debug(True)
            self._event_loop.run_forever()
        finally:
            try:
                self._event_loop.run_until_complete(self._shutdown())
            finally:
                try: # retrieve all CancelledError
                    self._event_loop.run_until_complete(asyncio.gather(*asyncio.Task.all_tasks()))
                except asyncio.CancelledError:
                    pass
                self._event_loop.close()
                sys.exit(self._exit_code)
    
    
    def set_looping_interval(self, interval: float) -> None:
        """
        Set the looping interval. This function has no effect if loop is a
        coroutine.
        
        :param interval: float, looping interval in seconds.
        :return: None
        """
        
        self._looping_interval = interval
    
    async def _poll(self):
        is_handler_async=asyncio.iscoroutinefunction(self._on_message)
        while True:
            if self._should_stop.is_set():
                return
            try:
                msgs = await self.network.coro.poll()
                for msg_id in msgs:
                    msg = await self.network.coro.retrieve(msg_id)
                    if is_handler_async:
                        await self._on_message(msg)
                    else:
                        self._on_message(msg)
            except asyncio.CancelledError:
                raise
            except KeyboardInterrupt:
                self.shutdown(1)
            except:
                print('Error polling')
                pass  # TODO: Handle specific connection errors
            finally:
                await asyncio.sleep(0.2)
    
    def _run_setup(self):
        # patching the source code
        source = inspect.getsource(self._setup)
        source = source.split('\n')
        source = source[1:]  # to get rid of the def setup() part
        source = '\n'.join(source)
        source = textwrap.dedent(source)
        
        ns = {}
        try:
            exec(source, self.__globals, ns)
        except KeyboardInterrupt:
            self.shutdown(1)
        except:
            exc_type, exc_obj, tb = sys.exc_info()
            tbs = traceback.extract_tb(tb)
            print('Error while running setup: %s' % traceback.format_exception_only(exc_type, exc_obj)[0].strip(), file=sys.stderr)
            print('\t', source.split('\n')[tbs[1].lineno - 1],
                  '\t\t(at line %d)' % tbs[1].lineno,
                  file=sys.stderr)
            if len(tbs) > 2:
                for s in tbs.format()[2:]:
                    print(textwrap.dedent(s), file=sys.stderr)
            if not self._ignore_exceptions:
                self.shutdown(1)
        
        self.__globals.update(ns)
    
    def _run_loop(self):
        if self._should_stop.is_set():
            return
        self._event_loop.call_later(self._looping_interval, self._run_loop)
        try:
            exec(self._loop.__code__, self.__globals)
        except KeyboardInterrupt:
            self.shutdown(1)
        except:
            sys.stdout.flush()
            exc_type, exc_obj, tb = sys.exc_info()
            tbs = traceback.extract_tb(tb)
            print('Error while running loop: %s' % traceback.format_exception_only(exc_type, exc_obj)[0].strip(), file=sys.stderr)
            for s in tbs.format()[1:]:
                print(s, file=sys.stderr)
            if not self._ignore_exceptions:
                self.shutdown(1)
    
    async def _run_loop_async(self):
        while True:
            if self._should_stop.is_set():
                return
            try:
                await self._loop()
            except asyncio.CancelledError:
                raise
            except KeyboardInterrupt:
                self.shutdown(1)
            except:
                sys.stdout.flush()
                exc_type, exc_obj, tb = sys.exc_info()
                tbs = traceback.extract_tb(tb)
                print('Error while running loop: %s' % traceback.format_exception_only(exc_type, exc_obj)[0].strip(), file=sys.stderr)
                for s in tbs.format()[1:]:
                    print(s, file=sys.stderr)
                if not self._ignore_exceptions:
                    self.shutdown(1)
    
    async def _shutdown(self):
        """
        Cleanup handler. This function should be called only once.
        """
        
        self._should_stop.set()
        current=asyncio.current_task() # so it doesn't cancel itself
        for task in asyncio.Task.all_tasks():
            if task!=current:
                task.cancel()
            
        try:
            if asyncio.iscoroutinefunction(self._on_shutdown):
                await self._on_shutdown()
            else:
                self._on_shutdown()
        except:
            sys.stdout.flush()
            exc_type, exc_obj, tb = sys.exc_info()
            tbs = traceback.extract_tb(tb)
            print('Error ignored while running on_shutdown: %s' % traceback.format_exception_only(exc_type, exc_obj)[0].strip(), file=sys.stderr)
            for s in tbs.format()[1:]:
                print(s, file=sys.stderr)
    

    def shutdown(self,exit_code=0):
        """
        Shutdown the program.
        :param int exit_code: Optional. Program exit code (if you don't know \
        what it is, leave it to the default value)
        :return: None
        """
        self._should_stop.set()
        self._event_loop.stop()
        self._exit_code=exit_code

