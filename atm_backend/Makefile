build: Dockerfile atm_backend/*
	docker build  -t atm.img --rm=true .

start: build
	-docker container start atm.cont || docker run -p 1336:1336 --net=host --privileged -v /dev/:/dev/ -t --name atm.cont atm.img

stop:
	-docker container stop atm.cont

clean:
	-docker container stop atm.cont
	-docker container rm atm.cont

logs:
	docker exec atm.cont cat /atm/atm_backend/logs/atm_backend.log > atm_backend.log

# command run unittests in bank_server/tests
test: clean build
	(cd ../bank_server && make clean && make start &)
	(make clean && make start &)
	# run this after hsm and card are connected 
	# docker exec atm.cont python -m unittest discover
