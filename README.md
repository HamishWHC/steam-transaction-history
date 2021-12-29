# Steam Transaction History Reader

This is a quick script + module to read transactions from your Steam transaction history that I made to find out how much I had spent on Steam games. Someone please make this into a browser extension (in hindsight, that would've been easier if I wrote this in JS...).

```
$ python3 main.py -h                                 
usage: main.py [-h] [--dump-json FILE] filename

Reads a Steam transaction history page and sums up how much you've spent over your account's lifetime. You will need to download/save the page as an HTML file so this script can read it. Load all the transactions on the page by using the "Load More Transactions" button. Then, press Ctrl/Cmd + S to save the page.

positional arguments:
  filename          filename of account history page's HTML

optional arguments:
  -h, --help        show this help message and exit
  --dump-json FILE  dump transaction events to given json file
```