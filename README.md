# tournament
A simple app that sets up and manages matches between game players.

### Setup

Make sure that you have [VirtualBox](https://www.virtualbox.org/wiki/Download_Old_Builds) installed. **Note**: this project will not work on VirtualBox v5. The link directs you to v4.3 which is what I used for this project.

### From a terminal (OS X)

```
vagrant up default --provider=virtualbox
```

**Note**: You may see an error similar to:

```
The provider 'VirtualBox' could not be found, but was requested to
back the machine 'default'. Please use a provider that exists.
```

If you see this, look for a folder in your current working dir that looks like this: ```.vagrant/machines/<machine_name>/VirtualBox```. Simple change ```VirtualBox``` to virtualbox (or whatever spelling you provided to --provider) and the issue should be fixed.

```
username   $ vagrant ssh 
vagrant-vm $ createdb tournament
vagrant-vm $ psql
vagrant   => \c tournament
vagrant   => \i /vagrant/tournament/tournament.sql
```

### Run tests

```
$ python path/to/tournament_test.py
```
