from sqlalchemy import Column, Integer, String, select, Text, Boolean, DateTime, func, ForeignKey
from sqlalchemy.dialects.postgresql import Any
from sqlalchemy.exc import ProgrammingError
from sqlalchemy.orm import sessionmaker, relationship

from .base import Base


class Tariffs(Base):
    __tablename__ = 'tariffs'

    id = Column(Integer, primary_key=True, autoincrement=True)
    tariffs_name = Column(String(255), nullable=False)
    # tariffs_name_uzb = Column(String(255), nullable=True)
    description = Column(Text(), nullable=True)
    # description_uzb = Column(Text(), nullable=True)
    price = Column(Integer(), nullable=False)
    created_at = Column(DateTime, server_default=func.now())

    # Отношение "один ко многим" с Product
    products = relationship("Products", back_populates="tariff")
    # Связь с User (обратная ссылка)
    user = relationship("Users", back_populates="tariffs", uselist=False)

    def __init__(self, tariffs_name, price, description, **kw: Any):
        super().__init__(**kw)
        self.tariffs_name = tariffs_name
        self.description = description
        self.price = price

    @property
    def stats(self) -> str:
        """
        :return:
        """
        return ""

    def __str__(self) -> str:
        return f"<tariff:{self.tariffs_name}>"

    def __repr__(self):
        return self.__str__()

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
                    select(Tariffs.tariffs_name)
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
    async def get_tariff_from_name(tariffs_name: str, session_maker: sessionmaker):
        """
        Получить тариф по его имени
        :param tariffs_name:
        :param session_maker:
        :return:
        """
        async with session_maker() as session:
            async with session.begin():
                result = await session.execute(
                    select(Tariffs)
                    .filter(Tariffs.tariffs_name == tariffs_name)  # type: ignore
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
                tariffs_name = [row[0] for row in result]
                return tariffs_name

    @staticmethod
    async def create_tariff(tariffs_name: str, price: bool, description: str,
                            session_maker: sessionmaker, ) -> None:
        async with session_maker() as session:
            async with session.begin():
                tariff = Tariffs(
                    tariffs_name=tariffs_name,
                    description=description,
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
