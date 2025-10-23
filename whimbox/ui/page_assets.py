from whimbox.ui.page import UIPage, TitlePage
from whimbox.ui.ui_assets import *

page_loading = UIPage(check_icon=[IconUILoading1, IconUILoading2])

page_main = UIPage(check_icon=IconPageMainFeature)
page_bigmap = UIPage(check_icon=IconUIBigmap)
# page_esc = UIPage(check_icon=TextPageEscFeature)
page_esc = TitlePage("美鸭梨")
page_daily_task = UIPage(check_icon=TextDailyTaskFeature)
page_zxxy = UIPage(check_icon=IconUIZxxy)
page_xhsy = UIPage(check_icon=IconUIXhsy)
page_dress = UIPage(check_icon=ButtonWardrobeDressDIY)
page_ability = UIPage(check_icon=TextWardrobeAbilityBattle)
# page_huanjing = UIPage(check_icon=TextHuanjingFeature)
page_huanjing = TitlePage("幻境挑战")
# page_huanjing_jihua = UIPage(check_icon=TextHuanjingJihuaFeature)
page_huanjing_jihua = TitlePage("素材激化幻境")
# page_huanjing_bless = UIPage(check_icon=TextHuanjingBlessFeature)
page_huanjing_bless = TitlePage("祝福闪光幻境")
# page_huanjing_monster = UIPage(check_icon=TextHuanjingMonsterFeature)
page_huanjing_monster = TitlePage("魔物试炼幻境")
# page_photo = UIPage(check_icon=TextPhotoFeature)
page_photo = TitlePage("大喵相机")
# page_monthly_pass = UIPage(check_icon=TextMonthlyPassFeature)
page_monthly_pass = TitlePage("奇迹之旅")

ui_pages = [
    page_main,
    page_bigmap,
    page_daily_task,
    page_zxxy,
    page_xhsy,
    page_dress,
    page_ability,
    page_esc,
    page_huanjing,
    page_huanjing_jihua,
    page_huanjing_bless,
    page_huanjing_monster,
    page_photo,
    page_monthly_pass,
]

page_main.link('m', page_bigmap)
page_main.link('esc', page_esc)
page_main.link('l', page_daily_task)
page_main.link('c', page_dress)
page_main.link('p', page_photo)
page_main.link('j', page_monthly_pass)

page_bigmap.link('m', page_main)

page_esc.link('esc', page_main)

page_daily_task.link('esc', page_main)
page_daily_task.link(ButtonHuanjingGo, page_huanjing)
page_daily_task.link(ButtonZxxyEntrance, page_zxxy)
page_daily_task.link(ButtonXhsyEntrance, page_xhsy)

page_huanjing.link('esc', page_daily_task)
page_huanjing.link(TextHuanjingJihuaEntrace, page_huanjing_jihua)
page_huanjing.link(TextHuanjingBlessEntrace, page_huanjing_bless)
page_huanjing.link(TextHuanjingMonsterEntrace, page_huanjing_monster)

page_huanjing_jihua.link('esc', page_huanjing)
page_huanjing_bless.link('esc', page_huanjing)
page_huanjing_monster.link('esc', page_huanjing)

page_zxxy.link("esc", page_daily_task)

page_xhsy.link("esc", page_daily_task)

page_dress.link("esc", page_main)
page_dress.link(TextWardrobeAbilityTab, page_ability)

page_ability.link("esc", page_main)

page_photo.link("esc", page_main)

page_monthly_pass.link("esc", page_main)