from datetime import datetime, timedelta

from src.post.comment.models import Comment
from tests.conftest import async_session_market


async def test_comments_daily_breakdown(auth_client, created_post):
    async with async_session_market() as session:
        comments = []
        dates = [
            datetime.now() - timedelta(days=2),
            datetime.now() - timedelta(days=1),
            datetime.now(),
        ]

        left = 1
        for day, date in enumerate(dates):
            for i in range(3):
                comment = Comment(
                    post_id=created_post["id"],
                    content=f"Test comment {i + 1} for date {day + 1}",
                    created_at=date,
                    is_blocked=(i % 2 == 0),
                    user_id=1,
                    lft=left,
                    rgt=left + 1,
                    level=1,
                )
                comments.append(comment)
                left += 2

        session.add_all(comments)
        await session.commit()

    date_from = (datetime.now() - timedelta(days=3)).strftime("%Y-%m-%d")
    date_to = datetime.now().strftime("%Y-%m-%d")

    response = await auth_client.get(
        "/comments-daily-breakdown", params={"date_from": date_from, "date_to": date_to}
    )

    assert response.status_code == 200, "Request to comments breakdown failed"
    daily_stats = response.json()

    assert (
        len(daily_stats) == 3
    ), "There should be 3 entries in daily stats for the selected dates"

    for stat in daily_stats:
        assert "date" in stat, "Each stat entry should have a date"
        assert "total_comments" in stat, "Each stat entry should have total_comments"
        assert (
            "blocked_comments" in stat
        ), "Each stat entry should have blocked_comments"

        assert (
            stat["total_comments"] == 3
        ), f"Total comments for {stat['date']} should be 3"
        assert (
            stat["blocked_comments"] == 2
        ), f"Blocked comments for {stat['date']} should be 2 (as every second comment is blocked)"
