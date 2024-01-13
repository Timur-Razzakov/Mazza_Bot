from sqlalchemy import Column, Integer, String, select, Text, Boolean, DateTime, func, ForeignKey
from sqlalchemy.dialects.postgresql import Any
from sqlalchemy.exc import ProgrammingError
from sqlalchemy.orm import sessionmaker, relationship

from .base import Base


class Tariffs(Base):
    __tablename__ = 'tariffs'

    id = Column(Integer, primary_key=True, autoincrement=True)
    tariff_name = Column(String(255), nullable=False)
    tariff_name_uzb = Column(String(255), nullable=True)
    description = Column(Text(), nullable=True)
    description_uzb = Column(Text(), nullable=True)
    price = Column(String(255), nullable=False)
    group_link = Column(String(255), nullable=True)
    created_at = Column(DateTime, server_default=func.now())

    # Отношение "один ко многим" с Product
    products = relationship("Products", back_populates="tariff")
    # Связь с User (обратная ссылка)
    user = relationship("Users", back_populates="tariffs", uselist=False)

    def __init__(self, tariff_name, group_link, tariff_name_uzb, price, description, **kw: Any):
        super().__init__(**kw)
        self.tariff_name = tariff_name
        self.tariff_name_uzb = tariff_name_uzb
        self.description = description
        self.group_link = group_link
        self.price = price

    @property
    def stats(self) -> str:
        """
        :return:
        """
        return ""

    def __str__(self) -> str:
        return f"<tariff:{self.tariff_name}>"

    def __repr__(self):
        return self.__str__()

    @staticmethod
    async def get_group_link(id: int, session_maker: sessionmaker):
        """
        Получить ссылку на группу по его id
        :param id:
        :param session_maker:
        :return:
        """
        async with session_maker() as session:
            async with session.begin():
                result = await session.execute(
                    select(Tariffs.group_link)
                    .filter(Tariffs.id == id)  # type: ignore
                )
                return result.scalars().one_or_none()

    @staticmethod
    async def get_tariff(id: int, session_maker: sessionmaker):
        """
        Получить тариф по его id
        :param id:
        :param session_maker:
        :return:
        """
        async with session_maker() as session:
            async with session.begin():
                result = await session.execute(
                    select(Tariffs.tariff_name)
                    .filter(Tariffs.id == id)  # type: ignore
                )
                return result.scalars().one_or_none()

    @staticmethod
    async def update_tariff(tariff_id: int, session_maker: sessionmaker, **update_fields):
        """
        Обновить данные тарифа.

        :param tariff_id: ID тарифа, данные которого нужно обновить.
        :param session_maker: Фабрика сессий SQLAlchemy.
        :param update_fields: Поля и их новые значения для обновления.
        """
        async with session_maker() as session:
            async with session.begin():
                # Найти тариф по ID
                tariff = await session.get(Tariffs, tariff_id)
                if tariff:
                    # Обновляем поля тарифа
                    for field, value in update_fields.items():
                        if hasattr(tariff, field):
                            setattr(tariff, field, value)
                    try:
                        # Сохраняем изменения
                        await session.commit()
                    except Exception as e:
                        # В случае ошибки откатываем изменения
                        session.rollback()
                        raise e
                else:
                    # Тариф не найден
                    raise ValueError(f"Тариф с таким {tariff_id} не найден!")

    @staticmethod
    async def get_group_name(tariff_name: str, session_maker: sessionmaker):
        """
        Получить тариф по его имени
        :param tariff_name:
        :param session_maker:
        :return:
        """
        async with session_maker() as session:
            async with session.begin():
                result = await session.execute(
                    select(Tariffs)
                    .filter(Tariffs.tariff_name == tariff_name)  # type: ignore
                )
                return result.scalars().one_or_none()

    @staticmethod
    async def get_all_tariffs(session_maker: sessionmaker):
        """
        Получить все тарифы
        :param session_maker:
        :return:
        """
        async with session_maker() as session:
            async with session.begin():
                result = await session.execute(select(Tariffs).distinct())
                tariff_name = [row[0] for row in result]
                return tariff_name

    @staticmethod
    async def create_tariff(tariff_name: str, group_link: str, tariff_name_uzb: str,
                            description_uzb: str, price: bool,
                            description: str,
                            session_maker: sessionmaker, ) -> None:
        async with session_maker() as session:
            async with session.begin():
                tariff = Tariffs(
                    tariff_name=tariff_name,
                    tariff_name_uzb=tariff_name_uzb,
                    description=description,
                    group_link=group_link,
                    description_uzb=description_uzb,
                    price=price,
                )
                try:
                    session.add(tariff)
                    await session.commit()  # Сохранить изменения
                except ProgrammingError as e:
                    session.rollback()  # Откатить изменения в случае ошибки
                    # TODO: add log
                    pass

    # Функция удаления записи из таблицы "tariff"
    @staticmethod
    async def delete_tariff_by_id(tariff_id: int, session_maker: sessionmaker):
        """
        Удалить тариф по его идентификатору.
        :param tariff_id:
        :param tariff_id: Идентификатор тарифа для удаления.
        :param session_maker: Фабрика сессий SQLAlchemy.
        """
        async with session_maker() as session:
            async with session.begin():
                tariff = await session.get(Tariffs, tariff_id)
                if tariff:
                    try:
                        await session.delete(tariff)
                        await session.commit()  # Сохранить изменения
                    except Exception as e:
                        session.rollback()  # Откатить изменения в случае ошибки
                        # TODO: Добавьте обработку ошибки или логирование
                else:
                    # Тариф с указанным идентификатором не найден
                    return "Тариф  не найден"

    @staticmethod
    async def get_tariff_by_id(tariff_id: int, session_maker: sessionmaker):
        """
        Получить тариф по его id
        :param tariff_id:
        :param session_maker:
        :return:
        """
        async with session_maker() as session:
            async with session.begin():
                tariff = await session.execute(
                    select(Tariffs)
                    .filter(Tariffs.id == tariff_id)  # type: ignore
                )
                return tariff.scalars().one_or_none()

    @staticmethod
    async def get_tariff_by_name_and_price(
            tariff_name: str,
            lang: str,
            session_maker: sessionmaker
    ):
        """
        Получить тариф по цене и имени учитывая язык пользователя
        :param tariff_name:
        :param price:
        :param lang:
        :param session_maker:
        :return:
        """
        tariff_name_field = 'tariff_name' if lang == 'ru' else 'tariff_name_uzb'
        condition = {
            tariff_name_field: tariff_name,
        }
        async with session_maker() as session:
            tariff = await session.execute(
                select(Tariffs).filter_by(
                    **condition
                )
            )
            return tariff.scalars().one_or_none()

    @staticmethod
    async def get_tariff_from_name(tariff_name: str, session_maker: sessionmaker):
        """
        Получить тариф по его имени
        :param tariff_name:
        :param session_maker:
        :return:
        """
        async with session_maker() as session:
            async with session.begin():
                result = await session.execute(
                    select(Tariffs)
                    .filter(Tariffs.tariff_name == tariff_name)  # type: ignore
                )
                return result.scalars().one_or_none()
