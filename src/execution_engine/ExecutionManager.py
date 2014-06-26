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
# Imports
#===============================================================================

#===============================================================================
# Class
#===============================================================================
class ExecutionManager(object):
    """
    This class is intended to be a singleton.
    """
    _INSTANCE  = None
    # This is really a list of futures
    _JOB_QUEUE = {} #TODO: This should really be stored in DB
    #TODO: Kill all currently executing jobs and wipe from DB if api is killed.
    
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
    def add_job(self, uuid, fn):
        self._JOB_QUEUE[uuid] = self._pool.submit(fn)
        
    def job_done(self, uuid):
        return self._get_future(uuid).done()
    
    def job_running(self, uuid):
        return self._get_future(uuid).running()
    
    def job_result(self, uuid):
        """
        :raise exception: If run raised exception.
        """
        future = self._get_future(uuid)
        if future.running():
            return None
        return future.result()
    
    def _get_future(self, uuid):
        return self._JOB_QUEUE[uuid]
    
        
#===========================================================================
# Ensure the initial instance is created.
#===========================================================================    
ExecutionManager.Instance()

#===============================================================================
# Run Main
#===============================================================================
if __name__ == "__main__":
    from uuid import uuid4
    import time

    em = ExecutionManager.Instance()
    def add(x, y, z):
        time.sleep(2)
        raise Exception("failed")
        return x+y+z
        
    uuid = str(uuid4())
    em.add_job(uuid, add, 1,2,3)
    print em.job_result(uuid)
    i = 0
    while  em.job_running(uuid):
        print i 
        i += 1
        time.sleep(1)
    print em.job_result(uuid)
