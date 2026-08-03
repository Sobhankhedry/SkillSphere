from abc import ABC, abstractmethod
from uuid import UUID

from domain.entities.user import ProfileEntity, UserEntity


class UserRepository(ABC):
    @abstractmethod
    def get_by_id(self, user_id: UUID) -> UserEntity | None: ...

    @abstractmethod
    def get_by_email(self, email: str) -> UserEntity | None: ...

    @abstractmethod
    def get_by_username(self, username: str) -> UserEntity | None: ...

    @abstractmethod
    def create(
        self, email: str, username: str, password: str, **kwargs
    ) -> UserEntity: ...

    @abstractmethod
    def update(self, user_id: UUID, **kwargs) -> UserEntity: ...

    @abstractmethod
    def get_profile(self, user_id: UUID) -> ProfileEntity | None: ...

    @abstractmethod
    def update_profile(self, user_id: UUID, **kwargs) -> ProfileEntity: ...
