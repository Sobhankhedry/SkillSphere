from dataclasses import dataclass
from uuid import UUID


@dataclass
class UserEntity:
    id: UUID
    email: str
    username: str
    first_name: str = ""
    last_name: str = ""
    role: str = "user"
    is_active: bool = True
    email_verified: bool = False

    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}".strip()


@dataclass
class ProfileEntity:
    id: UUID
    user_id: UUID
    bio: str = ""
    avatar: str | None = None
    github_link: str = ""
    linkedin_link: str = ""
