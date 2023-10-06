prepare:
	python3 -m venv venv \
	&& . venv/bin/activate \
	&& pip install -r requirements.txt \
	pip install -e .

unittest:
	python3 test/test_config.py
	python3 test/test_database.py
	python3 test/test_url_loader.py
