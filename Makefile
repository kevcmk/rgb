DOCKERHUB_USER := kevinkatz
BASEMATRIX_NAME := basematrix
APP_NAME := rgbstrip
GIT_HASH_TAG := $$(git log -1 --format=%h)
TRGT := "cyan.local"
PLATFORMS := "linux/arm64,linux/arm/v7"

runtk:
	PYTHONPATH="$$(pwd)/src" python src/rgb/maintk.py 

build2d:
	@docker --debug buildx build \
		--pull \
		-f "${BASEMATRIX_NAME}.Dockerfile" \
		-t "${DOCKERHUB_USER}/${BASEMATRIX_NAME}:${GIT_HASH_TAG}" -t "${DOCKERHUB_USER}/${BASEMATRIX_NAME}:latest" \
		--platform=linux/arm64 \
		--push .
 
build:
	@docker --debug buildx build \
		--pull \
		-f "${APP_NAME}.Dockerfile" \
		-t "${DOCKERHUB_USER}/${APP_NAME}:${GIT_HASH_TAG}" -t "${DOCKERHUB_USER}/${APP_NAME}:latest" \
		--platform=${PLATFORMS} \
		--push .

restart:
	@ssh dietpi@${TRGT} "sudo systemctl restart docker.rgb"
restart1d:
	@ssh dietpi@${TRGT} "sudo systemctl restart docker.rgbstrip"

tail:
	@ssh dietpi@${TRGT} "sudo journalctl -u docker.rgb -f"
tail1d:
	@ssh dietpi@${TRGT} "sudo journalctl -u docker.rgbstrip -f"
