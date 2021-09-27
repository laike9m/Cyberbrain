.PHONY: test

test:
	python3.7 -m pytest test --assert=plain -s -vv
	python3.7 -m pytest test/test_outside_func.py --assert=plain -s -vv
	python3.8 -m pytest test --assert=plain -s -vv
	python3.8 -m pytest test/test_outside_func.py --assert=plain -s -vv
	python3.9 -m pytest test --assert=plain -s -vv
	python3.9 -m pytest test/test_outside_func.py --assert=plain -s -vv

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
	${python377} -m pytest test --assert=plain -s -vv
	${python377} -m pytest test/test_outside_func.py --assert=plain -s -vv
	${python383} -m pytest test --assert=plain -s -vv
	${python383} -m pytest test/test_outside_func.py --assert=plain -s -vv

update_dep:
	pdm update
	cd cyberbrain-vsc/ && npm update

# We must use npm not yarn. See https://github.com/microsoft/vscode-vsce/issues/497
publish:
	npm install -g vsce
#	pdm build
#	pdm run twine upload -r pypi dist/*  # Assuming .pypirc exists.
	cd ./cyberbrain-vsc && vsce package --no-yarn && vsce publish --no-yarn
	cd ./cyberbrain-vsc && npx ovsx publish -p ${ovsx_token}
