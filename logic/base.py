
class BaseGPT:

    def __init__(self,
                 chat_id: int):
        self.chat_id = chat_id
        self.cash


    async def _get_init_list(self):
        pass


    async def _get_item_data(self):
        pass

    async def _run_get_items_data(self):
        q_list = main_dict[chat_id]['quizz']['q_list']
        tasks = [gpt_q_data(chat_id, q) for q in q_list]
        await asyncio.gather(*tasks)
        main_dict[chat_id]['wait'] = False
