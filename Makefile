.PHONY: test

test:
	python3.7 -m pytest --assert=plain -s -vv
	python3.8 -m pytest --assert=plain -s -vv
