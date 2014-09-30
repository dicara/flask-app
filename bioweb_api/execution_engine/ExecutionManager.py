'''
Copyright 2014 Bio-Rad Laboratories, Inc.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

@author: Dan DiCara
@date:   Jun 1, 2014
'''

#===============================================================================
# Imports
#===============================================================================
from concurrent.futures import ProcessPoolExecutor
import multiprocessing

#===============================================================================
# Class
#===============================================================================
class ExecutionManager(object):
    """
    This class is intended to be a singleton.
    """
    _INSTANCE  = None
    # List of futures for submitted jobs.
    _JOB_QUEUE = {} 
    
    #===========================================================================
    # Constructor
    #===========================================================================
    def __init__(self):
        # Enforce that it's a singleton
        if self._INSTANCE:
            raise Exception("%s is a singleton and should be accessed through the Instance method." % self.__class__.__name__)
        cpu_count = multiprocessing.cpu_count()
        self._pool = ProcessPoolExecutor(max_workers=cpu_count)
        
    def __del__(self):
        self._pool.shutdown()
    
    @classmethod
    def Instance(cls):
        if not cls._INSTANCE:
            cls._INSTANCE = ExecutionManager()
        return cls._INSTANCE
    
    #===========================================================================
    # Simple execution functions
    #===========================================================================
    def add_job(self, uuid, fn, callback=None):
        """
        Submit new job to job queue.
        """
        future = self._pool.submit(fn)
        if callback:
            future.add_done_callback(callback)
        self._JOB_QUEUE[uuid] = future
        
    def done(self, uuid):
        """
        Is this job done running.
        """
        return self._get_future(uuid).done()
    
    def running(self, uuid):
        """
        Is this job running.
        """
        return self._get_future(uuid).running()
    
    def result(self, uuid):
        """
        :raise exception: If run raised exception.
        """
        future = self._get_future(uuid)
        if future.running():
            return None
        return future.result()
    
    def cancel(self, uuid):
        """
        Cancel job.
        """
        if self.done(uuid) or self.running(uuid):
            return False
        else:
            return self._get_future(uuid).cancel()
    
    def _get_future(self, uuid):
        return self._JOB_QUEUE[uuid]
    
#===========================================================================
# Ensure the initial instance is created.
#===========================================================================    
ExecutionManager.Instance()

#===============================================================================
# Run Main
#===============================================================================
class my_add(object):
    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z
        
    def __call__(self):
        time.sleep(2)
        return self.x+self.y+self.z

if __name__ == "__main__":
    from uuid import uuid4
    import time

    em = ExecutionManager.Instance()
        
    uuid = str(uuid4())
    em.add_job(uuid, None, my_add(1,2,3))
    print em.job_result(uuid)
    i = 0
    while  em.job_running(uuid):
        print i 
        i += 1
        time.sleep(1)
    print em.job_result(uuid)
