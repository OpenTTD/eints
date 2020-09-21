FROM python:3.8-slim

ARG BUILD_DATE=""
ARG BUILD_VERSION="dev"

LABEL maintainer="OpenTTD Dev Team <info@openttd.org>"
LABEL org.opencontainers.image.created=${BUILD_DATE}
LABEL org.opencontainers.image.authors="OpenTTD Dev Team <info@openttd.org>"
LABEL org.opencontainers.image.url="https://github.com/OpenTTD/eints"
LABEL org.opencontainers.image.source="https://github.com/OpenTTD/eints"
LABEL org.opencontainers.image.version=${BUILD_VERSION}
LABEL org.opencontainers.image.licenses="GPLv2"
LABEL org.opencontainers.image.title="WebTranslator for OpenTTD and its add-ons"
LABEL org.opencontainers.image.description="Eints Is a Newgrf Translation Service. Though now it is also used for Game Scripts and OpenTTD itself."

WORKDIR /code

COPY requirements.txt \
        LICENSE.md \
        README.md \
        run \
        /code/
# Needed for Sentry to know what version we are running
RUN echo "${BUILD_VERSION}" > /code/.version

RUN pip --no-cache-dir install -r requirements.txt

# Validate that what was installed was what was expected
RUN pip freeze 2>/dev/null > requirements.installed \
        && diff -u --strip-trailing-cr requirements.txt requirements.installed 1>&2 \
        || ( echo "!! ERROR !! requirements.txt defined different packages or versions for installation" \
                && exit 1 ) 1>&2

COPY rights_example.dat /code/rights.dat
COPY static /code/static
COPY stable_languages /code/stable_languages
COPY unstable_languages /code/unstable_languages
COPY views /code/views
COPY webtranslate /code/webtranslate

VOLUME ["/data"]
ENTRYPOINT ["python", "/code/run", "--project-root", "/data", "--server-host", "0.0.0.0"]
CMD []
