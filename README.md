dokku-controller
================

Keep track of your seperate dokku installations and allow you to restart/delete apps over a nice rest API.

Features
--------

- Configure environment on dokku over a REST API
- Restart and delete your dokku apps over a REST API
- Configures redis for use with [dotcloud/hipache load balancer](https://github.com/dotcloud/hipache)

Roadmap
-------

- Push directly to the controller and let the controller manage on which dokku to deploy
- Health check, move app if a dokku is down
- Service Gateway ([puppet scripts](https://github.com/KristianOellegaard/puppet-postgresql) + provisioning API).

Publish information from dokku
------------------------------

[Use the agent](https://github.com/KristianOellegaard/dokku-controller-agent)


Setup
=====

Controller
----------
pip install -r requirements.txt
honcho start


Dokku
-----
(from controller)
```
cat ~/.ssh/id_rsa.pub | ssh ubuntu@<server> "sudo gitreceive upload-key dokku-controller"
```
Furthermore, add the ssh public key, of the user that is running the controller to the user ```ubuntu``` on every dokku instance.

Add the following to sudoers file:
```
ubuntu  ALL=(root) NOPASSWD: /usr/bin/docker
```
Make sure the agent is running
