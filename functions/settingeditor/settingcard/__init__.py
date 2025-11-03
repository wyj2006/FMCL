import logging
import traceback
from typing import Any, Callable, Optional

from .setting_card import SettingCard


def dispatch_card(
    getter: Callable[[], Any],
    attr_getter: Callable[[str, Optional[Any]], Any],
    setter: Callable[[Any], None] = lambda *_: None,
    attr_setter: Callable[[str, Any], None] = lambda *_: None,
):
    from .bool_card import BoolCard
    from .default_card import DefaultCard
    from .dict_card import DictCard
    from .list_card import ListCard
    from .mirror_card import MirrorCard
    from .string_card import StringCard

    setting_card_name = attr_getter("setting_card", None)
    if setting_card_name != None:
        try:
            return MirrorCard(
                getter=getter,
                attr_getter=attr_getter,
                setter=setter,
                attr_setter=attr_setter,
            )
        except:  # source不存在或者其它问题
            logging.error(
                f"无法使用自定义的setting_card: {setting_card_name}: {traceback.format_exc()}"
            )

    value = getter()
    card_cls = DefaultCard
    match value:
        case bool():
            card_cls = BoolCard
        case str():
            card_cls = StringCard
        case list():
            card_cls = ListCard
        case dict():
            card_cls = DictCard
    return card_cls(getter, attr_getter, setter, attr_setter)
