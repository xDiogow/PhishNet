"""Campaign API routes.

All campaign operations go through CampaignService, which handles email
delivery and result tracking natively (no external GoPhish dependency).

Routes:
  GET    /api/campaigns              list campaigns for the caller's tenant
  GET    /api/campaigns/<id>         get a single campaign
  GET    /api/campaigns/<id>/summary live stats + per-target result list
  POST   /api/campaigns              create and immediately launch a campaign
  DELETE /api/campaigns/<id>         delete a campaign (cascades to results)
  POST   /api/campaigns/<id>/complete mark a campaign as stopped
"""
from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models.campaign import Campaign
from app.repository.campaign_repository import CampaignRepository
from app.repository.user_repository import UserRepository
from app.services.campaign_service import CampaignService
from app.utils.auth_helper import get_current_user

bp = Blueprint('campaigns', __name__, url_prefix='/api/campaigns')


def campaign_to_dict(campaign: Campaign) -> dict:
    """Serialise a Campaign model to the API response shape."""
    return {
        'id': campaign.id,
        'name': campaign.name,
        'status': campaign.status.value,
        'tenant_id': campaign.tenant_id,
        'created_by_user_id': campaign.created_by_user_id,
        'template_id': campaign.template_id,
        'created_at': campaign.created_at.isoformat() if campaign.created_at else None,
        'launched_at': campaign.launched_at.isoformat() if campaign.launched_at else None,
        'stopped_at': campaign.stopped_at.isoformat() if campaign.stopped_at else None,
    }


@bp.route('', methods=['GET'])
@jwt_required()
def get_all_campaigns():
    """Return all campaigns belonging to the caller's tenant."""
    try:
        user = get_current_user()
        if not user:
            return jsonify({'error': 'User not found'}), 404
        repo = CampaignRepository()
        campaigns = repo.get_all(tenant_id=user.tenant_id)
        return jsonify({'campaigns': [campaign_to_dict(c) for c in campaigns]}), 200
    except Exception as e:
        current_app.logger.exception('Error getting campaigns')
        return jsonify({'error': 'Failed to get campaigns', 'message': str(e)}), 500


@bp.route('/<int:campaign_id>', methods=['GET'])
@jwt_required()
def get_campaign(campaign_id):
    """Return a single campaign. Returns 404 if it belongs to a different tenant."""
    try:
        user = get_current_user()
        if not user:
            return jsonify({'error': 'User not found'}), 404
        repo = CampaignRepository()
        campaign = repo.get_by_id(campaign_id, tenant_id=user.tenant_id)
        if not campaign:
            return jsonify({'error': 'Campaign not found'}), 404
        return jsonify(campaign_to_dict(campaign)), 200
    except Exception as e:
        current_app.logger.exception('Error getting campaign')
        return jsonify({'error': 'Failed to get campaign', 'message': str(e)}), 500


@bp.route('/<int:campaign_id>/summary', methods=['GET'])
@jwt_required()
def get_campaign_summary(campaign_id):
    """Return live campaign statistics and per-target result list.

    Stats are computed on-the-fly from CampaignResult rows so they are always
    current without any background sync. Also updates the CampaignStats cache.
    """
    try:
        user = get_current_user()
        if not user:
            return jsonify({'error': 'User not found'}), 404
        # Verify tenant ownership
        repo = CampaignRepository()
        campaign = repo.get_by_id(campaign_id, tenant_id=user.tenant_id)
        if not campaign:
            return jsonify({'error': 'Campaign not found'}), 404
        service = CampaignService()
        data = service.get_campaign_summary(campaign_id)
        return jsonify(data), 200
    except Exception as e:
        current_app.logger.exception('Error getting campaign summary')
        return jsonify({'error': 'Failed to get campaign summary', 'message': str(e)}), 500


@bp.route('', methods=['POST'])
@jwt_required()
def create_campaign():
    """Create and immediately launch a phishing campaign.

    Requires ``name`` and ``template_id`` in the request body. The campaign is
    sent to every target currently registered for the caller's tenant. Raises
    400 if the tenant has no targets configured.
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400

        user_id = get_jwt_identity()
        user_repo = UserRepository()
        user = user_repo.get_by_id(user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 404

        missing = [f for f in ['name', 'template_id'] if not data.get(f)]
        if missing:
            return jsonify({'error': 'Missing required fields', 'missing': missing}), 400

        try:
            template_id = int(data['template_id'])
        except (ValueError, TypeError):
            return jsonify({'error': 'template_id must be a valid integer'}), 400

        service = CampaignService()
        campaign = service.create_campaign(
            name=data['name'],
            template_id=template_id,
            tenant_id=user.tenant_id,
            user_id=user.id,
        )

        from app.services.audit_log_service import audit_service
        audit_service.log_action(
            user_id=user.id,
            tenant_id=user.tenant_id,
            action='CREATE_CAMPAIGN',
            resource_type='Campaign',
            resource_id=str(campaign.id),
            details={'name': campaign.name, 'template_id': template_id},
        )

        return jsonify({
            'status': 'success',
            'message': 'Campaign created successfully',
            'campaign': campaign_to_dict(campaign),
        }), 201

    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        current_app.logger.exception('Error creating campaign')
        return jsonify({'error': 'Failed to create campaign', 'message': str(e)}), 500


@bp.route('/<int:campaign_id>', methods=['DELETE'])
@jwt_required()
def delete_campaign(campaign_id):
    """Permanently delete a campaign and all its results/stats (cascades in DB)."""
    try:
        user = get_current_user()
        if not user:
            return jsonify({'error': 'User not found'}), 404
        # Verify tenant ownership before deleting
        repo = CampaignRepository()
        campaign = repo.get_by_id(campaign_id, tenant_id=user.tenant_id)
        if not campaign:
            return jsonify({'error': 'Campaign not found'}), 404
        service = CampaignService()
        service.delete_campaign(campaign_id)
        return jsonify({'status': 'success', 'message': 'Campaign deleted successfully'}), 200
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        current_app.logger.exception('Error deleting campaign')
        return jsonify({'error': 'Failed to delete campaign', 'message': str(e)}), 500


@bp.route('/<int:campaign_id>/complete', methods=['POST'])
@jwt_required()
def complete_campaign(campaign_id):
    """Mark a campaign as stopped. Does not delete any data."""
    try:
        user = get_current_user()
        if not user:
            return jsonify({'error': 'User not found'}), 404
        repo = CampaignRepository()
        campaign = repo.get_by_id(campaign_id, tenant_id=user.tenant_id)
        if not campaign:
            return jsonify({'error': 'Campaign not found'}), 404
        service = CampaignService()
        campaign = service.complete_campaign(campaign_id)
        return jsonify({
            'status': 'success',
            'message': 'Campaign stopped successfully',
            'campaign': campaign_to_dict(campaign),
        }), 200
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        current_app.logger.exception('Error completing campaign')
        return jsonify({'error': 'Failed to complete campaign', 'message': str(e)}), 500
