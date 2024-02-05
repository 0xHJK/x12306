clean:
	pip uninstall x12306 -y
	rm -fr build dist .egg *.egg-info
	find . | grep __pycache__ | xargs rm -fr
	find . | grep .pyc | xargs rm -f

install:
	python3 setup.py install

publish:
	pip install 'twine>=1.5.0'
	python setup.py sdist bdist_wheel
	twine upload dist/*
	rm -fr build .egg requests.egg-info
