from types import SimpleNamespace

from bot.services.telegram.context_builder import ReplyContextBuilder


def make_message(text, reply=None):
    return SimpleNamespace(text=text, caption=None, reply_to_message=reply)


def test_build_ancestor_context_uses_bounded_chain():
    root = make_message('root msg')
    mid = make_message('mid msg', reply=root)
    target = make_message('target msg', reply=mid)
    builder = ReplyContextBuilder(max_messages=3, max_chars=100)
    result = builder.build_ancestor_context(target)
    assert result == '[context 1] root msg\n[context 2] mid msg'


def test_build_ancestor_context_respects_char_budget():
    root = make_message('a' * 40)
    target = make_message('target', reply=root)
    builder = ReplyContextBuilder(max_messages=3, max_chars=10)
    assert builder.build_ancestor_context(target) == ''
