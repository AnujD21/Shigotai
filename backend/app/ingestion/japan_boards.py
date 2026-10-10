"""Company job boards polled for live Japan-based roles.

Every board here was checked against its public API and had open roles in
Japan when added (Oct 2026). To add a company, find its careers page: a URL
on boards.greenhouse.io / job-boards.greenhouse.io, jobs.lever.co,
jobs.ashbyhq.com, or jobs.smartrecruiters.com contains the board slug. Then
check it has Japan roles with `python -m app.ingest --board <platform>:<slug>
--dry-run`.

Most Japan-headquartered companies use domestic ATSs (HERP, HRMOS, Talentio)
that don't publish a public jobs API, so these boards skew toward global
companies' Japan offices. A board that 404s or errors is skipped for that
run without touching its existing jobs.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class BoardConfig:
    platform: str  # greenhouse | lever | ashby | smartrecruiters
    slug: str
    company: str
    website: str | None = None
    industry: str | None = None


JAPAN_BOARDS: list[BoardConfig] = [
    # Engineering-heavy Japan teams
    BoardConfig("lever", "woven-by-toyota", "Woven by Toyota", "https://woven.toyota", "Mobility & Automotive"),
    BoardConfig("smartrecruiters", "BoschGroup", "Bosch", "https://www.bosch.co.jp", "Engineering & Manufacturing"),
    BoardConfig("ashby", "openai", "OpenAI", "https://openai.com", "AI Research"),
    BoardConfig("greenhouse", "anthropic", "Anthropic", "https://www.anthropic.com", "AI Research"),
    BoardConfig("greenhouse", "databricks", "Databricks", "https://www.databricks.com", "Data & AI"),
    BoardConfig("ashby", "cursor", "Cursor", "https://cursor.com", "Developer Tools"),
    BoardConfig("ashby", "clickhouse", "ClickHouse", "https://clickhouse.com", "Databases"),
    BoardConfig("lever", "palantir", "Palantir", "https://www.palantir.com", "Data & AI"),
    # Global companies with Tokyo offices
    BoardConfig("greenhouse", "datadog", "Datadog", "https://www.datadoghq.com", "Cloud Software"),
    BoardConfig("greenhouse", "zscaler", "Zscaler", "https://www.zscaler.com", "Cybersecurity"),
    BoardConfig("smartrecruiters", "ServiceNow", "ServiceNow", "https://www.servicenow.com", "Cloud Software"),
    BoardConfig("ashby", "notion", "Notion", "https://www.notion.so", "Productivity Software"),
    BoardConfig("greenhouse", "newrelic", "New Relic", "https://newrelic.com", "Cloud Software"),
    BoardConfig("greenhouse", "braze", "Braze", "https://www.braze.com", "Marketing Technology"),
    BoardConfig("greenhouse", "block", "Block", "https://block.xyz", "Fintech"),
    BoardConfig("greenhouse", "mongodb", "MongoDB", "https://www.mongodb.com", "Databases"),
    BoardConfig("greenhouse", "adyen", "Adyen", "https://www.adyen.com", "Fintech"),
    BoardConfig("greenhouse", "airbnb", "Airbnb", "https://www.airbnb.com", "Travel"),
    BoardConfig("greenhouse", "okta", "Okta", "https://www.okta.com", "Cybersecurity"),
    BoardConfig("greenhouse", "asana", "Asana", "https://asana.com", "Productivity Software"),
    BoardConfig("greenhouse", "workato", "Workato", "https://www.workato.com", "Cloud Software"),
    BoardConfig("greenhouse", "stripe", "Stripe", "https://stripe.com", "Fintech"),
    BoardConfig("greenhouse", "gitlab", "GitLab", "https://about.gitlab.com", "Developer Tools"),
    BoardConfig("greenhouse", "elastic", "Elastic", "https://www.elastic.co", "Cloud Software"),
    BoardConfig("greenhouse", "figma", "Figma", "https://www.figma.com", "Design Software"),
    BoardConfig("smartrecruiters", "Wise", "Wise", "https://wise.com", "Fintech"),
    BoardConfig("ashby", "replit", "Replit", "https://replit.com", "Developer Tools"),
    BoardConfig("ashby", "elevenlabs", "ElevenLabs", "https://elevenlabs.io", "AI Research"),
    BoardConfig("ashby", "cohere", "Cohere", "https://cohere.com", "AI Research"),
    BoardConfig("greenhouse", "duolingo", "Duolingo", "https://www.duolingo.com", "Education Technology"),
    BoardConfig("greenhouse", "fivetran", "Fivetran", "https://www.fivetran.com", "Data & AI"),
    BoardConfig("greenhouse", "twilio", "Twilio", "https://www.twilio.com", "Cloud Software"),
    BoardConfig("greenhouse", "cloudflare", "Cloudflare", "https://www.cloudflare.com", "Cloud Software"),
    BoardConfig("greenhouse", "roblox", "Roblox", "https://www.roblox.com", "Gaming"),
]
