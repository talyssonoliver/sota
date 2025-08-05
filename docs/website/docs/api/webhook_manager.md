# api/webhook_manager.py

## Classes
- **WebhookEventType** (line 25)
- **WebhookStatus** (line 39)
- **WebhookEndpoint** (line 49)
  - Methods: __post_init__
- **WebhookDelivery** (line 70)
- **WebhookEventData** (line 86)
  - Methods: review_created, review_approved, review_rejected, escalation_triggered
- **WebhookManager** (line 159)
  - Methods: __init__, _load_config, _save_config, _setup_routes, _verify_signature, _process_incoming_webhook, _handle_external_approval, _handle_external_rejection, _handle_external_escalation, register_endpoint, remove_endpoint, send_webhook, _create_delivery, get_delivery_status, get_endpoint_stats

## Functions
- **get_webhook_manager()** (line 575)
- **send_review_created_webhook(task_id, checkpoint_id, review_data)** (line 584)
- **send_review_approved_webhook(task_id, checkpoint_id, approval_data)** (line 590)
- **send_review_rejected_webhook(task_id, checkpoint_id, rejection_data)** (line 596)
- **send_escalation_webhook(task_id, escalation_data)** (line 602)
