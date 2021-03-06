from chat.models import TalkingRoom, TalkStatus
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync


def start_talk(talking_room):
    """
    talkの開始処理(talk_ticketのstatus変更, 双方にnotification送信)
    :param talking_room:
    :return:
    """
    talking_room.speaker_ticket.status = TalkStatus.TALKING
    talking_room.speaker_ticket.save()
    talking_room.listener_ticket.status = TalkStatus.TALKING
    talking_room.listener_ticket.save()

    send_talk_notification(
        recipient=talking_room.speaker_ticket.owner,
        context={'room_id': str(talking_room.id), 'status': 'start'}
    )
    send_talk_notification(
        recipient=talking_room.listener_ticket.owner,
        context={'room_id': str(talking_room.id), 'status': 'start'}
    )


def create_talking_room(speaker_ticket, listener_ticket):
    """
    talking roomの作成
    :param speaker_ticket:
    :param listener_ticket:
    :return:
    """
    talking_room = TalkingRoom(
        speaker_ticket=speaker_ticket,
        listener_ticket=listener_ticket,
    )
    talking_room.save()
    return talking_room


# 循環importを防ぐため、NotificationV2Consumer内ではなく、ここに記述
def send_talk_notification(recipient, context=None):
    """
    ex) NotificationV2Consumer.send_talk_notification(recipient=user, context={'room_id': str(room_id), 'status': 'start' or 'end'})
    """
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)('notification_v2_{}'.format(str(recipient.id)), {
        'type': 'notice_talk',
        'context': context if context is not None else None,
    })
