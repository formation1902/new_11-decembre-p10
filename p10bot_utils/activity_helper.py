#
# Utilitaire pour la creation de la reponse (reply)
#
from datetime import datetime

from botbuilder.schema import Activity, ActivityTypes
from botbuilder.schema import ChannelAccount
from botbuilder.schema import ConversationAccount
from datetime import datetime


def create_activity_reply(activity: Activity, text: str = None, locale: str = None):
    print("INFO : [Activity-HELPER : create_activity_reply] called")
    from_property = ChannelAccount(
        id   = getattr(activity.recipient, "id", None),
        name = getattr(activity.recipient, "name", None),
    )
    print("\t ---> [Activity-HELPER : create_activity_reply] from_property = ",from_property)
    recipient = ChannelAccount(
        id   = activity.from_property.id, 
        name = activity.from_property.name
    )
    print("\t ---> [Activity-HELPER : create_activity_reply] recipient = ",recipient)
    conversation = ConversationAccount(
        is_group    = activity.conversation.is_group,
        id          = activity.conversation.id,
        name        = activity.conversation.name,
    )
    print("\t ---> [Activity-HELPER : create_activity_reply] conversation = ",conversation)
    reply =  Activity(
        type            = ActivityTypes.message,
        timestamp       = datetime.utcnow(),
        from_property   = from_property,
        recipient       = recipient,
        reply_to_id     = activity.id,
        service_url     = activity.service_url,
        channel_id      = activity.channel_id,
        conversation=conversation,
        text=text or "",
        locale=locale or "",
        attachments=[],
        entities=[],
    )
    print("\t ---> [Activity-HELPER : create_activity_reply] reply = ",reply)
    print("INFO : [Activity-HELPER : create_activity_reply] done")
    return reply
