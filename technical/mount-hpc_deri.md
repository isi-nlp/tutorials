
How to Mount HPC on your Local (Linux or Mac) Machine
====================

Aliya Deri and Jon May
----------

### Why?

When working on a remote cluster like HPC, many think they must give up their favorite smart IDE (e.g., Sublime, PyCharm, Eclipse) and instead use a comparatively dumb terminal editor (e.g., vim, emacs). 

*This is false!*

Instead, you can mount your remote system on your local machine. This allows you to view your files through a normal GUI (e.g., Ubuntu's Nautilus), as well as use your favorite editor.  

Note: your files are mounted, not copied over. This has a few benefits: For example, any huge files you've mounted will never take up space on your laptop!  However, if the cluster is slow, you may sometimes notice lag in your editing.

### How?


1. 
  * (Linux) On your local machine, install the sshfs package. You can find a link to the package at [this link](https://help.ubuntu.com/community/SSHFS), directly under Installation and Setup. 
  * (Mac) Install fuse and sshfs from [this link](http://osxfuse.github.io/)

2. Also on your local machine, add yourself to the fuse group. 

  * (Linux) `sudo gpasswd -a $USER fuse`. You can find out your USER variable by typing `whoami`. After this step, you may need to restart your terminal or shell to register the change.
  * (Mac) System Preferences; Users & Groups; Little '+' button, next to "New Account" select 'Group'; Full name 'fuse'; select the group from the list, tick your account name
3. Make a folder where you want to mount your files. I'll call mine hpc. 

          mkdir ~/hpc

4. Mount the folder. 

          sshfs -o idmap=user $HPC_USER@hpc-login3.usc.edu:$HPC_DIR ~/hpc

   `$HPC_USER` is, obviously, your HPC user name. `$HPC_DIR` specifies the exact path to the folder in HPC that you want mounted. (Often, your home directory in HPC is not the directory where you usually work.) For example, user Bob might use:

           sshfs -o idmap=user bob@hpc-login3.usc.edu:$/auto/nlg-05/bob ~/hpc

   You should be prompted for your password unless you have passwordless ssh set up.

5. Sanity check: Did it work? Try it out! On your local terminal, navigate to `~/hpc`. Does it shows the files
   on HPC? Try creating a test file, then ssh into HPC and check if it actually appeared. Delete the file over ssh, and it will disappear in
   `~/hpc`. Open a file browser and drag some files from `~/hpc` to your desktop.

   Even more important: Try running an IDE on the HPC files from `~/hpc`.

6. To unmount `~/hpc`, simply run:

           fusermount -u ~/hpc


7. So you don't have to remember all those commands, let's add this to your `.bashrc`. 

            alias hpcmount='fusermount -u ~/hpc ; 
            sshfs -o idmap=user $HPC_USER@hpc-login3.usc.edu:$HPC_DIR ~/hpc ; '


8. Close and reopen your terminal. Type `hpcmount` and you will automatically unmount `~/hpc` (in case it was already mounted) and remount it. Congrats!


### Some more notes


* When you run a command from `~/sim/hpc` (your mounted folder), it will run on your local machine. That is, you cannot submit jobs to HPC from `~/sim/hpc`; if you have Python 2.7 running on your machine and Python 2.6 on HPC, running a script from `~/sim/hpc` will run Python 2.7.

However, running major, data-intensive jobs on your `~/sim/hpc` **will** waste HPC CPU and slow everyone down due to data transfer across the network!  It's a good idea to open another terminal tab, SSH into HPC, and run and submit jobs from the terminal there.

In short: Your mounted folder is for editing, not for running code!

* At some point you might turn off your computer without actually unmounting `~/sim/hpc`. If you leave an IDE open, it might get confused and try to save the open files in the (now empty) `~/sim/hpc` folder. The next time you run hpcmount, you will get a "nonempty" error.

Assuming you saved your files, you can just delete the files in `~/sim/hpc` (or even `~/sim/hpc` itself and `mkdir` again). But do doublecheck what you're deleting--if somehow you delete everything in `~/sim/hpc` while it's mounted, you will lose everything on HPC as well!

* It's useful to also alias your HPC SSHing as well. To use hpcssh from terminal, add this to your `.bashrc`:

      alias hpcssh='ssh $HPC_USER@hpc-login3.usc.edu ; '

  SSH provides functionality to do this kind of thing directly. Add these lines to `.ssh/config` (on your user machine):

      Host hpc hpc.usc.edu
      HostName hpc-login3.usc.edu
      User $HPC_USER

  Now if you type `ssh hpc` or `ssh hpc.usc.edu` ssh will interpret this as `ssh $HPC_USER@hpc-login3.usc.edu`

* If you're having trouble, you can try contacting Aliya at `aderi@isi.edu`. You can also find more detailed and technical descriptions by starting [here](https://help.ubuntu.com/community/SSHFS).
