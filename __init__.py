# coding=utf-8
import random
import traceback
from os.path import join

from yuiChyan import CQEvent, FunctionException
from yuiChyan.service import Service
from yuiChyan.util import FreqLimiter, DailyNumberLimiter
from .Life import Life
from .PicClass import *

# 每个人的指令冷却 | 默认10秒
lmt = FreqLimiter(10)

# 每个人的每天次数限制 | 默认每天2次
full_limit = DailyNumberLimiter(2)

FULL_EXCEED_NOTICE = f'您今天已经重来过{full_limit.max}次人生了，要寄了，请明早5点后再来哦！'

sv = Service('人生重来模拟器', help_cmd='人生重来帮助')


def genp(prop):
    ps = []
    # for _ in range(4):
    #     ps.append(min(prop, 8))
    #     prop -= ps[-1]
    tmp = prop
    while True:
        for i in range(0, 4):
            if i == 3:
                ps.append(tmp)
            else:
                if tmp >= 10:
                    ps.append(random.randint(0, 10))
                else:
                    ps.append(random.randint(0, tmp))
                tmp -= ps[-1]
        if ps[3] < 10:
            break
        else:
            tmp = prop
            ps.clear()
    return {
        'CHR': ps[0],
        'INT': ps[1],
        'STR': ps[2],
        'MNY': ps[3]
    }


@sv.on_match(('/remake', '人生重来'))
async def remake(bot, ev: CQEvent):
    if not lmt.check(ev.group_id):
        raise FunctionException(ev, f'本群人生重来功能冷却中(剩余 {int(lmt.left_time(ev.group_id)) + 1}秒)')
    if not full_limit.check(ev.user_id):
        raise FunctionException(ev, FULL_EXCEED_NOTICE)
    lmt.start_cd(ev.group_id)
    full_limit.increase(ev.user_id)

    pic_list = []
    mes_list = []

    Life.load(join(FILE_PATH, 'data'))
    while True:
        life = Life()
        life.setErrorHandler(lambda e: traceback.print_exc())
        life.setTalentHandler(lambda ts: random.choice(ts).id)
        life.setPropertyHandler(genp)
        flag = life.choose()
        if flag:
            break

    name = ev['sender']['card'] or ev['sender']['nickname']
    choice = 0
    person = name + '本次重生的基本信息如下：\n\n【你的天赋】\n'
    for t in life.talent.talents:
        choice = choice + 1
        person = person + str(choice) + '、天赋：【' + t.name + '】' + ' 效果:' + t.desc + '\n'

    person = person + '\n【基础属性】\n'
    person = person + '   美貌值:' + str(life.property.CHR) + '  '
    person = person + '智力值:' + str(life.property.INT) + '  '
    person = person + '体质值:' + str(life.property.STR) + '  '
    person = person + '财富值:' + str(life.property.MNY) + '  '
    pic_list.append('这是' + name + '本次轮回的基础属性和天赋:')
    pic_list.append(ImgText(person).draw_text())

    await bot.send(ev, '你的命运正在重启....', at_sender=True)

    res = life.run()  # 命运之轮开始转动
    mes = '\n'.join('\n'.join(x) for x in res)
    pic_list.append('这是' + name + '本次轮回的生平:')
    pic_list.append(ImgText(mes).draw_text())

    _sum = life.property.generate_summary()  # 你的命运之轮到头了
    pic_list.append('这是' + name + '本次轮回的评价:')
    pic_list.append(ImgText(_sum).draw_text())

    for img in pic_list:
        data = {
            'type': 'node',
            'data': {
                'name': '色图机器人',
                'uin': '2854196310',
                'content': img
            }
        }
        mes_list.append(data)

    await bot.send_group_forward_msg(group_id=ev['group_id'], messages=mes_list)
