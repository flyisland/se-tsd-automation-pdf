import click
import confluence

htmlBody = """<div><h2>Summary</h2><ac:structured-macro ac:name="details" ac:schema-version="1" data-layout="default" ac:local-id="582b2ebe-4e02-40b7-a80c-dd069eaa9a0c" ac:macro-id="aa084c2c-2689-4de1-a558-9f9b6196d204"><ac:rich-text-body><table data-layout="default" ac:local-id="c4394ae8-8aed-44f5-8a95-6db27ccce384"><colgroup><col style="width: 340.0px;" /><col style="width: 340.0px;" /></colgroup><tbody><tr><th><p><strong>Owner</strong></p></th><td><p><ac:link><ri:user ri:account-id="5e18b6c89af3650e9e4103f0" /></ac:link> </p></td></tr><tr><th><p><strong>Reviewer</strong></p></th><td><p><ac:link><ri:user ri:account-id="5df2965d47c6b30ec90cc526" /></ac:link> </p></td></tr><tr><th><p><strong>Customer</strong></p></th><td><p>BYD Auto</p></td></tr><tr><th><p><strong>SalesForce Account Link</strong></p></th><td><p><a href="https://solacecorp.lightning.force.com/lightning/r/Account/0010z00001YlCFEAA3/view" data-card-appearance="inline">https: //solacecorp.lightning.force.com/lightning/r/Account/0010z00001YlCFEAA3/view</a> </p></td></tr><tr><th><p><strong>SalesForce Opportunity Link</strong></p></th><td><p><a href="https://solacecorp.lightning.force.com/lightning/r/0064z000028wvXAAAY/view">https://solacecorp.lightning.force.com/lightning/r/0064z000028wvXAAAY/view</a></p></td></tr><tr><th><p><strong>Hub Account Folder</strong></p></th><td><p><a href="https://solacesystems.sharepoint.com/teams/SFDCAccounts/Shared%20Documents/BYD%20Auto%20Co.%2C%20Ltd">https://solacesystems.sharepoint.com/teams/SFDCAccounts/Shared Documents/BYD Auto Co.%2C Ltd</a></p></td></tr><tr><th><p><strong>Description</strong></p></th><td><p>Using Solace Event Mesh to route critical information from Car Product Lines all over the country to the HQ</p></td></tr><tr><th><p><strong>Solution Type</strong></p></th><td><p>Software</p></td></tr><tr><th><p><strong>Industry</strong></p></th><td><p>Manufacturing Hi Tech</p></td></tr><tr><th><p><strong>Horizontal</strong></p></th><td><p>Event Driven Integration</p></td></tr><tr><th><p><strong>Cloud Platform</strong></p></th><td><p>On Prem</p></td></tr><tr><th><p><strong>Status</strong></p></th><td><p>Complete</p></td></tr><tr><th><p><strong>AccountID</strong></p></th><td><p>0010z00001YlCFEAA3</p></td></tr><tr><th><p><strong>OpportunityID</strong></p></th><td><p>0064z000028wvXAAAY</p></td></tr></tbody></table></ac:rich-text-body></ac:structured-macro><p> </p><ac:structured-macro ac:name="toc" ac:schema-version="1" data-layout="default" ac:local-id="a058c6f5-0ad1-4316-a008-3d26b5ab55a5" ac:macro-id="e1bea72e-6e11-41e5-bfad-d625f2cbc388" /><h2>Overview</h2><p>The car product lines need to submit critical information about each car to the HQ IT Center before the car goes off the product line.</p><p>Currently, the product lines invoke the center services in a sync manner, therefore issues like network or service outages will stop the product lines.</p><p>The customer is looking for a more robust solution for routing  information from Car Product Lines all over the country to the HQ</p><h2>Business Proposition</h2><p><ac:placeholder>To be able to provide a solution to the prospect/customer it is critical understand the business conditions of the account and opportunity. </ac:placeholder></p><h2>Why Solace</h2><ul><li><p>Exclusive Event Mesh technology to route critical events between multiple production lines and headquarters nationwide</p></li><li><p>Extremely high fault tolerance and ensures continuous production of the production line without interruption</p></li><li><p>Support a variety of message standards and HTTP protocols</p></li><li><p>High throughput, low latency</p></li><li><p>Verified solutions by Apple, Bosch, Renault, etc.</p></li></ul><h2>Alternative Solutions</h2><a href="https://solacesystems.sharepoint.com/teams/SFDCAccounts/_layouts/15/Doc.aspx?sourcedoc=%7BF9B9C831-922D-43A8-8DFF-B2E927CE3AD5%7D&amp;file=BYD-TSD-0.1.pptx&amp;action=edit&amp;mobileredirect=true">BYD-TSD-0.1.pptx</a><a href="https://solacesystems.sharepoint.com/teams/SFDCAccounts/_layouts/15/Doc.aspx?sourcedoc=%7BF9B9C831-922D-43A8-8DFF-B2E927CE3AD5%7D&amp;file=BYD-TSD-0.1.pptx&amp;action=edit&amp;mobileredirect=true">BYD-TSD-0.1.pptx</a><h2>Current State</h2><ac:image ac:align="center" ac:layout="center" ac:original-height="540" ac:original-width="960"><ri:attachment ri:filename="Slide2.png" ri:version-at-save="1" /></ac:image><p><ac:placeholder>Current state architecture and solution. Use diagrams where appropriate.</ac:placeholder></p><h2>Challenges with Current State</h2><p>Currently, the product lines invoke the center services in a sync manner, therefore issues like network or service outages will stop the product lines.</p><h2>Technical Solution</h2><p> </p><ac:image ac:align="center" ac:layout="center" ac:original-height="540" ac:original-width="960"><ri:attachment ri:filename="Slide5.png" ri:version-at-save="1" /></ac:image><ac:image ac:align="center" ac:layout="center" ac:original-height="540" ac:original-width="960"><ri:attachment ri:filename="Slide6.png" ri:version-at-save="1" /></ac:image><ac:image ac:align="center" ac:layout="center" ac:original-height="540" ac:original-width="960"><ri:attachment ri:filename="Slide7.png" ri:version-at-save="1" /></ac:image><p /><p><ac:placeholder>Detail on the Solace Target state architecture</ac:placeholder></p><h2>POC Success Criteria</h2><ol start="1"><li><p>No loss of events</p></li><li><p>Auto-retransmit events after the outages were recovered</p></li><li><p>Able to integrate with existing applications</p></li></ol><p>We have completed the PoC last month, and the customer&rsquo;s development dept has started developing their solution based on our product. Currently, the project has entered the business phase.</p><h2>Issue Tracking</h2><p><ac:placeholder>Details of any issues that are encountered. Inert table for tracking if this is desired format. Should also create links to any RT tickets that have been created during the pre-sales process.</ac:placeholder></p><h2>Resources</h2><p><ac:placeholder>This section would detail any internal or external resources that proved useful in constructing the TSD. Examples would be, other TSD\'s, internal LMS\' or codelabs. This section could also reference external whitepapers, blogs, or training courses. The intent is to be able to equip SC\'s on future similar opportunities.</ac:placeholder></p><h2>Links &amp; Addendum</h2><p><ac:placeholder>Links, any other information</ac:placeholder></p><p /><p /><p /><p /><p /></div>"""


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
    if kwargs.get("all"):
        confluence.export_all(kwargs)
    elif kwargs.get("page_id"):
        confluence.export_page(kwargs.get("page_id"), kwargs)
    else:
        click.echo("Please provide a page id")


if __name__ == "__main__":
    main()
