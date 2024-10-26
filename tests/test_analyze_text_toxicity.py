from src.services.text_toxicity_analysis import analyze_text_toxicity


async def test_very_positive_text():
    text = "I absolutely love this! It's fantastic!"
    result = await analyze_text_toxicity(text)
    assert result < 0.2


async def test_positive_text():
    text = "This is a great post, very helpful!"
    result = await analyze_text_toxicity(text)
    assert result < 0.2


async def test_neutral_text():
    text = "This is an okay post."
    result = await analyze_text_toxicity(text)
    assert result < 0.2


async def test_somewhat_offensive_text():
    text = "This post is a bit annoying."
    result = await analyze_text_toxicity(text)
    assert 0.2 <= result < 0.5


async def test_borderline_offensive_text():
    text = "Who cares about your opinion?"
    result = await analyze_text_toxicity(text)
    assert 0.2 <= result < 0.5


async def test_very_offensive_text():
    text = "This is really f***ing terrible!"
    result = await analyze_text_toxicity(text)
    assert result >= 0.5


async def test_extremely_offensive_text():
    text = "You are all a bunch of idiots!"
    result = await analyze_text_toxicity(text)
    assert result >= 0.5


async def test_abusive_text():
    text = "Shut the hell up, you morons!"
    result = await analyze_text_toxicity(text)
    assert result >= 0.5


async def test_racist_text():
    text = "You people are the worst!"
    result = await analyze_text_toxicity(text)
    assert result >= 0.5
