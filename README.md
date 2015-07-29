# tournament
A simple app and library that sets up and manages tournament matches between game players.

At it's core, it's simply a library that uses psychopg to manage connections and make queries to a PostgreSQL database. 

### Setup

I recommend using the attached Vagrant configuration to try out the demo and library, however you can use a local Postgres instance if you prefer. These instructions will assume you're using the VM and executing scripts from the VM's terminal (denoted where you see `vagrant-vm $` below).

Make sure that you have [VirtualBox](https://www.virtualbox.org/wiki/Download_Old_Builds) installed. **NOTE**: this project will not work on VirtualBox v5. The link directs you to v4.3 which is what I used for this project.

### From a terminal (OS X)

```
$ vagrant up default --provider=virtualbox
```

**Note**: You may see an error similar to:

```
The provider 'VirtualBox' could not be found, but was requested to
back the machine 'default'. Please use a provider that exists.
```

If you see this, look for a folder in your current working dir that looks like this: ```.vagrant/machines/<machine_name>/VirtualBox```. Simple change ```VirtualBox``` to virtualbox (or whatever spelling you provided to --provider) and the issue should be fixed.

```
### Create your db and populate it with some tables ###
username   $ vagrant ssh 
vagrant-vm $ createdb tournament
vagrant-vm $ psql
vagrant   => \c tournament
vagrant   => \i /vagrant/tournament/tournament.sql
vagrant   => \q
```

### Run tests

```
vagrant-vm $ python path/to/tournament_test.py
```

### Run the demo

I put together a quick script to demo how an app might be built using the tournament library.

```
vagrant-vm $ python path/to/demo.py
```
