# Freedom Fighting Mode (FFM)

FFM is a hacking harness that you can use during the post-exploitation phase of a red-teaming
engagement. The idea of the tool was derived from a 
[2007 conference](https://conference.hitb.org/hitbsecconf2007kl/materials/D1T1%20-%20The%20Grugq%20-%20Meta%20Antiforensics%20-%20The%20HASH%20Hacking%20Harness.pdf) 
from @thegrugq.

It was presented at [SSTIC 2018](https://www.sstic.org) and the accompanying slide deck is 
available at [this url](http://manalyzer.org/static/talks/SSTIC2018.pptx). If you're not familiar
with this class of tools, it is strongly advised to have a look at them to understand what a
hacking harness' purpose is. All the comments are included in the slides.

This project is distributed under the terms of the 
[GPL v3 License](https://www.gnu.org/licenses/gpl.html).

## Usage

The goal of a hacking harness is to act as a helper that automates common tasks during the 
post-exploitation phase, but also safeguards the user against mistakes they may make.

It is an instrumentation of the shell. Run `./ffm.py` to activate it and you can start working
immediately. There are two commands you need to know about:

- Type `!list` to display the commands provided by the harness.
- Type `SHIFT+TAB` to perform tab completion on the local machine. This may be useful if you're
ssh'd into a remote computer but need to reference a file that's located on your box.

## List of features

This hacking harness provides a few features that are described below. As they are described, 
the design philosophy behind the tool will also be introduced. It is not expected that all
the commands implemented in FFM will suit you. Everyone has their own way of doing things, and
tuning the harness to your specific need is likely to require you to modify some of the code
and/or write a few plugins. A lot of effort went into making sure this is a painless task.

### Commands

* `!os` is an extremely simple command that just runs `cat /etc/*release*` to show what OS
the current machine is running. It is probably most valuable as a demonstration that in the
context of a hacking harness, you can define aliases that work across machine boundaries.
SSH into any computer, type `!os` and the command will be run. This plugin is located in 
`commands/replacement_commands.py` and is a good place to start when you want to learn about
writing plugins.
* `!download [remote file] [local path]` gets a file from the remote machine and copies it
locally through the terminal. This command is a little more complex because more stringent
error checking is required but it's another plugin you can easily read to get started.
You can find it in `commands/download_file.py`. Note that it requires `xxd` or `od` on the remote
machine to function properly.
* `!upload [local file] [remote path]` works exactly the same as the previous command, 
except that a local file is put on the remote machine. It requires `xxd`, and the utility is not present by default on CentOS. Expect
the plugin to be rewritten with `od` in the near future.
* `!pty` spawns a TTY, which is something you don't want in most cases because it tends to 
leave forensics evidence. However, some commands (`sudo`) or exploits require a TTY to run
in so this is provided as a convenience. `UNSET HISTFILE` is passed to it as soon as it
spawns.
* `!py [local script]` executes a local Python script on the remote machine, and does so
*entirely in memory*. Check out my 
[other repository](https://github.com/JusticeRage/freedomfighting) for scripts you might
want to use. This commands uses a multiline syntax with `<<`, which means that pseudo-shells
that don't support it (Weevely is a good example of that) will break this command quite badly.

### Processors

Conceptually, commands (as described above) are used to generate some bash which is forwarded
to the shell. They can perform more complex operations by capturing the shell's output and 
generating additional instructions based on what is returned.
Processors are a little different as they are rather used to rewrite data circulating between
the user and the underlying bash process. While it is true that any processor could be rewritten
as a command, it seemed a little cleaner to separate the two. Input processors work on whatever
is typed by the user once they press the `ENTER` key, and output processors can modify anything
returned by the shell.

* A good processor example can be found in `processors/ssh_command_line.py`. All it does is add
the `-T` option to any SSH command it sees if it is missing. Be sure to check out its simple 
code if you are interested in writing a processor.
* Another input processor present in the framework, `processors/assert_torify.py`, contains a
blacklist of networking commands (`ssh`, `nc`) and blocks them if they don't seem to be proxied
through a tool such as `torify`. The harness does its best to only bother the user if it seems
like the command is being run on the local machine. Obviously this should not be your only
safeguard against leaking your home IP address.
* Finally, `processors/sample_output_processor.py` is a very simple output processor that 
highlights in red any occurrence of the word "password". As it's quite useless, it's not enabled
in the framework but you can still use it as a starting point if you want to do something more 
sophisticated.

## Known issues

`CTRL+R` is not implemented yet and we all miss it dearly.

There is currently no way to run ELFs in memory on a remote machine. This is high on the
ToDo list.

More problematic is the fact that the framework hangs from time to time. In 99% of the cases,
this happens when it fails to detect that a command it launched has finished running. Usually,
this means that the command prompt of the machine you're logged into could not be recognized
as such. In that case, you can try improving the regular expression located at the very
beginning of the file `ffm.py`, or log into that same machine with `ssh -T` as there won't be
any problematic prompt anymore. When the framework hangs, there's not much you can do to unhang
it beyond `pkill -f ffm.py` as there is no timeout mechanism at the moment (but there will be
at some point).

## Closing statement

I think I've covered everything about this tool. Again, it's a little different from what I
usually release as most people will probably need to modify it before it can be valuable to
them.

Many plugins have yet to be written, so be sure to share back any improvements you make to
FFM. Feel free to open issues not only for bugs, but also if you're trying to do something
and can't figure out how; this way I'll be able to improve the documentation for everyone.

## Miscellaneous

### Donations
The project is 100% free. I do like Bitcoins though, so if you want to send some my way, 
here's an address you can use: ```1PUeq8FfyqvyJqA1Eb23qHrnkdPknt4aKF```
Feel free to drop me a line if you donate, so I can thank you personally!

### Contact
[![](https://manalyzer.org/static/mail.png)](justicerage@manalyzer[.]org)
[![](https://manalyzer.org/static/twitter.png)](https://twitter.com/JusticeRage)
[![](https://manalyzer.org/static/gpg.png)](https://pgp.mit.edu/pks/lookup?op=vindex&search=0x40E9F0A8F5EA8754)