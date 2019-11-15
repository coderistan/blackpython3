# coding:utf-8
# @coderistan
# WMI yardımıyla process watcher
# gereklilikler: pywin32,wmi

import wmi
import sys

PY = sys.version_info.major

def optimizePy():
    if(PY == 2):
        reload(sys)
        sys.setdefaultencoding("utf-8")

def log_to_file(message):
    fd = open("process_monitor_log.csv", "ab")

    if(PY == 2):
        fd.write("%s\r\n" % message)

    else:
        fd.write(bytes("{}\r\n".format(message),"utf-8"))

    fd.close()
    return

def log_message(*args):
    if(PY == 2):
        log = "%s,%s,%s,%s,%s,%s,%s"
        return log%tuple(args)
    else:
        return "{},{},{},{},{},{},{}".format(*args)


log_to_file("Time,User,Executable,CommandLine,PID,Parent PID,Privileges")
c = wmi.WMI()
process_watcher = c.CIM_Process.watch_for("creation")

while True:
    try:
        new_process = process_watcher()
        proc_owner= new_process.GetOwner()
        proc_owner= "%s\\%s" % (proc_owner[0],proc_owner[2])
        create_date= new_process.CreationDate
        executable= new_process.ExecutablePath
        cmdline= new_process.CommandLine
        pid= new_process.ProcessId
        parent_pid= new_process.ParentProcessId
        privileges = "N/A"
        process_log_message = log_message(create_date,proc_owner, executable, cmdline, pid, parent_pid, privileges)
        print(process_log_message)
        log_to_file(process_log_message)
    except Exception as e:
        print(str(e))
