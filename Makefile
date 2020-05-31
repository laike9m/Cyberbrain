.PHONY: test

test:
	python3.7 -m pytest --assert=plain -s -vv
	python3.8 -m pytest --assert=plain -s -vv

	# The follow versions are compiled with `--without-computed-gotos` using command:
	# PYTHON_CONFIGURE_OPTS="--without-computed-gotos" pyenv install 3.8.3
	#
	# It is for verifying our program can work without computed gotos. Python installed
	# on Windows does not have computed goto, so this could help us detect potential
	# breakages on Windows.
	#
	# To be able to run tests, we need to install needed dependencies.
    #
    # Since pyenv doesn't recognize different Python patch versions, here I use an
    # environment variable to point to the the Python executable path.
	${python377} -m pytest --assert=plain -s -vv
	${python383} -m pytest --assert=plain -s -vv