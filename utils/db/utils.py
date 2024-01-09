from utils.db import Users


async def get_user_language(user_id, session_maker):
    user = await Users.get_user(user_id=user_id,
                                session_maker=session_maker)
    return user
