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
	# To be able to run tests, we need to install needed libs as well.
    #
    # Since pyenv doesn't recognize different Python patch versions, here I use an
    # environment variable to point to the path of Python 3.8.3
	${python383} -m pytest --assert=plain -s -vv