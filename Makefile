BASEMATRIX_NAME       := kevinkatz/basematrix
BASEMATRIX_DOCKERFILE := basematrix.Dockerfile
RGBSTRIP_NAME := kevinkatz/rgbstrip
RGBSTRIP_DOCKERFILE := rgbstrip.Dockerfile
TAG        := $$(git log -1 --format=%h)

BASEMATRIX_IMG := "${BASEMATRIX_NAME}:${TAG}"
RGBSTRIP_IMG := "${RGBSTRIP_NAME}:${TAG}"

BASEMATRIX_LATEST     := "${BASEMATRIX_NAME}:latest"
RGBSTRIP_LATEST     := "${RGBSTRIP_NAME}:latest"

BASEMATRIX_HOST       := "matrix.local"
 
build:
	@docker --debug buildx build \
		--pull \
		-f "${BASEMATRIX_DOCKERFILE}" \
		-t "${BASEMATRIX_IMG}" -t "${BASEMATRIX_LATEST}" \
		--platform=linux/arm64 \
		--push .
 
build_rgbstrip:
	@docker --debug buildx build \
		--pull \
		-f "${RGBSTRIP_DOCKERFILE}" \
		-t "${RGBSTRIP_IMG}" -t "${RGBSTRIP_LATEST}" \
		--platform=linux/arm64 \
		--push .
 
restart:
	@ssh dietpi@${BASEMATRIX_HOST} "sudo systemctl restart docker.rgb"
tail:
	@ssh dietpi@${BASEMATRIX_HOST} "sudo journalctl -u docker.rgb -f"
