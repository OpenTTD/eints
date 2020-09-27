import click
import logging
import sentry_sdk

from .click import click_additional_options

log = logging.getLogger(__name__)


@click_additional_options
@click.option("--sentry-dsn", help="Sentry DSN.")
@click.option(
    "--sentry-environment",
    help="Environment we are running in.",
    default="development",
)
def click_sentry(sentry_dsn, sentry_environment):
    if not sentry_dsn:
        return

    # Release is expected to be in the file '.version'
    with open(".version") as f:
        release = f.readline().strip()

    sentry_sdk.init(sentry_dsn, release=release, environment=sentry_environment)
    log.info(
        "Sentry initialized with release='%s' and environment='%s'",
        release,
        sentry_environment,
    )
