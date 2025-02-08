    from telethon import TelegramClient, events
    from telethon.tl.functions.channels import GetParticipantsRequest
    from telethon.tl.types import ChannelParticipantsSearch

    api_id = '22544328'
    api_hash = 'c9b5f81a263933e3fecce08cc719fa00'
    phone = '+919702270708'

    client = TelegramClient('session_name', api_id, api_hash)

    async def get_all_users(channel_username):
        await client.start(phone)
        channel = await client.get_entity(channel_username)
        
        all_participants = []
        offset = 0
        limit = 200

        while True:
            participants = await client(GetParticipantsRequest(
                channel, ChannelParticipantsSearch(''), offset, limit, hash=0
            ))
            if not participants.users:
                break
            all_participants.extend(participants.users)
            offset += len(participants.users)
            
            for user in participants.users:
                print(f"User: {user.first_name} {user.last_name} | Username: @{user.username} | ID: {user.id}")

    async def main():
        target_channels = [
            '@amazonindiaassociates',
            '@realearnkaro',
            '@techglaredeals'
        ]
        
        for channel in target_channels:
            print(f"\nGetting users from {channel}")
            await get_all_users(channel)

    client.loop.run_until_complete(main())
