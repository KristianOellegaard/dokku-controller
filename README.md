dokku-controller
================

Keep track of your seperate dokku installations and allow you to restart/delete apps over a nice rest API.

Roadmap
-------

- Load balancing (with [dotcloud/hipache](https://github.com/dotcloud/hipache))
- Push directly to the controller and let the controller manage on which dokku to deploy
- Health check, move app if a dokku is down
- Service Gateway ([puppet scripts](https://github.com/KristianOellegaard/puppet-postgresql) + provisioning API).

Publish information from dokku
------------------------------

[Use the agent](https://github.com/KristianOellegaard/dokku-controller-agent)
