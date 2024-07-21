#!/bin/bash

retcode=0;

userid=$1

userproperties=$(getent passwd | grep -m 1 -E "^$userid")
homedir=$(echo $userproperties | cut -d ":" -f 6);
gidnr=$(echo $userproperties | cut -d ":" -f 4);
uidnr=$(echo $userproperties | cut -d ":" -f 3);



if [ -d $homedir ]; then

    do_log "Looking D-bus for user $userid has to be started." 
    
    #
    # do a check whether dbus-daemon is already running for this user
    # dbus-launch needs to be started by the user (uidnr)
    #
    
    if [ -f $homedir/.dbus-session ]; then
    
	# pid according to the ps command
	ps_dbus_session_pid=$(ps aux | grep -m 1 -E "^$userid.*dbus-daemon.*session.*" | grep -v "grep" | sed 's@[[:space:]][[:space:]]*@ @g' | cut -d " " -f 2)

	# the pid according the .dbus-session file	
	. $homedir/.dbus-session
	
	if [ -z "$ps_dbus_session_pid" ]; then
	
	    # dbus for this user not running
	    
	    rm $homedir/.dbus-session
	    
	elif [ $DBUS_SESSION_BUS_PID -ne $ps_dbus_session_pid ]; then
	
	    # there is something wrong:
	    
	    if [ $(id -u) -eq 0 ]; then
		sudo -H -u $userid sh -c "kill $ps_dbus_session_pid"
	    elif [ $(id -u) -eq $uidnr ]; then
		kill -SIGTERM $ps_dbus_session_pid
	    fi

	    rm $homedir/.dbus-session
	    
	fi
    
    fi
    
    if [ ! -f $homedir/.dbus-session ]; then
    
	if [ $(id -u) -eq 0 ]; then
	    sudo -u $userid -H /bin/sh -c "dbus-launch --auto-syntax > $homedir/.dbus-session"
	    retcode=$?
	    chown $uidnr:$gidnr $homedir/.dbus-session
	    chmod 0600 $homedir/.dbus-session
	    echo "D-bus started."
	elif [ $(id -u) -eq $uidnr ]; then 
	    dbus-launch --auto-syntax > $homedir/.dbus-session
	    retcode=$?
	    chmod 0600 $homedir/.dbus-session
	    echo "D-bus started."	    
	fi
	
    else
    
	do_log "D-bus not started. Already running."
	
    fi

fi;
    	

if [ $retcode -ne 0 ]; then
    echo "An error with dbus ($retcode)."
fi;

exit $retcode
