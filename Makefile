PROMPT_COLOR=\033[36m
PROMPT_NC=\033[0m # No Color

MS_IMAGE_REGISTRY = public.ecr.aws/e3b4k2v5/otterside
MS_CART_SERVICE_NAME = cart
MS_USERS_SERVICE_NAME = users
MS_FRONTEND_SERVICE_NAME = frontend
MS_PRODUCTS_SERVICE_NAME = products
MS_CHECKOUT_SERVICE_NAME = checkout
MS_NEWSLETTER_SERVICE_NAME = newsletter

HELM_CHART_PATH = ./helm
KUBECONFIG_PATH = $(HOME)/.kube/config
OTTERSIDE_NAMESPACE = otterside

# Include .env file if it exists
ifneq (,$(wildcard ./.env))
    include .env
    export
endif

help: ## Show help message
	@awk 'BEGIN {FS = ":.*##"; printf "\nUsage:\n"} /^[$$()% a-zA-Z_-]+:.*?##/ { printf "  ${PROMPT_COLOR}%-25s${PROMPT_NC} %s\n", $$1, $$2 } /^##@/ { printf "\n\033[1m%s\033[0m\n", substr($$0, 5) } ' $(MAKEFILE_LIST)

# Image building targets

build-users: ## Builds and pushes the users service image
	@echo "${PROMPT_COLOR}Building users image'...${PROMPT_NC}"
	docker buildx build --platform linux/amd64 -t $(MS_IMAGE_REGISTRY):$(MS_USERS_SERVICE_NAME)-amd64 --push --file build/$(MS_USERS_SERVICE_NAME).Dockerfile .
	docker buildx build --platform linux/arm64 -t $(MS_IMAGE_REGISTRY):$(MS_USERS_SERVICE_NAME)-arm64 --push --file build/$(MS_USERS_SERVICE_NAME).Dockerfile .

build-cart: ## Builds and pushes the cart service image
	@echo "${PROMPT_COLOR}Building cart image'...${PROMPT_NC}"
	docker buildx build --platform linux/amd64 -t $(MS_IMAGE_REGISTRY):$(MS_CART_SERVICE_NAME)-amd64 --push --file build/$(MS_CART_SERVICE_NAME).Dockerfile .
	docker buildx build --platform linux/arm64 -t $(MS_IMAGE_REGISTRY):$(MS_CART_SERVICE_NAME)-arm64 --push --file build/$(MS_CART_SERVICE_NAME).Dockerfile .

build-checkout: ## Builds and pushes the checkout service image
	@echo "${PROMPT_COLOR}Building checkout image'...${PROMPT_NC}"
	docker buildx build --platform linux/amd64 -t $(MS_IMAGE_REGISTRY):$(MS_CHECKOUT_SERVICE_NAME)-amd64 --push --file build/$(MS_CHECKOUT_SERVICE_NAME).Dockerfile .
	docker buildx build --platform linux/arm64 -t $(MS_IMAGE_REGISTRY):$(MS_CHECKOUT_SERVICE_NAME)-arm64 --push --file build/$(MS_CHECKOUT_SERVICE_NAME).Dockerfile .

build-frontend: ## Builds and pushes the frontend service image
	@echo "${PROMPT_COLOR}Building frontend image'...${PROMPT_NC}"
	docker buildx build --platform linux/amd64 -t $(MS_IMAGE_REGISTRY):$(MS_FRONTEND_SERVICE_NAME)-amd64 --push --file build/$(MS_FRONTEND_SERVICE_NAME).Dockerfile .
	docker buildx build --platform linux/arm64 -t $(MS_IMAGE_REGISTRY):$(MS_FRONTEND_SERVICE_NAME)-arm64 --push --file build/$(MS_FRONTEND_SERVICE_NAME).Dockerfile .

build-newsletter: ## Builds and pushes the newsletter service image
	@echo "${PROMPT_COLOR}Building newsletter image'...${PROMPT_NC}"
	docker buildx build --platform linux/amd64 -t $(MS_IMAGE_REGISTRY):$(MS_NEWSLETTER_SERVICE_NAME)-amd64 --push --file build/$(MS_NEWSLETTER_SERVICE_NAME).Dockerfile .
	docker buildx build --platform linux/arm64 -t $(MS_IMAGE_REGISTRY):$(MS_NEWSLETTER_SERVICE_NAME)-arm64 --push --file build/$(MS_NEWSLETTER_SERVICE_NAME).Dockerfile .

build-products: ## Builds and pushes the products service image
	@echo "${PROMPT_COLOR}Building products image'...${PROMPT_NC}"
	docker buildx build --platform linux/amd64 -t $(MS_IMAGE_REGISTRY):$(MS_PRODUCTS_SERVICE_NAME)-amd64 --push --file build/$(MS_PRODUCTS_SERVICE_NAME).Dockerfile .
	docker buildx build --platform linux/arm64 -t $(MS_IMAGE_REGISTRY):$(MS_PRODUCTS_SERVICE_NAME)-arm64 --push --file build/$(MS_PRODUCTS_SERVICE_NAME).Dockerfile .

build-images: build-users build-cart build-checkout build-frontend build-newsletter build-products ## Build and push all images

# Combine arch images

tag-users: ## Tag the users service images
	docker buildx imagetools create -t $(MS_IMAGE_REGISTRY):$(MS_USERS_SERVICE_NAME) \
	$(MS_IMAGE_REGISTRY):$(MS_USERS_SERVICE_NAME)-amd64 \
	$(MS_IMAGE_REGISTRY):$(MS_USERS_SERVICE_NAME)-arm64

tag-cart: ## Tag the cart service images
	docker buildx imagetools create -t $(MS_IMAGE_REGISTRY):$(MS_CART_SERVICE_NAME) \
	$(MS_IMAGE_REGISTRY):$(MS_CART_SERVICE_NAME)-amd64 \
	$(MS_IMAGE_REGISTRY):$(MS_CART_SERVICE_NAME)-arm64

tag-checkout: ## Tag the checkout service images
	docker buildx imagetools create -t $(MS_IMAGE_REGISTRY):$(MS_CHECKOUT_SERVICE_NAME) \
	$(MS_IMAGE_REGISTRY):$(MS_CHECKOUT_SERVICE_NAME)-amd64 \
	$(MS_IMAGE_REGISTRY):$(MS_CHECKOUT_SERVICE_NAME)-arm64

tag-frontend: ## Tag the frontend service images
	docker buildx imagetools create -t $(MS_IMAGE_REGISTRY):$(MS_FRONTEND_SERVICE_NAME) \
	$(MS_IMAGE_REGISTRY):$(MS_FRONTEND_SERVICE_NAME)-amd64 \
	$(MS_IMAGE_REGISTRY):$(MS_FRONTEND_SERVICE_NAME)-arm64

tag-newsletter: ## Tag the newsletter service images
	docker buildx imagetools create -t $(MS_IMAGE_REGISTRY):$(MS_NEWSLETTER_SERVICE_NAME) \
	$(MS_IMAGE_REGISTRY):$(MS_NEWSLETTER_SERVICE_NAME)-amd64 \
	$(MS_IMAGE_REGISTRY):$(MS_NEWSLETTER_SERVICE_NAME)-arm64

tag-products: ## Tag the products service images
	docker buildx imagetools create -t $(MS_IMAGE_REGISTRY):$(MS_PRODUCTS_SERVICE_NAME) \
	$(MS_IMAGE_REGISTRY):$(MS_PRODUCTS_SERVICE_NAME)-amd64 \
	$(MS_IMAGE_REGISTRY):$(MS_PRODUCTS_SERVICE_NAME)-arm64

tag-images: tag-users tag-cart tag-checkout tag-frontend tag-newsletter tag-products ## Tag all images

update-images: build-images tag-images ## Build and tag all images

install-otterside: ## Installs Otterside in the kubernetes cluster
	helm --kubeconfig=$(KUBECONFIG_PATH) dep up $(HELM_CHART_PATH); \
	helm --kubeconfig=$(KUBECONFIG_PATH) upgrade --install otterside $(HELM_CHART_PATH) -n $(OTTERSIDE_NAMESPACE) --create-namespace