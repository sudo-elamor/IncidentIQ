from celery import Celery

celery_app = Celery(
    "ai_agent",
    broker="redis://broker:6379/0",
    backend="redis://broker:6379/1",
    include=["agent_tasks"]
)

celery_app.conf.task_routes = {
    "app.tasks.analyze_logs.*": {"queue": "agent_queue"}
}
