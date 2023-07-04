from datetime import datetime

from asyncio import Event
from fastapi import HTTPException, status, Depends, Path, WebSocket
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from .router import router
from src.types.user import UserForm
from src.types import Token
from ..database import User, ChatMessage
from .dependecies import create_token, SETTINGS, auth


new_message = Event()


@router.post('/register')
async def register(form: UserForm):
    form.hash()
    async with User.session() as session:
        user = User(**form.dict())
        session.add(user)
        try:
            await session.commit()
        except IntegrityError:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='email is not unique')
        else:
            raise HTTPException(status_code=status.HTTP_202_ACCEPTED, detail='success')


@router.post('/login', response_model=Token)
async def login(form: UserForm):
    async with User.session() as session:
        user = await session.scalar(
            select(User)
            .filter_by(email=form.email)
        )
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='user not found')
    if not form.verify(user.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='invalid password')
    return Token(
        token_type=SETTINGS.TOKEN_TYPE,
        access_token=create_token(user.email)
    )


class Message(BaseModel):
    message: str = Field(max_length=1024)


class MessageDetail(Message):
    chat_id: int
    author_id: int
    date_created: datetime
    id: int

    class Config:
        orm_mode = True


@router.get('/chat/{chat_id}')
async def chat(auth: User = Depends(auth), chat_id: int = Path()):
    async with ChatMessage.session() as session:
        messages = await session.scalars(
            select(ChatMessage)
            .filter_by(chat_id=chat_id)
            .order_by(ChatMessage.date_created.asc())
        )
        return [MessageDetail.from_orm(message) for message in messages]


@router.post('/chat/{chat_id}')
async def chat(message: Message, auth: User = Depends(auth), chat_id: int = Path()):
    async with ChatMessage.session() as session:
        chat_message = ChatMessage(
            chat_id=chat_id,
            author_id=auth.id,
            message=message.message
        )
        session.add(chat_message)
        try:
            await session.commit()
        except IntegrityError:
            raise HTTPException(400)
        else:
            new_message.set()
            await session.refresh(chat_message)
            return MessageDetail.from_orm(chat_message)


@router.websocket('/ws/chat/{chat_id}/{access_token}')
async def ws_chat(ws: WebSocket, chat_id: int = Path(), access_token: str = Path()):
    from asyncio import sleep
    await ws.accept()

    async with ChatMessage.session() as session:
        messages = await session.scalars(
            select(ChatMessage)
            .filter_by(chat_id=chat_id)
            .order_by(ChatMessage.date_created.asc())
        )
        messages = messages.all()
        last_message_id = messages[-1].id
        await ws.send_json([MessageDetail.from_orm(message).json() for message in messages])

    while ...:
        while not new_message.is_set():
            await sleep(1)
        else:
            new_message.clear()

        async with ChatMessage.session() as session:
            messages = await session.scalars(
                select(ChatMessage)
                .filter_by(chat_id=chat_id)
                .filter(ChatMessage.id > last_message_id)
                .order_by(ChatMessage.date_created.asc())
            )
            messages = messages.all()
            if messages:
                last_message_id = messages[-1].id
                await ws.send_json([MessageDetail.from_orm(message).json() for message in messages])
        await sleep(1)
