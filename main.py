from astrbot.api.event.filter import event_message_type, EventMessageType
from astrbot.api.event import AstrMessageEvent
from astrbot.api.star import Context, Star, register
from astrbot.api.message_components import *
from collections import defaultdict
from typing import List
import random

@register("astrbot_plugin_repetition", "FengYing", "复读机插件", "1.0.0", "https://github.com/FengYing1314/astrbot_plugin_repetition")
class RepetitionPlugin(Star):
    def __init__(self, context: Context):
        super().__init__(context)
        self.last_messages = defaultdict(list)
        self.repeat_count = defaultdict(int)

    def get_message_identifier(self, message) -> str:
        """获取消息的唯一标识符"""
        result = []
        for msg in message:
            if isinstance(msg, Image):
                # 对于图片消息，使用文件名作为标识符
                result.append(f"image:{msg.file}")
            else:
                result.append(str(msg))
        return "".join(result)

    def rebuild_message_chain(self, message) -> List:
        """重建消息链，确保图片等媒体消息能正确发送"""
        new_chain = []
        for msg in message:
            if isinstance(msg, Image):
                # 对于图片消息，使用URL重新构建
                new_chain.append(Image.fromURL(msg.url))
            else:
                new_chain.append(msg)
        return new_chain

    @event_message_type(EventMessageType.ALL)
    async def on_message(self, event: AstrMessageEvent):
        '''自动复读相同的消息'''
        if "/" in event.message_obj.message_str:
            return
            
        session_id = event.unified_msg_origin
        current_message = event.message_obj.message
        
        if not current_message:
            return
        
        message_id = self.get_message_identifier(current_message)
        if message_id == self.last_messages[session_id]:
            self.repeat_count[session_id] += 1
            if self.repeat_count[session_id] == 1:
                # 修改为30%概率复读
                if random.random() < 0.3:
                    new_chain = self.rebuild_message_chain(current_message)
                    yield event.chain_result(new_chain)
                else:
                    yield event.plain_result("打断施法！")
        else:
            self.repeat_count[session_id] = 0
            
        self.last_messages[session_id] = message_id
