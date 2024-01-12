from sqlalchemy import (Column, Integer, String, select,
                        Text, Boolean, ForeignKey, or_)
from sqlalchemy.dialects.postgresql import Any
from sqlalchemy.exc import ProgrammingError
from sqlalchemy.orm import sessionmaker, relationship

from .base import Base


class Products(Base):
    __tablename__ = 'products'

    id = Column(Integer, primary_key=True, autoincrement=True)
    product_name = Column(String(255), nullable=False)
    product_name_uzb = Column(String(255), nullable=True)
    free = Column(Boolean, default=False, nullable=False)
    description = Column(Text(), nullable=True)
    description_uzb = Column(Text(), nullable=True)
    tariff_id = Column(Integer, ForeignKey('tariffs.id'), nullable=True)  # Внешний ключ
    file_id = Column(String(500), nullable=True)
    file_type = Column(String(255), nullable=True)
    # Определение отношения к таблице "Tariffs"
    tariff = relationship("Tariffs", back_populates="products")

    def __init__(self, product_name, file_id, file_type, product_name_uzb, free, tariff_id, description,
                 description_uzb,
                 **kw: Any):
        super().__init__(**kw)
        self.product_name = product_name
        self.product_name_uzb = product_name_uzb
        self.tariff_id = tariff_id
        self.description = description
        self.description_uzb = description_uzb
        self.file_id = file_id
        self.file_type = file_type
        self.free = free

    @property
    def stats(self) -> str:
        """

        :return:
        """
        return ""

    def __str__(self) -> str:
        return f"<product:{self.product_name}>"

    def __repr__(self):
        return self.__str__()

    @staticmethod
    async def get_product(id: int, session_maker: sessionmaker):
        """
        Получить продукт по его id
        :param id:
        :param session_maker:
        :return:
        """
        async with session_maker() as session:
            async with session.begin():
                result = await session.execute(
                    select(Products)
                    .filter(Products.id == id).first()  # type: ignore
                )
                return result

    @staticmethod
    async def get_product_from_name(product_name: str, session_maker: sessionmaker):
        """
        Получить продукт по его имени
        :param product_name:
        :param session_maker:
        :return:
        """
        async with session_maker() as session:
            async with session.begin():
                result = await session.execute(
                    select(Products)
                    .filter(
                        or_(Products.product_name == product_name, Products.product_name_uzb == product_name))
                    # type: ignore
                )
                return result.scalars().one_or_none()

    @staticmethod
    async def get_all_products(session_maker: sessionmaker):
        """
        Получить все продукты
        :param session_maker:
        :return:
        """
        async with session_maker() as session:
            async with session.begin():
                result = await session.execute(select(Products).distinct())
                product_name = [row[0] for row in result]
                return product_name

    @staticmethod
    async def get_all_free_products(session_maker: sessionmaker):
        """
        Получить все бесплатные продукты
        :param session_maker: Фабрика сессий SQLAlchemy
        :return: Список бесплатных продуктов
        """
        async with session_maker() as session:
            async with session.begin():
                # Добавляем фильтр для выбора только бесплатных продуктов
                result = await session.execute(
                    select(Products).filter(Products.free == True).distinct()
                )
                # Возможно, вам нужно изменить способ доступа к данным в зависимости от структуры Products
                product_name = [row[0] for row in result]
                return product_name

    @staticmethod
    async def create_product(product_name: str, file_id: str, file_type: str, product_name_uzb: str,
                             description_uzb: str,
                             free: bool,
                             tariff_id: int, description: str,
                             session_maker: sessionmaker, ) -> None:
        async with session_maker() as session:
            async with session.begin():
                product = Products(
                    product_name=product_name,
                    product_name_uzb=product_name_uzb,
                    tariff_id=tariff_id,
                    description=description,
                    description_uzb=description_uzb,
                    free=free,
                    file_id=file_id,
                    file_type=file_type,
                )
                try:
                    session.add(product)
                    await session.commit()  # Сохранить изменения
                except ProgrammingError as e:
                    session.rollback()  # Откатить изменения в случае ошибки
                    # TODO: add log
                    pass

    # Функция удаления записи из таблицы "countries"
    @staticmethod
    async def delete_product_by_id(product_id: int, session_maker: sessionmaker):
        """
        Удалить страну по её идентификатору.
        :param product_id:
        :param product_id: Идентификатор продукта для удаления.
        :param session_maker: Фабрика сессий SQLAlchemy.
        """
        async with session_maker() as session:
            async with session.begin():
                country = await session.get(Products, product_id)
                if country:
                    try:
                        await session.delete(country)
                        await session.commit()  # Сохранить изменения
                    except Exception as e:
                        session.rollback()  # Откатить изменения в случае ошибки
                        # TODO: Добавьте обработку ошибки или логирование
                else:
                    # Продукт с указанным идентификатором не найден
                    return "Продукт  не найдена"

    @staticmethod
    async def update_product(product_id: int, session_maker: sessionmaker, **update_fields):
        """
        Обновить данные продукта.

        :param product_id: ID продукта, данные которого нужно обновить.
        :param session_maker: Фабрика сессий SQLAlchemy.
        :param update_fields: Поля и их новые значения для обновления.
        """
        async with session_maker() as session:
            async with session.begin():
                # Найти продукт по ID
                product = await session.get(Products, product_id)
                if product:
                    # Обновляем поля продукта
                    for field, value in update_fields.items():
                        if hasattr(product, field):
                            setattr(product, field, value)
                    try:
                        # Сохраняем изменения
                        await session.commit()
                    except Exception as e:
                        # В случае ошибки откатываем изменения
                        session.rollback()
                        raise e
                else:
                    # Продукт не найден
                    raise ValueError(f"Продукт с таким {product_id} не найден!")
