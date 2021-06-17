NAME       := kevinkatz/gravity
DOCKERFILE := gravity.Dockerfile
TAG        := $$(git log -1 --format=%h)
IMG        := "${NAME}:${TAG}"
LATEST     := "${NAME}:latest"
 
build:
	@docker --debug buildx build \
		--pull \
		-f "${DOCKERFILE}" \
		-t "${IMG}" -t "${LATEST}" \
		--platform linux/arm64 \
		--push .
 
restart:
	@ssh dietpi@${RGB_HOST} "sudo systemctl restart docker.rgb"
tail:
	@ssh dietpi@${RGB_HOST} "sudo journalctl -u docker.rgb -f"
