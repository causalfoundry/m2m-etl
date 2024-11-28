TAG ?= $$(git rev-parse head)

DEBIAN_FLAVOR ?= bullseye

POSTGRES_VERSION ?= postgres:15
PROJECT_ID ?= m2mgcpetl
REDIS_VERSION ?= redis:7.0
REGION ?= africa-south1

check:
	echo "run test"

build-image:
	@docker build \
		-t ${REGION}-docker.pkg.dev/${PROJECT_ID}/etl/etl:${TAG} \
		-f ./Dockerfile .

