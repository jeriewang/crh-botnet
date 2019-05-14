import asyncio, inspect, textwrap, traceback, sys, socket, re, signal, os, logging
from typing import Union
from .network import RobotNetwork


def noop(): pass


class Robot:
    def __init__(self):
        self.network = RobotNetwork(self)
        self.id = None
        logger = logging.getLogger('Robot')
        
        file_handler = logging.FileHandler('/var/tmp/crh_botnet.log')
        stream_handler = logging.StreamHandler()
        
        formatter = logging.Formatter('%(asctime)s.%(msecs).3d %(levelname)-5s    %(message)s', datefmt='%H:%M:%S')
        
        file_handler.setFormatter(formatter)
        stream_handler.setFormatter(formatter)
        
        logger.addHandler(file_handler)
        logger.addHandler(stream_handler)
        logger.setLevel(logging.INFO)
        self._logger = logger
    
    def run(self, namespace: dict, id: int = None, looping_interval: float = 0.05, ignore_exceptions=False, offline=False, debug=False):
        """
        Runs the main event loop. This function must be called only once.
        It should be placed on the last line of the robot's script because
        this function does not return.
        
        :param dict namespace: The global namespace (technically, the namespace \
        that contains :func:`setup()` and :func:`loop()`) the robot program. \
        This is what makes all the magic happen. If you have \
        no idea what it is, use :func:`globals()`.
        :param id: The robot's ID. If the program is running on an robotics \
        lab's Raspberry Pi, it is automatically calculated. This is not \
        necessary if the robot is operating under offline mode.
        :param float looping_interval: Looping interval \
        in seconds. Defaults to :code`0.05` (that is, the loop runs 20 times per \
        second).
        :param bool ignore_exceptions: Whether or not the robot should continue \
        running if an exception occurs when the loop is running. Note that it\
        does not mean the program will continue executing the next line, but\
        will run the next iteration of the loop instead. Defaults to :code:`False`.\
        It is dangerous to enable and use only if you are confident that your\
        program can recover from unhandled exceptions. Regardless of this value,\
        KeyboardInterrupt (ctrl-c) will always shutdown the robot.
        :param bool offline: Whether the robot should operate offline. That is,\
        if offline is set to True, the robot will not attempt to connect to the \
        network. You also don't have to supply a robot ID if this is set to True.
        :param bool debug: Whether to enable debugging mode or not, default to \
        False. This will enable the verbose mode, good to enable if you ever \
        wonder what's going on inside the robot.
        """
        if debug:
            self._logger.setLevel(logging.DEBUG)
        
        self._logger.info('Initializing the robot...')
        
        if offline:
            self._logger.info('Running under offline mode.')
            self.id = 0
        else:
            self._logger.debug("Attempting to deduct robot's ID from hostname...")
            hostname = socket.gethostname()
            match = re.fullmatch(r'^choate-robotics-rpi-(\d{2})$', hostname)
            if match:
                self.id = int(match.group(1))
                self._logger.debug("Calculated ID is %d." % self.id)
            else:
                if isinstance(id, int):
                    self._logger.debug("Cannot calculate ID. Using user supplied ID %d." % id)
                    self.id = id
                else:
                    raise ValueError("ID cannot be calculated. Please specify an ID.")
        
        self._event_loop = asyncio.get_event_loop()
        self._event_loop.set_exception_handler(self._exception_handler)
        self._should_stop = asyncio.Event()
        self._exit_code = 0
        self._ignore_exceptions = False
        self._debug = debug
        
        self.__globals = namespace
        self._looping_interval = looping_interval
        self._ignore_exceptions = ignore_exceptions
        
        signal.signal(signal.SIGTERM, self._signal_handler)
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGQUIT, self._signal_handler)
        
        if 'setup' in self.__globals:
            self._setup = self.__globals['setup']
            self._logger.debug('Setup function collected from the user namespace.')
        else:
            self._setup = noop
            self._logger.debug('Setup function not found in the user namespace. Using noop.')
        
        if asyncio.iscoroutinefunction(self._setup):
            print('Setup function must not be async')
            sys.exit(1)
        if not offline:
            self._logger.info('Attempting to connect to the RobotNetwork...')
            self.network.connect()
            if self.network.is_connected:
                self._logger.info('Connected to the network')
        
        self._logger.debug('Running setup.')
        self._run_setup()
        
        if 'on_message' in self.__globals:
            self._on_message = self.__globals['on_message']
            self._logger.debug('Message handler collected from the user namespace.')
        else:
            self._on_message = noop
            self._logger.debug("Message handler not found in the user namespace. Using noop.")
        
        if 'on_shutdown' in self.__globals:
            self._on_shutdown = self.__globals['on_shutdown']
            self._logger.debug('Shutdown handler collected from the user namespace.')
        else:
            self._on_shutdown = noop
            self._logger.debug("Shutdown handler not found in the user namespace. Using noop.")
        
        if 'loop' in self.__globals:
            self._loop = self.__globals['loop']
            self._logger.debug('Loop function collected from the user namespace.')
        else:
            self._loop = noop
            self._logger.debug("Loop function not found in the user namespace. Using noop.")
        
        if asyncio.iscoroutinefunction(self._loop):
            asyncio.ensure_future(self._run_loop_async())
        else:
            self._event_loop.call_soon(self._run_loop)
        
        self._logger.debug('Loop runner scheduled.')
        
        if not offline:
            asyncio.ensure_future(self._poll())
            self._logger.debug('Polling scheduled.')
        
        try:
            self._event_loop.set_debug(self._debug)
            self._logger.debug('Starting the event loop...')
            self._event_loop.run_forever()
        finally:
            try:
                self._logger.debug("Running final cleanup.")
                self._event_loop.run_until_complete(self._shutdown())
            finally:
                try:  # retrieve all CancelledError
                    self._event_loop.run_until_complete(asyncio.gather(*asyncio.Task.all_tasks()))
                except asyncio.CancelledError:
                    pass
                self._logger.debug('Event loop closed.')
                self._event_loop.close()
                self._logger.debug("Robot exit.")
                logging.shutdown()
                sys.exit(self._exit_code)
    
    def set_looping_interval(self, interval: float) -> None:
        """
        Set the looping interval.
        
        :param interval: float, looping interval in seconds.
        :return: None
        """
        
        self._looping_interval = interval
    
    async def _poll(self):
        is_handler_async = asyncio.iscoroutinefunction(self._on_message)
        while True:
            if self._should_stop.is_set():
                return
            try:
                self._logger.debug('Polling.')
                msgs = await self.network.coro.poll()
                for msg in msgs:
                    self._logger.debug('Running message handler for %s' % repr(msg))
                    try:
                        if is_handler_async:
                            await self._on_message(msg)
                        else:
                            self._on_message(msg)
                    except:
                        sys.stdout.flush()
                        exc_type, exc_obj, tb = sys.exc_info()
                        tbs = traceback.extract_tb(tb)
                        print('Error while running on_message: %s' % traceback.format_exception_only(exc_type, exc_obj)[0].strip(), file=sys.stderr)
                        for s in tbs.format()[1:]:
                            print(s, file=sys.stderr)
                        if not self._ignore_exceptions:
                            self.shutdown(1)
            except asyncio.CancelledError:
                raise
            except KeyboardInterrupt:
                self.shutdown(1)
            except:
                if self._debug:
                    print('Error polling:', file=sys.stderr)
                    print(traceback.format_exc(), file=sys.stderr)
                else:
                    print('Error Polling', file=sys.stderr)
                # TODO: Handle specific connection errors
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
        
        self._logger.debug('Variables injected into the user global namespace: %s' % ' '.join(ns.keys()))
        self.__globals.update(ns)
    
    def _run_loop(self):
        if self._should_stop.is_set():
            return
        if self._looping_interval > 0:
            self._logger.debug('Next iteration of loop scheduled for %0.3fms later.' % (self._looping_interval * 1000))
            self._event_loop.call_later(self._looping_interval, self._run_loop)
        else:
            self._logger.debug('Next iteration of loop scheduled ASAP.')
            self._event_loop.call_soon(self._run_loop)
        try:
            self._logger.debug('Running loop.')
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
                self._logger.debug('Running loop.')
                await self._loop()
                if self._looping_interval > 0:
                    self._logger.debug('Sleeping for %0.3fms.' % (self._looping_interval * 1000))
                    await asyncio.sleep(self._looping_interval)
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
    
    def __getattr__(self, item: str):
        if item.startswith('_'):  # Don't expose private variables
            raise AttributeError("The robot does not have attribute %s.", item)
        try:
            return getattr(self.network, item)
        except AttributeError:
            raise AttributeError("The robot does not have attribute %s.", item)
    
    async def _shutdown(self):
        """
        Cleanup handler. This function should be called only once.
        """
        
        self._should_stop.set()
        current = asyncio.current_task()  # so it doesn't cancel itself
        for task in asyncio.Task.all_tasks():
            if task != current:
                task.cancel()
        try:
            self._logger.debug('Running the shutdown handler.')
            if asyncio.iscoroutinefunction(self._on_shutdown):
                await self._on_shutdown()
            else:
                self._on_shutdown()
            if self.network.is_connected:
                self._logger.debug('Disconnecting from the network.')
                await self.network.coro.disconnect()
        except:
            sys.stdout.flush()
            exc_type, exc_obj, tb = sys.exc_info()
            tbs = traceback.extract_tb(tb)
            print('Error ignored while running on_shutdown: %s' % traceback.format_exception_only(exc_type, exc_obj)[0].strip(), file=sys.stderr)
            for s in tbs.format()[1:]:
                print(s, file=sys.stderr)
    
    def _exception_handler(self, loop: asyncio.AbstractEventLoop, context: dict):
        """
        This function is intended for missed exceptions in random places.
        """
        try:
            if 'exception' in context:
                exc = context['exception']
                print('Uncaught exception %s' % exc, file=sys.stderr)
                print(traceback.format_tb(exc.__traceback__), file=sys.stderr)
                if not self._ignore_exceptions:
                    self.shutdown(1)
            else:
                print('Uncaught exception with unknown type ignored', file=sys.stderr)
        except:
            print('Something went seriously wrong. Error in error handler.', file=sys.stderr)
            print(context, file=sys.stderr)
            print(traceback.format_exc(), file=sys.stderr)
    
    def _signal_handler(self, signum, frame):
        self.shutdown(1)
    
    def shutdown(self, exit_code=0):
        """
        Shutdown the robot cleanly.
        
        :param int exit_code: Optional. Program exit code (if you don't know \
        what it is, leave it to the default value.)
        :return: None
        """
        self._should_stop.set()
        self._event_loop.stop()
        self._exit_code = exit_code
    
    def emergency_shutdown(self, exit_code=1):
        """
        Shutdown the robot immediately. All pending tasks will be discarded.
        
        :param int exit_code: Optional. Program exit code (if you don't know \
        what it is, leave it to the default value.)
        :return: None
        """
        self._logger.critical('Emergency shutdown commenced. Abandoning all hopes.')
        logging.shutdown()
        os._exit(exit_code)


__all__ = ['Robot']
