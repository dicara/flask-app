#!/usr/local/bin/python2.7
# encoding: utf-8

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
import sys
import os
import getpass
import platform
import logging
import time
import signal
import csv
import tornado.options

from argparse import ArgumentParser
from argparse import RawDescriptionHelpFormatter
from datetime import datetime
from tornado.wsgi import WSGIContainer
from tornado.ioloop import IOLoop
from tornado.web import FallbackHandler, Application, RequestHandler

from . import app, PORT, HOME_DIR, TORNADO_LOG_FILE_PREFIX, \
    TARGETS_UPLOAD_FOLDER, PROBES_UPLOAD_FOLDER, RESULTS_FOLDER, REFS_FOLDER, \
    DEV
from utilities import io_utilities

#===============================================================================
# Class private variables
#===============================================================================
__all__     = []
__version__ = 0.1
__date__    = '2014-05-28'
__updated__ = '2014-05-28'

#===============================================================================
# Public global variables
#===============================================================================
RUNINFO_FILENAME  = "run_info.txt"
PORT_HEADER       = "port"
PID               = "pid"
USER              = "user"
MACHINE           = "machine"
START_DATETIME    = "start_datetime"
TIME_FORMAT       = "%Y_%m_%d__%H_%M_%S"
HEADER            = [ MACHINE, PID, PORT_HEADER, USER, START_DATETIME]

# Mode for reading/writing server info file is rw:rw:r
MODE = io_utilities.get_python_mode([6,6,4])

#===============================================================================
# Classes
#===============================================================================
class MainHandler(RequestHandler):
    def get(self):
        self.write("This message comes from Tornado ^_^")

#===============================================================================
# Main
#===============================================================================
def main(argv=None): # IGNORE:C0111
    '''Command line options.'''
    if argv is None:
        argv = sys.argv
    else:
        sys.argv.extend(argv)

    program_name = os.path.basename(sys.argv[0])
    program_version = "v%s" % __version__
    program_build_date = str(__updated__)
    program_version_message = '%%(prog)s %s (%s)' % (program_version, 
                                                     program_build_date)
    
    program_shortdesc = ''' 
  Start, stop, restart and check status of rest API. Settings for this tool 
  are contained in the default_settings.py included in the deployed source 
  code. However, these settings can be overridden by setting a FLASKR_SETTINGS 
  environment variable that points to a custom settings file.
  '''

    program_license = '''%s

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

USAGE
''' % (program_shortdesc)

    try:
        # Setup argument parser
        parser = ArgumentParser(description=program_license, 
                                formatter_class=RawDescriptionHelpFormatter)
        parser.add_argument("-v", "--verbose", dest="verbose", action="count", 
                            help="set verbosity level [default: %(default)s]")
        parser.add_argument('-V', '--version', action='version', 
                            version=program_version_message)
        # Either start, stop, restart, or check status of the server, 
        # but you can only do one per invocation of this script.
        group = parser.add_mutually_exclusive_group(required=True)
        group.add_argument("-r", "--restart", action="store_true", 
                           help="Restart the server [default: %(default)s]")
        group.add_argument("-s", "--start", action="store_true", 
                           help="Start the server [default: %(default)s]")
        group.add_argument("-x", "--stop", action="store_true", 
                           help="Stop the server [default: %(default)s]")
        group.add_argument("-t", "--status", action="store_true", 
                           help="Show server status [default: %(default)s]")
        
        flags = ["-V", "--version", 
                 "-r", "--restart", 
                 "-s", "--start", 
                 "-x", "--stop",
                 "-t", "--status",
                ]

        # Process arguments
        args = parser.parse_args()

        verbose        = args.verbose
        restart_server = args.restart
        start_server   = args.start
        stop_server    = args.stop
        show_status    = args.status
        
        logging_level = logging.WARNING
        if verbose > 0 or DEV:
            logging_level = logging.INFO
        logging.basicConfig(stream=sys.stderr, format='%(asctime)s::%(levelname)s  %(message)s', datefmt='%Y-%m-%d %I:%M:%S %p', level=logging_level)

    except KeyboardInterrupt:
        ### handle keyboard interrupt ###
        return 0
    except Exception, e:
        indent = len(program_name) * " "
        sys.stderr.write(program_name + ": " + repr(e) + "\n")
        sys.stderr.write(indent + "  for help use --help")
        return 2
    
    io_utilities.safe_make_dirs(HOME_DIR)
    io_utilities.safe_make_dirs(TARGETS_UPLOAD_FOLDER)
    io_utilities.safe_make_dirs(PROBES_UPLOAD_FOLDER)
    io_utilities.safe_make_dirs(RESULTS_FOLDER)
    io_utilities.safe_make_dirs(REFS_FOLDER)

    # current_info: currently running process machine, pid, port, user, and 
    #               datestamp
    # running_info_list: info for each running server instance in 
    #                    RUNINFO_FILENAME file
    # running_info: populated if an instance of server with current_info machine 
    #               and port is in running_info_list
    current_info      = get_current_info() 
    running_info_list = read_running_info_list()
    running_info      = is_running(current_info, running_info_list)
    
    # Clean up command line arguments - tornado parses it and will not recognize 
    # these.
    for flag in flags:
        if flag in sys.argv:
            sys.argv.remove(flag)
    
    # Start, stop, restart, or show status
    if start_server:
        if running_info:
            sys.stderr.write("Cannot start server: a server instance on " \
                             "this machine %s and port %s is currently " \
                             "running.\n" % (current_info[MACHINE], 
                                             current_info[PORT_HEADER]))
        else:
            start(current_info)
    elif stop_server:
        if running_info:
            stop(current_info, running_info_list, running_info)
        else:
            sys.stderr.write("Cannot stop server: could not find server " \
                             "instance on this machine %s and port %s.\n" % \
                             (current_info[MACHINE], current_info[PORT_HEADER]))
    elif restart_server:
        if running_info: 
            # Only restart if killing the running instance succeeded
            if stop(current_info, running_info_list, running_info):
                start(current_info)
        else:
            start(current_info)
    elif show_status:
        print_status(current_info, running_info_list)

