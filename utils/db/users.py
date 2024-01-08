from typing import Optional, List

from sqlalchemy import Column, Integer, String, ForeignKey, select
from sqlalchemy.dialects.postgresql import Any
from sqlalchemy.exc import ProgrammingError
from sqlalchemy.orm import sessionmaker, relationship

from .base import Base
from .product import Products


# Определяем класс модели для таблицы пользователя
class Users(Base):
    __tablename__ = 'users'

    user_id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    phone = Column(String(25), nullable=True)
    lang = Column(String(255), nullable=True)
    # Внешний ключ для связи с Tariffs
    tariff_id = Column(Integer, ForeignKey('tariffs.id'), nullable=True)
    # Отношение с Tariffs
    tariffs = relationship("Tariffs", back_populates="user")

    def __init__(self, user_id, phone, tariff_id, name, lang, **kw: Any):
        super().__init__(**kw)
        self.name = name
        self.phone = phone
        self.user_id = user_id
        self.tariff_id = tariff_id
        self.lang = lang

    @property
    def stats(self) -> str:
        """

        :return:
        """
        return ""

    def __str__(self) -> str:
        return f"<User:{self.user_id}>"

    def __repr__(self):
        return self.__str__()

    @staticmethod
    async def get_users_by_tariff_status(session_maker: sessionmaker,
                                         has_tariff: Optional[bool] = None) -> List:
        """
        Возвращает список пользователей на основе статуса наличия у них тарифа.

        :param session_maker: Сессия SQLAlchemy для доступа к базе данных.
        :param has_tariff: Если True, возвращает пользователей с тарифом.
                           Если False, возвращает пользователей без тарифа.
                           Если None, возвращает всех пользователей.
        :return: Список пользователей.
        """
        async with session_maker() as session:  # session теперь AsyncSession
            if has_tariff is not None:
                if has_tariff:
                    # Возвращаем пользователей с тарифом
                    query = select(Users).where(Users.tariff_id.isnot(None))
                else:
                    # Возвращаем пользователей без тарифа
                    query = select(Users).where(Users.tariff_id.is_(None))
            else:
                # Возвращаем всех пользователей
                query = select(Users)
            result = await session.execute(query)
            return result.scalars().all()

    @staticmethod
    async def create_user(user_id: int,
                          name: str,
                          lang: str,
                          phone: str,
                          tariff_id: int,
                          session_maker: sessionmaker) -> None:
        async with session_maker() as session:
            async with session.begin():
                order = Users(
                    user_id=user_id,
                    name=name,
                    phone=phone,
                    tariff_id=tariff_id,
                    lang=lang,
                )
                try:
                    session.add(order)
                    session.commit()  # Сохранить изменения
                except ProgrammingError as e:
                    session.rollback()  # Откатить изменения в случае ошибки
                    # TODO: add log
                    pass

    @staticmethod
    async def get_user(user_id: int, session_maker: sessionmaker):
        """
        Получить язык пользователя по user_id
        :param user_id:
        :param session_maker:
        :return:
        """
        async with session_maker() as session:
            async with session.begin():
                result = await session.execute(
                    select(Users.lang)
                    .filter(Users.user_id == user_id)  # type: ignore
                )
                return result.scalars().one_or_none()

    @staticmethod
    def get_available_courses_for_user(user_id, session):
        """
        Возвращает список доступных курсов для пользователя на основе его тарифа.

        :param user_id: ID пользователя
        :param session: Сессия SQLAlchemy для доступа к базе данных
        :return: Список доступных курсов
        """
        # Найти пользователя по ID (переписать на 2 версию)
        user = session.query(Users).filter(Users.user_id == user_id).first()

        # Проверить, задан ли у пользователя тариф
        if user and user.tariffs:
            # Получить продукты, связанные с тарифом пользователя
            available_products = session.query(Products).filter(Products.tariff_id == user.tariffs.id).all()
            return available_products

        return []

    @staticmethod
    async def get_users_by_language(language: str, session_maker: sessionmaker, ):
        async with session_maker() as session:
            try:
                result = await session.execute(select(Users).filter(Users.lang == language))
                return result.scalars().all()  # Получаем всех пользователей с заданным языком
            except Exception as e:
                print(f"Ошибка при получении пользователей: {e}")
                return []

    @staticmethod
    async def update_user(user_id: int, session_maker: sessionmaker, **update_fields):
        """
        Обновить данные пользователя.

        :param user_id: ID пользователя, чьи данные нужно обновить.
        :param session_maker: Фабрика сессий SQLAlchemy.
        :param update_fields: Поля и их новые значения для обновления.
        """
        async with session_maker() as session:
            async with session.begin():
                # Найти пользователя по ID
                user = await session.get(Users, user_id)
                if user:
                    # Обновляем поля пользователя
                    for field, value in update_fields.items():
                        if hasattr(user, field):
                            setattr(user, field, value)
                    try:
                        # Сохраняем изменения
                        await session.commit()
                    except Exception as e:
                        # В случае ошибки откатываем изменения
                        session.rollback()
                        raise e
                else:
                    # Пользователь не найден
                    raise ValueError(f"Пользователь с таким {user_id} не найден!!")

    @staticmethod
    async def get_user_by_id(user_id: int, session_maker: sessionmaker):
        async with session_maker() as session:
            user = await session.execute(
                select(Users).filter_by(user_id=user_id)
            )
            return user.scalars().one_or_none()
