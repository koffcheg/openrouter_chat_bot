from bot.services.health.status_service import StatusService


def test_status_service_records_attempts_and_fallback():
    service = StatusService()
    service.begin_request(chat_id=1, command='ask', selected_model='meta', fallback_chain=['meta', 'router'])
    service.record_attempt(chat_id=1, model_slug='meta')
    service.record_provider_error(chat_id=1, error_text='429')
    service.record_attempt(chat_id=1, model_slug='router')
    service.record_success(chat_id=1, model_slug='router', duration_ms=120)
    snapshot = service.snapshot(chat_id=1)
    assert snapshot.selected_model == 'meta'
    assert snapshot.attempted_models == ['meta', 'router']
    assert snapshot.last_served_model == 'router'
    assert snapshot.fallback_used is True
    assert snapshot.provider_failures == 1
    assert snapshot.total_requests == 1
