.PHONY: test

test:
	python3.7 -m pytest --assert=plain -s -vv
	python3.8 -m pytest --assert=plain -s -vv

	# This is a special version compiled with `--without-computed-gotos`.
	# Using command:
	# PYTHON_CONFIGURE_OPTS="--without-computed-gotos" pyenv install 3.8.3
	#
	# It is for verifying our program can work without computed gotos. Python
	# installed on Windows does not have computed goto, so this also help us
	# detect potential breakage on Windows.
	#
	# To be able to run tests, we need to installed needed libs as well.
    #
    # This approach is not optimal, but pyenv does not support specifying patch
    # versions, so we have to hard-code the path.
	/Users/laike9m/.pyenv/versions/3.8.3/bin/python -m pytest --assert=plain -s -vv