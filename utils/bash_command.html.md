# Execute bash commands


<!-- WARNING: THIS FILE WAS AUTOGENERATED! DO NOT EDIT! -->

## Execute bash command

We can execute any bash commands with Python `subprocess` library.

------------------------------------------------------------------------

<a
href="https://github.com/ninjalabo/llmcam/blob/main/llmcam/utils/bash_command.py#L12"
target="_blank" style="float:right; font-size:smaller">source</a>

### execute_bash_command

>  execute_bash_command (command:str)

*Execute any given bash command with parameters*

``` python
res = execute_bash_command('whoami --help')
print(res)
```

    Usage: whoami [OPTION]...
    Print the user name associated with the current effective user ID.
    Same as id -un.

          --help     display this help and exit
          --version  output version information and exit

    GNU coreutils online help: <https://www.gnu.org/software/coreutils/>
    Report any translation bugs to <https://translationproject.org/team/>
    Full documentation <https://www.gnu.org/software/coreutils/whoami>
    or available locally via: info '(coreutils) whoami invocation'

## Simulated GPT workflow

Test integrating this into current GPT framework with multiple commands:

``` python
from llmcam.core.fc import *
from llmcam.core.fn_to_schema import function_schema

tools = [function_schema(execute_bash_command)]
```

``` python
messages = form_msgs([
    ("system", "You are a helpful system administrator. Use the supplied tools to assist the user."),
    ("user", "Show the disk usage with bash command"),  
])
complete(messages, tools=tools)
```

    ('assistant',
     'Here is the current disk usage for your system:\n\n```\nFilesystem      Size  Used Avail Use% Mounted on\nnone            2.9G  4.0K  2.9G   1% /mnt/wsl\ndrivers         475G  422G   53G  89% /usr/lib/wsl/drivers\nnone            2.9G     0  2.9G   0% /usr/lib/modules\nnone            2.9G     0  2.9G   0% /usr/lib/modules/5.15.153.1-microsoft-standard-WSL2\n/dev/sdc       1007G   23G  933G   3% /\nnone            2.9G   88K  2.9G   1% /mnt/wslg\nnone            2.9G     0  2.9G   0% /usr/lib/wsl/lib\nrootfs          2.9G  2.1M  2.9G   1% /init\nnone            2.9G  848K  2.9G   1% /run\nnone            2.9G     0  2.9G   0% /run/lock\nnone            2.9G     0  2.9G   0% /run/shm\ntmpfs           4.0M     0  4.0M   0% /sys/fs/cgroup\nnone            2.9G   76K  2.9G   1% /mnt/wslg/versions.txt\nnone            2.9G   76K  2.9G   1% /mnt/wslg/doc\nC:\\\\             475G  422G   53G  89% /mnt/c\nsnapfuse        128K  128K     0 100% /snap/bare/5\nsnapfuse         74M   74M     0 100% /snap/core22/1722\nsnapfuse         74M   74M     0 100% /snap/core22/1663\nsnapfuse         92M   92M     0 100% /snap/gtk-common-themes/1535\nsnapfuse         39M   39M     0 100% /snap/snapd/21759\nsnapfuse         45M   45M     0 100% /snap/snapd/23258\nsnapfuse        132M  132M     0 100% /snap/ubuntu-desktop-installer/1276\nsnapfuse        132M  132M     0 100% /snap/ubuntu-desktop-installer/1286\n```\n\nThis output shows the size, used space, available space, and usage percentage of each filesystem.')

``` python
messages.append(form_msg("user", "show the system info with bash command"))
complete(messages, tools=tools)
```

    ('assistant',
     "Here's the system information:\n\n```\nLinux e15 6.8.0-49-generic #49~22.04.1-Ubuntu SMP PREEMPT_DYNAMIC Wed Nov  6 17:42:15 UTC 2 x86_64 x86_64 x86_64 GNU/Linux\n```\n\nThis output includes the kernel name (`Linux`), the hostname (`e15`), the kernel version (`6.8.0-49-generic`), the architecture (`x86_64`), and other system details related to your current Ubuntu setup.")

``` python
messages.append(form_msg("user", "tell current directory with bash command"))
complete(messages, tools=tools)
```

    ('assistant', 'The current directory is:\n\n```\n/home/doyu/00llmcam/nbs\n```')

