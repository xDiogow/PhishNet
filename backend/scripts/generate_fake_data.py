"""Generate realistic fake targets, campaigns, and results for a tenant.

Usage:
    python scripts/generate_fake_data.py --tenant-id 1 --user-id 1
    python scripts/generate_fake_data.py --tenant-id 1 --user-id 1 --targets 20 --campaigns 5
"""
import argparse
import random
import sys
import os
import uuid
from faker import Faker
from datetime import datetime, timedelta, timezone

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app
from app.extensions import db
from app.models.tenant import Tenant
from app.models.user import User
from app.models.target import Target
from app.models.template import Template
from app.models.campaign import Campaign, CampaignStatus
from app.models.campaign_stats import CampaignStats
from app.models.campaign_result import CampaignResult
from app.models.audit_log import AuditLog

fake = Faker()


def generate_data(tenant_id: int, user_id: int, num_targets: int, num_campaigns: int):
    app = create_app()
    with app.app_context():
        # Validate tenant and user
        tenant = db.session.get(Tenant, tenant_id)
        if not tenant:
            print(f"Error: Tenant with ID {tenant_id} not found.")
            return

        user = db.session.get(User, user_id)
        if not user:
            print(f"Error: User with ID {user_id} not found.")
            return

        if user.tenant_id != tenant_id:
            print(f"Error: User {user_id} does not belong to tenant {tenant_id}.")
            return

        # Fetch available templates (not tenant-scoped; templates are global)
        templates = db.session.query(Template).all()
        if not templates:
            print("Error: No templates found. Create at least one template first.")
            return

        print(f"Starting generation for Tenant: {tenant.name} (ID: {tenant_id})")

        # Generate fake targets
        print(f"Generating {num_targets} fake targets...")
        new_targets = []
        for _ in range(num_targets):
            target = Target(
                email=fake.unique.email(),
                first_name=fake.first_name(),
                last_name=fake.last_name(),
                position=fake.job(),
                tenant_id=tenant_id
            )
            new_targets.append(target)
            db.session.add(target)

        db.session.flush()

        for target in new_targets:
            db.session.add(AuditLog(
                user_id=user_id,
                tenant_id=tenant_id,
                action="CREATE_TARGET",
                resource_type="Target",
                resource_id=str(target.id),
                details={
                    "email": target.email,
                    "first_name": target.first_name,
                    "last_name": target.last_name,
                    "note": "Generated via fake data script"
                },
                ip_address="127.0.0.1"
            ))

        # Generate fake campaigns
        print(f"Generating {num_campaigns} fake campaigns...")
        for i in range(num_campaigns):
            template = random.choice(templates)
            campaign_status = random.choice([
                CampaignStatus.RUNNING,
                CampaignStatus.STOPPED,
                CampaignStatus.ARCHIVED,
            ])

            launched_at = datetime.now(timezone.utc) - timedelta(days=random.randint(1, 30))
            stopped_at = launched_at + timedelta(days=7) if campaign_status != CampaignStatus.RUNNING else None

            campaign = Campaign(
                name=f"Fake Campaign {fake.word().capitalize()} {i + 1}",
                tenant_id=tenant_id,
                created_by_user_id=user_id,
                template_id=template.id,
                status=campaign_status,
                launched_at=launched_at,
                stopped_at=stopped_at,
            )
            db.session.add(campaign)
            db.session.flush()

            # Realistic funnel percentages
            sent = num_targets
            opened = random.randint(max(1, int(sent * 0.25)), max(1, int(sent * 0.75)))
            clicked = random.randint(max(1, int(opened * 0.25)), max(1, int(opened * 0.75)))
            submitted = random.randint(max(0, int(clicked * 0.25)), max(1, int(clicked * 0.75)))
            reported = random.randint(0, max(1, int(sent * 0.10)))

            db.session.add(CampaignStats(
                campaign_id=campaign.id,
                total_targets=num_targets,
                sent_count=sent,
                opened_count=opened,
                clicked_count=clicked,
                submitted_count=submitted,
                reported_count=reported,
            ))

            # Generate per-target results with realistic timestamps
            print(f"  Populating results for campaign {campaign.id}...")
            shuffled = list(new_targets)
            random.shuffle(shuffled)

            for idx, target in enumerate(shuffled):
                if idx < submitted:
                    result_status = "Submitted Data"
                elif idx < clicked:
                    result_status = "Clicked"
                elif idx < opened:
                    result_status = "Opened"
                else:
                    result_status = "Sent"

                offset_h = random.randint(1, 48)
                result_time = launched_at + timedelta(hours=offset_h)

                result = CampaignResult(
                    campaign_id=campaign.id,
                    email=target.email,
                    first_name=target.first_name,
                    last_name=target.last_name,
                    position=target.position,
                    tracking_token=str(uuid.uuid4()),
                    status=result_status,
                    sent_at=launched_at,
                    opened_at=result_time if result_status in ("Opened", "Clicked", "Submitted Data") else None,
                    clicked_at=result_time + timedelta(minutes=random.randint(1, 30)) if result_status in ("Clicked", "Submitted Data") else None,
                    submitted_at=result_time + timedelta(minutes=random.randint(2, 60)) if result_status == "Submitted Data" else None,
                )
                db.session.add(result)

            db.session.add(AuditLog(
                user_id=user_id,
                tenant_id=tenant_id,
                action="CREATE_CAMPAIGN",
                resource_type="Campaign",
                resource_id=str(campaign.id),
                details={
                    "name": campaign.name,
                    "template_id": template.id,
                    "note": "Generated via fake data script"
                },
                ip_address="127.0.0.1"
            ))

        db.session.commit()
        print(f"Done. Generated {num_targets} targets and {num_campaigns} campaigns for tenant {tenant_id}.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate fake target and campaign data for a tenant.")
    parser.add_argument("--tenant-id", type=int, required=True, help="ID of the tenant")
    parser.add_argument("--user-id", type=int, required=True, help="ID of the user creating the data")
    parser.add_argument("--targets", type=int, default=10, help="Number of targets to generate (default: 10)")
    parser.add_argument("--campaigns", type=int, default=2, help="Number of campaigns to generate (default: 2)")

    args = parser.parse_args()
    generate_data(args.tenant_id, args.user_id, args.targets, args.campaigns)
