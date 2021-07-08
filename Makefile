DOCKERHUB_USER := kevinkatz
BASEMATRIX_NAME := basematrix
RGBSTRIP_NAME := rgbstrip
GIT_HASH_TAG := $$(git log -1 --format=%h)
TRGT := "cyan.local"

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
		--platform=linux/arm64 \
		--push .
 
restart:
	@ssh dietpi@${TRGT} "sudo systemctl restart docker.rgb"

tail:
	@ssh dietpi@${TRGT} "sudo journalctl -u docker.rgb -f"