#===============================================================================
# Start, stop, and show status
#===============================================================================
def start(current_info):
    '''
    Start an instance of the server. 
    '''
    io_utilities.safe_make_dirs(os.path.dirname(TORNADO_LOG_FILE_PREFIX))
    tornado.options.options.log_file_prefix = TORNADO_LOG_FILE_PREFIX
    tornado.options.parse_command_line()
    
    logging.info("Starting up server on machine %s and port %s at %s." % 
                 (current_info[MACHINE], current_info[PORT_HEADER], 
                  time.strftime("%I:%M:%S")))
    
    tr = WSGIContainer(app)
    application = Application([ (r"/tornado", MainHandler),
                                (r".*", FallbackHandler, dict(fallback=tr)),
                              ])
    application.listen(PORT)
    
    # Gracefully handle server shutdown.
    signal.signal(signal.SIGTERM, sig_handler)
    signal.signal(signal.SIGINT, sig_handler)
    signal.signal(signal.SIGQUIT, sig_handler)
    
    # Add the current info to the running info file.
    write_running_info([current_info])
    
    IOLoop.instance().start()
    
def stop(current_info, running_info_list, running_info):
    ''' 
    Attempt to kill server instance represented by running_info. If successful, 
    remove the info entry from the RUNINFO_FILENAME file and return True. 
    Otherwise, return False.
    '''
    if running_info[USER] != current_info[USER]:
        sys.stderr.write("User that started the server (%s) must be the one " \
                         "to stop it.\n" % running_info[USER])
        return False
    else:
        os.kill(running_info[PID], signal.SIGQUIT)
        while is_running_pid(running_info[PID]):
            time.sleep(0.25)
        running_info_list.remove(running_info)
        rewrite_info(running_info_list)
        return True
    
def print_status(current_info, running_info_list):
    '''
    Display the list of running instances of server.
    '''
    running_info_this_machine = list()
    for running_info in running_info_list:
        current_info[PORT_HEADER] = running_info[PORT_HEADER]
        info = is_running(current_info, [running_info])
        if info:
            running_info_this_machine.append(info)
    running_info_other_machines = \
        filter(lambda x: x[MACHINE] != current_info[MACHINE], running_info_list)
    
    if len(running_info_this_machine) < 1 and \
       len(running_info_other_machines) < 1:
        print "\nThere aren't any instances of record that are currently "\
              "running\n"
    else:
        if len(running_info_this_machine) > 0:
            print "\nThere is/are %d currently running instance(s) on "\
                  "this machine (%s): " % (len(running_info_this_machine), \
                                      current_info[MACHINE])
            header_minus_machine = [col for col in HEADER if col != MACHINE]
            print "\t%s" % "\t".join(header_minus_machine)
            print "\t%s" % "\t".join(["====" for _ in 
                                      range(len(header_minus_machine))])
            for info in running_info_this_machine:
                print "\t%s" % "\t".join([str(info[col]) for col in 
                                          header_minus_machine])
        if len(running_info_other_machines) > 0:
            print "\nThere is/are %d currently running instance(s) on " \
                  "other machines: " % len(running_info_other_machines)
            print "\t%s" % "\t".join(HEADER)
            print "\t%s" % "\t".join(["====" for _ in range(len(HEADER))])
            for info in running_info_this_machine:
                print "\t%s" % "\t".join([str(info[col]) for col in HEADER])
        print "\n"

