DOCKERHUB_USER := kevinkatz
BASEMATRIX_NAME := basematrix
RGBSTRIP_NAME := rgbstrip
GIT_HASH_TAG := $$(git log -1 --format=%h)
TRGT := "cyan.local"

runtk:
	PYTHONPATH="$$(pwd)/src" python src/rgb/maintk.py 

build2d:
	@docker --debug buildx build \
		--pull \
		-f "${BASEMATRIX_NAME}.Dockerfile" \
		-t "${DOCKERHUB_USER}/${BASEMATRIX_NAME}:${GIT_HASH_TAG}" -t "${DOCKERHUB_USER}/${BASEMATRIX_NAME}:latest" \
		--platform=linux/arm64 \
		--push .
 
build1d:
	@docker --debug buildx build \
		--pull \
		-f "${RGBSTRIP_NAME}.Dockerfile" \
		-t "${DOCKERHUB_USER}/${RGBSTRIP_NAME}:${GIT_HASH_TAG}" -t "${DOCKERHUB_USER}/${RGBSTRIP_NAME}:latest" \
		--platform=linux/arm64,linux/arm/v7 \
		--push .
 
restart:
	@ssh dietpi@${TRGT} "sudo systemctl restart docker.rgb"
restart1d:
	@ssh dietpi@${TRGT} "sudo systemctl restart docker.rgbstrip"

tail:
	@ssh dietpi@${TRGT} "sudo journalctl -u docker.rgb -f"
tail1d:
	@ssh dietpi@${TRGT} "sudo journalctl -u docker.rgbstrip -f"
