import pytest
from src.gitlab_api import ProjectData

# Testidataa
test_project_data = {
    "name": "Test Project",
    "project_id": 1234,
    "description": "This is a test project.",
    "created_at": "2023-01-01T12:00:00Z",
    "last_activity_at": "2023-06-01T12:00:00Z",
}

def test_get_name():
    project = ProjectData(**test_project_data)
    assert project.get_name() == "Test Project"

def test_get_id():
    project = ProjectData(**test_project_data)
    assert project.get_id() == 1234

def test_get_description():
    project = ProjectData(**test_project_data)
    assert project.get_description() == "This is a test project."

def test_get_creation_date():
    project = ProjectData(**test_project_data)
    assert project.get_creation_date() == "2023-01-01T12:00:00Z"

def test_get_update_date():
    project = ProjectData(**test_project_data)
    assert project.get_update_date() == "2023-06-01T12:00:00Z"