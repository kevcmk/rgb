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
 
