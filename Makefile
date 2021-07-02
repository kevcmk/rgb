NAME       := kevinkatz/basematrix
DOCKERFILE := basematrix.Dockerfile
TAG        := $$(git log -1 --format=%h)
IMG        := "${NAME}:${TAG}"
LATEST     := "${NAME}:latest"
HOST       := "matrix.local"
 
build:
	@docker --debug buildx build \
		--pull \
		-f "${DOCKERFILE}" \
		-t "${IMG}" -t "${LATEST}" \
		--platform=linux/arm64 \
		--push .
 
restart:
	@ssh dietpi@${HOST} "sudo systemctl restart docker.rgb"
tail:
	@ssh dietpi@${HOST} "sudo journalctl -u docker.rgb -f"