#===============================================================================
# Helper functions
#===============================================================================
def get_run_info_path():
    return os.path.join(HOME_DIR, RUNINFO_FILENAME)

def write_running_info(running_info_list):
    '''
    Write running info the the RUNINFO_FILENAME file.
    '''
    run_info_path = get_run_info_path()
    if os.path.isfile(run_info_path):
        with open(run_info_path, 'a') as f:
            writer = csv.DictWriter(f, HEADER, dialect='excel-tab')
            writer.writerows(running_info_list)
    else:
        with open(run_info_path, 'w') as f:
            os.chmod(run_info_path, MODE)
            writer = csv.DictWriter(f, HEADER, dialect='excel-tab')
            writer.writeheader()
            writer.writerows(running_info_list)

def rewrite_info(running_info_list):
    ''' Remove the existing info file and write new with provided info list '''
    os.remove(get_run_info_path())
    write_running_info(running_info_list)

def read_running_info_list():
    ''' 
    List of running info dicts each containing machine, pid, port, user, and 
    start datetime for each running instance of server.
    '''
    run_info_path = get_run_info_path()
    info_list = list()
    if os.path.isfile(run_info_path):
        with open(run_info_path) as f:
            reader = csv.DictReader(f, dialect='excel-tab')
            for row in reader:
                # Ignore empty lines and comment lines
                if row[HEADER[0]].strip().startswith("#"):
                    continue
                row[PORT_HEADER] = int(row[PORT_HEADER])
                row[PID]         = int(row[PID])
                info_list.append(row)
    return info_list;

def get_current_info():
    '''
    Get info about this currently running process.
    '''
    pid     = os.getpid()
    user    = getpass.getuser()
    machine = platform.node()
    date    = datetime.today().strftime(TIME_FORMAT)

    return { 
            MACHINE: machine,
            PID: pid,
            PORT_HEADER: PORT, 
            USER: user,
            START_DATETIME: date,
           }
    
def is_running(current_info, running_info_list):
    ''' 
    Determine if a server instance on the current machine and port is currently 
    running. If the current machine and port is listed in the running_info, but
    the process (PID) is dead, then remove it from running_info.
    '''
    running_info = None
    stale_info   = None
    for info in running_info_list:
        if info[MACHINE] == current_info[MACHINE] and \
           info[PORT_HEADER] == current_info[PORT_HEADER]:
            if is_running_pid(info[PID]):
                running_info = info
                break
            else:
                # Stale info exists in RUNINFO_FILENAME file
                stale_info = info
                break
            
    # Remove stale info from RUNINFO_FILENAME file
    if stale_info:
        logging.info("Removing stale info: %s" % stale_info)
        running_info_list.remove(stale_info)
        rewrite_info(running_info_list)
        
    return running_info

def is_running_pid(pid):
    ''' 
    Return true if the provided process is currently running on this machine.
    '''
    try:
        # If a process with PID is no longer running, an exception is thrown
        os.getpgid(pid)
    except OSError:
        return False
    return True

#===============================================================================
# Gracefully handle shutdown
#===============================================================================
def sig_handler(sig, frame):
    tornado.ioloop.IOLoop.instance().add_callback(shutdown)

def shutdown():
    current_info = get_current_info()
    logging.info("Shutting down server on machine %s and port %s at %s." % 
                 (current_info[MACHINE], current_info[PORT_HEADER], 
                  time.strftime("%I:%M:%S")))
    IOLoop.instance().stop()

#===============================================================================
# Run Main
#===============================================================================
if __name__ == "__main__":
    sys.exit(main())