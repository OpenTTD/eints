import logging
import sentry_sdk

log = logging.getLogger(__name__)


def setup_sentry(sentry_dsn, environment):
    if not sentry_dsn:
        return

    # Release is expected to be in the file '.version'
    with open(".version") as f:
        release = f.readline().strip()

    sentry_sdk.init(sentry_dsn, release=release, environment=environment)
    log.info(
        "Sentry initialized with release='%s' and environment='%s'",
        release,
        environment,
    )
