import logging

from celery import shared_task

logger = logging.getLogger(__name__)


@shared_task
def generate_project_report(project_id):
    from .models import Project
    from apps.analytics.services import AnalyticsService

    try:
        project = Project.objects.select_related("owner").prefetch_related("tags", "files").get(id=project_id)
        total_downloads = project.download_count
        total_comments = project.comments.count()
        total_files = project.files.count()

        report = {
            "project_id": str(project_id),
            "title": project.title,
            "owner": project.owner.username,
            "status": project.status,
            "visibility": project.visibility,
            "total_downloads": total_downloads,
            "total_comments": total_comments,
            "total_files": total_files,
            "tags": list(project.tags.values_list("name", flat=True)),
            "created_at": project.created_at.isoformat(),
            "updated_at": project.updated_at.isoformat(),
        }
        logger.info("Report generated for project %s", project_id)
        return {"project_id": str(project_id), "status": "completed", "report": report}
    except Project.DoesNotExist:
        return {"error": "Project not found"}


@shared_task
def process_uploaded_file(file_id):
    from .models import ProjectFile

    try:
        project_file = ProjectFile.objects.select_related("project").get(id=file_id)
        file_size = project_file.file_size
        file_type = project_file.file_type

        result = {
            "file_id": str(file_id),
            "filename": project_file.original_filename,
            "file_type": file_type,
            "file_size": file_size,
            "status": "processed",
        }

        if file_type == "image":
            result["thumbnail_generated"] = False
            result["note"] = "Thumbnail generation not yet implemented"
        elif file_type == "pdf":
            result["page_count"] = None
            result["note"] = "PDF page counting not yet implemented"
        elif file_type == "zip":
            result["archive_contents"] = None
            result["note"] = "ZIP inspection not yet implemented"

        logger.info("Processed file %s (%s)", file_id, file_type)
        return result
    except ProjectFile.DoesNotExist:
        return {"error": "File not found"}
