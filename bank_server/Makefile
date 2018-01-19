build: Dockerfile bank_server/*
	docker build -t bank.img .

start: build
	-docker container start bank.cont || docker run -p 1337:1337 -p 1338:1338 -t --name bank.cont bank.img

stop:
	-docker container stop bank.cont

clean:
	-docker container stop bank.cont
	-docker container rm bank.cont

logs:
	docker exec bank.cont cat /bank/bank_server/logs/bank_server.log | cat > bank_server.log

# command run unittests in bank_server/tests
test: clean build
	docker run -p 1337:1337 -p 1338:1338 --name bank.cont bank.img python -m unittest discover
