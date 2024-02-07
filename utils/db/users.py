from datetime import datetime
from typing import Optional, List

import pytz
from sqlalchemy import Column, Integer, String, ForeignKey, select, BigInteger, DateTime, func
from sqlalchemy.dialects.postgresql import Any
from sqlalchemy.exc import ProgrammingError
from sqlalchemy.orm import sessionmaker, relationship

from data import config
from .tariff import Tariffs
from .base import Base
from .product import Products

tz = pytz.timezone('Asia/Tashkent')
aware_datetime = datetime.now(tz)

# Определяем класс модели для таблицы пользователя
class Users(Base):
    __tablename__ = 'users'

    user_id = Column(BigInteger, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    phone = Column(String(25), nullable=True)
    lang = Column(String(255), nullable=True)
    # Внешний ключ для связи с Tariffs
    tariff_id = Column(Integer, ForeignKey('tariffs.id'), nullable=True)
    # Отношение с Tariffs
    tariffs = relationship("Tariffs", back_populates="user")
    created_at = Column(DateTime, default=datetime.now)

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
                                         has_tariff: Optional[bool] = None,
                                         language: Optional[str] = None) -> List:
        """
        Возвращает список пользователей на основе статуса наличия у них тарифа.

        :param language:
        :param session_maker: Сессия SQLAlchemy для доступа к базе данных.
        :param has_tariff: Если True, возвращает пользователей с тарифом.
                           Если False, возвращает пользователей без тарифа.
                           Если None, возвращает всех пользователей.
        :param language: Язык пользователей ('uzb', 'rus' или другой). Если None, язык не учитывается.
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
            users = result.scalars().all()
            # Применяем фильтр по языку, если он указан
            if language is not None:
                users = [user for user in users if user.lang == language]

            return users

    @staticmethod
    async def create_user(user_id: int,
                          name: str,
                          lang: str,
                          phone: str,
                          tariff_id: int,
                          session_maker: sessionmaker) -> None:
        async with session_maker() as session:
            async with session.begin():
                user = Users(
                    user_id=user_id,
                    name=name,
                    phone=phone,
                    tariff_id=tariff_id,
                    lang=lang,
                )
                try:
                    session.add(user)
                    await session.commit()  # Сохранить изменения
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
    async def get_available_courses_for_user(user_id: int, session_maker: sessionmaker):
        """
        Возвращает список доступных курсов для пользователя на основе его тарифа.

        :param user_id: ID пользователя
        :param session_maker: Фабрика сессий SQLAlchemy
        :return: Список доступных курсов
        """
        async with session_maker() as session:
            # Асинхронно получаем пользователя по ID
            result = await session.execute(select(Users).where(Users.user_id == user_id))
            user = result.scalars().one_or_none()

            # Проверяем, задан ли у пользователя тариф
            if user:
                # Получаем тариф пользователя отдельным запросом
                tariff_result = await session.execute(select(Tariffs).where(Tariffs.id == user.tariff_id))
                tariff = tariff_result.scalars().one_or_none()

                if tariff:
                    # Получаем продукты, связанные с тарифом пользователя
                    products_result = await session.execute(
                        select(Products).where(Products.tariff_id == tariff.id))
                    return products_result.scalars().all()

            return []  # Возвращаем пустой список, если у пользователя нет тарифа

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

    @staticmethod
    async def get_all_users_tariffs(session_maker: sessionmaker):
        """
        Получаем всех пользователей и их тарифы для отчёта в excel,
        без учёта администраторов.
        """
        async with (session_maker() as session):
            users_raw = await session.execute(
                select(Users, Tariffs).where(
                    ~Users.user_id.in_(config.ADMIN_ID)
                ).outerjoin(
                    Tariffs, Users.tariff_id == Tariffs.id
                ).order_by(
                    Users.created_at.desc()
                )
            )
            return users_raw.fetchall()
