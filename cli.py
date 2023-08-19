import click
import confluence
import graph
import logging

logging.basicConfig(
    format="%(asctime)s, %(levelname)s, %(module)s, %(message)s", level=logging.INFO
)


@click.command(context_settings={"show_default": True})
@click.option(
    "--forge-email",
    envvar="FORGE_EMAIL",
    required=True,
    help="The email address associated with your Atlassian account",
)
@click.option(
    "--forge-api-token",
    envvar="FORGE_API_TOKEN",
    required=True,
    help="Your Atlassian API token",
)
@click.option(
    "--azure-client-id",
    envvar="AZURE_CLIENT_ID",
    required=True,
    help="'Application (client) ID' of app registration in Azure portal - this value is a GUID",
)
@click.option(
    "--azure-tenant-id",
    envvar="AZURE_TENANT_ID",
    required=True,
    help="Tenant ID of app registration in Azure portal - this value is a GUID",
)
@click.option(
    "--azure-client-secret",
    envvar="AZURE_CLIENT_SECRET",
    required=True,
    help="Client secret 'Value' (not its ID) from 'Client secrets' in app registration in Azure portal",
)
@click.option(
    "-d",
    "--domain",
    default="sol-jira",
    help="Confluence domain name, for example, your-domain.atlassian.net",
)
@click.option("-s", "--space", default="AT", help="The space you want to work on")
@click.option("-p", "--page-id", help="Page Id")
@click.option(
    "--all",
    is_flag=True,
    help="Perform the automation on all pages",
)
def main(**kwargs):
    confluence.init(kwargs)
    graph.init(kwargs)
    if kwargs.get("all"):
        confluence.export_all(kwargs)
    elif kwargs.get("page_id"):
        confluence.export_page(kwargs.get("page_id"))
    else:
        click.echo("Please provide a page id")


if __name__ == "__main__":
    main()
