# wc (word count)

https://www.youtube.com/playlist?list=PLhOuww6rJJNOGPw5Mu5FyhnumZjb9F6kk

Write a Python implementation of `wc` (word count).
The program should print lines, words, and characters for each input.
Files are acceptable arguments:

```
$ ./wc.py ../inputs/fox.txt
       1       9      45 ../inputs/fox.txt
```

As is "standard in" (`STDIN`) if given no arguments:

```
$ cat ../inputs/fox.txt | ./wc.py
       1       9      45 <stdin>
```

If given more than one file, also include a summary for each column:

```
$ ./wc.py ../inputs/*.txt
    1000    1000    5840 ../inputs/1000.txt
     100     100     657 ../inputs/1945-boys.txt
     100     100     684 ../inputs/1945-girls.txt
     865    7620   44841 ../inputs/const.txt
    2476    7436   41743 ../inputs/dickinson.txt
       1       9      45 ../inputs/fox.txt
      25     278    1476 ../inputs/gettysburg.txt
      37      91     499 ../inputs/issa.txt
       9      51     248 ../inputs/nobody.txt
       1      16      66 ../inputs/now.txt
       2       9      41 ../inputs/out.txt
       6      71     413 ../inputs/preamble.txt
    7035   68061  396320 ../inputs/scarlet.txt
      17     118     661 ../inputs/sonnet-29.txt
    2618   17668   95690 ../inputs/sonnets.txt
       3       7      45 ../inputs/spiders.txt
       9      34     192 ../inputs/the-bustle.txt
   37842   48990  369949 ../inputs/uscities.txt
     176    1340    8685 ../inputs/usdeclar.txt
   52322  152999  968095 total
```

The program should respond to `-h` and `--help` with a usage:

```
$ ./wc.py -h
usage: wc.py [-h] [FILE [FILE ...]]

Emulate wc (word count)

positional arguments:
  FILE        Input file(s) (default: [<_io.TextIOWrapper name='<stdin>'
              mode='r' encoding='UTF-8'>])

optional arguments:
  -h, --help  show this help message and exit
```

Run the test suite to ensure your program is working correctly.

```
$ make test
pytest -xv test.py
============================= test session starts ==============================
...
collected 9 items

test.py::test_exists PASSED                                              [ 11%]
test.py::test_usage PASSED                                               [ 22%]
test.py::test_bad_file PASSED                                            [ 33%]
test.py::test_empty PASSED                                               [ 44%]
test.py::test_one PASSED                                                 [ 55%]
test.py::test_two PASSED                                                 [ 66%]
test.py::test_fox PASSED                                                 [ 77%]
test.py::test_more PASSED                                                [ 88%]
test.py::test_stdin PASSED                                               [100%]

============================== 9 passed in 0.54s ===============================
```
