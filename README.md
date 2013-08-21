dokku-controller
================

Keep track of your seperate dokku installations and allow you to restart/delete apps over a nice rest API.

Roadmap
-------

- Load balancing (with dotcloud/hipache)
- Push directly to the controller and let the controller manage on which dokku to deploy
- Health check, move app if a dokku is down
- Service Gateway (puppet scripts + provisioning API).

Publish information from dokku
------------------------------

Upload this file:

publish.sh
```bash
 docker ps | sed 1d | awk '{ print $2 }' | python -c 'import sys; print sys.stdin.read().replace("app/", "").replace(":latest",""),' | python -c 'import json; import sys; import socket; print json.dumps({ socket.gethostname(): [app for app in sys.stdin.read().split("\n") if app]})'
```

Run this cronjob every few minutes:
```bash
sudo /home/ubuntu/publish.sh | redis-cli -h <host> -p 6379 -p <password>  -x PUBLISH app_announce
```
