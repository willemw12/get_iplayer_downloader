import logging
import traceback
from Queue import Queue, Full
from threading import Thread

from . import command

#ISSUE if TOTAL_WORKER_THREADS is 1:
#    In Queue.put(), the new worker thread blocks, if the last worker thread in the _queue is still running --> 
#    the _queue is not full and therefore Queue.put() does not time-out and a Queue.Full exception is not raised.
TOTAL_WORKER_THREADS = 2

logger = logging.getLogger(__name__)

# Singleton wrapper class (class containing a singleton)
class CommandQueue:
    
    """ Push commands in one of the available queues and execute them when popped from the queue.
        Running commands from different queues run in parallel.
    """
    class _Worker(Thread):
    
        def __init__(self, queue):
            Thread.__init__(self)
            self._queue = queue
    
        def run(self):
            while True:
                cmd, run_in_terminal_window, terminal_title = self._queue.get()
                try:
                    command.run(cmd, run_in_terminal_window=run_in_terminal_window, terminal_title=terminal_title)
                except:
                    traceback.print_exc()
                    #raise
                self._queue.task_done()

    def __init__(self):
        self._queue = _get_queue()
        
        # Start worker threads
        for i in range(TOTAL_WORKER_THREADS):
            thread = CommandQueue._Worker(self._queue)
            thread.setDaemon(True)
            thread.start()
    
    def run(self, cmd, run_in_terminal_window=False, terminal_title=None):
        try:
            # Timeout (in seconds)
            self._queue.put((cmd, run_in_terminal_window, terminal_title), True, 2)
            logger.debug("run(self, cmd): _queue size=" + str(self._queue.qsize()) + " empty=" + str(self._queue.empty()) + " full=" + str(self._queue.full()))
        except Full:
            return False
        return True

# Convenience method
def run(*args, **kwargs):
    """ Push the command on a queue and run the command when there is a process free to run the command.
    """
    return CommandQueue().run(*args, **kwargs)

def size():
    return _get_queue().qsize()

####

# Singletong queue
_queue = None

def _get_queue():
    global _queue
    #if _command_queue is None:
    if not _queue:
        _queue = Queue()
    return _queue
