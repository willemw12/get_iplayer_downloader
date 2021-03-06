import logging
import traceback

from queue import Queue, Full
from threading import Thread

from . import command

#NOTE Thread lock if TOTAL_WORKER_THREADS is 1:
#    In Queue.put(), the new worker thread blocks, if the last worker thread in the _queue is still running --> 
#    the _queue is not full and therefore Queue.put() does not time-out and a Queue.Full exception is not raised.
TOTAL_WORKER_THREADS = 8

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
                cmd, keywords = self._queue.get()
                try:
                    command.run(cmd, **keywords)
                except:
                    traceback.print_exc()
                    #raise
                self._queue.task_done()

    def __init__(self):
        self._queue = _get_queue()
        
        # Start worker threads
        for unused_i in range(TOTAL_WORKER_THREADS):
            thread = CommandQueue._Worker(self._queue)
            thread.setDaemon(True)
            thread.start()
    
    def run(self, cmd, **keywords):
        try:
            # Timeout (in seconds)
            self._queue.put((cmd, keywords), True, 2)
            logger.debug("run(): _queue size=" + str(self._queue.qsize()) + ", empty=" + str(self._queue.empty()) + ", full=" + str(self._queue.full()))
        except Full:
            return False
        return True

# Convenience method
#def run(*arguments, **keywords):
def run(cmd, **keywords):
    """ Push the command on a queue and run the command when there is a thread free to run the command. 
        Return true if command was successfully put on the queue.
    """
    #return CommandQueue().run(*arguments, **keywords)
    return CommandQueue().run(cmd, **keywords)

def size():
    """ Return queue size. """
    return _get_queue().qsize()

####

# Singleton queue
_queue = None

def _get_queue():
    global _queue
    #if _command_queue is None:
    if not _queue:
        _queue = Queue()
    return _queue