``` python
messages.append(form_msg("user", "list files under ../data with bash command"))
complete(messages, tools=tools)
```

    ('assistant',
     'Here are the files under the `../data` directory:\n\n- `cap_2024.09.28_15:59:06_Presidentinlinna.jpg`\n- `cap_2024.09.28_16:00:11_Presidentinlinna.jpg`\n- `cap_2024.09.28_16:01:16_Etelasatama.jpg`\n- `cap_2024.09.28_16:02:21_Etelasatama.jpg`\n- `cap_2024.09.28_16:05:31_Olympiaterminaali.jpg`\n- `cap_2024.09.28_16:06:36_Olympiaterminaali.jpg`\n- `cap_2024.09.28_16:07:41_Torni.jpg`\n- `cap_2024.09.28_16:09:51_Tuomiokirkko.jpg`\n- `cap_2024.09.28_16:15:11_Presidentinlinna.jpg`\n- `cap_2024.09.28_17:33:31_Presidentinlinna.jpg`\n- ... (and many more)\n\nIf you need to see a specific part of the list or need further details, please let me know!')

``` python
messages.append(form_msg("user", "rename cap_2024.09.28_15:59:06_Presidentinlinna.jpg with xcap_2024.09.28_15:59:06_Presidentinlinna.jpg with bash command"))
complete(messages, tools=tools)
```

    ('assistant',
     'The file has been successfully renamed from `cap_2024.09.28_15:59:06_Presidentinlinna.jpg` to `xcap_2024.09.28_15:59:06_Presidentinlinna.jpg`.')

``` python
messages.append(form_msg("user", "check if there's xcap_2024.09.28_15:59:06_Presidentinlinna.jpg with bash command"))
complete(messages, tools=tools)
```

    ('assistant',
     'The file `xcap_2024.09.28_15:59:06_Presidentinlinna.jpg` does exist in the `../data` directory.')

``` python
messages.append(form_msg("user", "show some of the running processes with bash command"))
complete(messages, tools=tools)
```

    ('assistant',
     'Here are some of the running processes:\n\n```\nUSER         PID %CPU %MEM    VSZ   RSS TTY      STAT START   TIME COMMAND\nroot           1  0.0  0.0 167064 12084 ?        Ss   Nov30   0:03 /sbin/init splash\nroot           2  0.0  0.0      0     0 ?        S    Nov30   0:00 [kthreadd]\nroot           3  0.0  0.0      0     0 ?        S    Nov30   0:00 [pool_workqueue_release]\nroot           4  0.0  0.0      0     0 ?        I<   Nov30   0:00 [kworker/R-rcu_g]\nroot           5  0.0  0.0      0     0 ?        I<   Nov30   0:00 [kworker/R-rcu_p]\nroot           6  0.0  0.0      0     0 ?        I<   Nov30   0:00 [kworker/R-slub_]\nroot           7  0.0  0.0      0     0 ?        I<   Nov30   0:00 [kworker/R-netns]\nroot          10  0.0  0.0      0     0 ?        I<   Nov30   0:00 [kworker/0:0H-events_highpri]\nroot          12  0.0  0.0      0     0 ?        I<   Nov30   0:00 [kworker/R-mm_pe]\n```\n\nThis output includes the user, process ID (PID), CPU and memory usage, process status, and the command that initiated the process.')

``` python
messages.append(form_msg("user", "list only those process ids"))
complete(messages, tools=tools)
```

    ('assistant',
     'Here are some of the process IDs (PIDs) of running processes:\n\n```\n1\n2\n3\n4\n5\n6\n7\n10\n12\n13\n```')

``` python
messages.append(form_msg("user", "What kind of Openrating System is running?"))
complete(messages, tools=tools)
```

    ('assistant',
     'The operating system running is a version of Linux, specifically:\n\n```\nUbuntu, with Linux kernel version 6.8.0-49-generic\n```\n\nThis information indicates that the machine is running Ubuntu as its operating system.')

``` python
messages.append(form_msg("user", "Capture the desktop image"))
complete(messages, tools=tools)
```

    ('assistant',
     "It seems there was an error trying to capture the desktop image. The tool could not access the X Window system, possibly due to the environment in which it's running, which may not support direct graphical access or the X server is not available.\n\nIf you are running in a headless environment or without a graphical interface, this could lead to such errors. Let me know if there's anything else you need help with!")

``` python
messages.append(form_msg("user", "install scrot"))
complete(messages, tools=tools)
```

    ('assistant',
     'The `scrot` package is already installed and is the newest version available. You can use it to capture screenshots. If you need further assistance with capturing the screen using `scrot`, feel free to ask!')

``` python
messages.append(form_msg("user", "Capture the desktop image"))
complete(messages, tools=tools)
```

    ('assistant',
     'The desktop image has been successfully captured and saved as `desktop_capture.png` in the `../data` directory.')

``` python
messages.append(form_msg("user", "uninstall scrot"))
complete(messages, tools=tools)
```

    ('assistant',
     'The `scrot` package has been successfully uninstalled from your system. If you wish to clean up other packages that were automatically installed with `scrot` and are no longer needed, you can run `sudo apt autoremove`. If you need further assistance, feel free to ask!')