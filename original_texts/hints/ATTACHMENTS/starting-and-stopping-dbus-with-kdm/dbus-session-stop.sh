#!/bin/bash

retcode=0;

userid=$1
userproperties=$(getent passwd | grep -m 1 -E "^$userid")
homedir=$(echo $userproperties | cut -d ":" -f 6);
gidnr=$(echo $userproperties | cut -d ":" -f 4);
uidnr=$(echo $userproperties | cut -d ":" -f 3);

if [ -d $homedir ]; then
	
	if [ -f $homedir/.dbus-session ]; then
	    . $homedir/.dbus-session
	    if [ -n "$DBUS_SESSION_BUS_PID" ]; then
		if [ $(id -u) -eq 0 ]; then
		    sudo -H -u $userid sh -c "kill $DBUS_SESSION_BUS_PID"
		    retcode=$?
		    rm $homedir/.dbus-session
		elif [ $(id -u) -eq $uidnr ]; then
		    kill -SIGTERM $DBUS_SESSION_BUS_PID
		    retcode=$?
		    rm $homedir/.dbus-session
		fi;
	    fi
	fi;	
fi;
    	

if [ $retcode -ne 0 ]; then
    echo "An error with dbus ($retcode)."
fi;

exit $retcode
