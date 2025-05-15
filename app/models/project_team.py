from .deps import  Field,  SQLModel


class ProjectTeamLink(SQLModel, table=True):
    """Tabla intermedia para relación muchos-a-muchos entre Project y Worker"""
    project_id: int = Field(foreign_key="project.id", primary_key=True)
    worker_id: int = Field(foreign_key="worker.id", primary_key=True)
    role: str = Field(default="Team Member")  # Rol específico en el proyecto
