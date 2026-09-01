import html


def esc(value) -> str:
    return html.escape(str(value or ""))


def duration_text(seconds: int) -> str:
    if not seconds:
        return "Unknown"

    minutes, sec = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)

    if hours:
        return f"{hours}:{minutes:02}:{sec:02}"

    return f"{minutes}:{sec:02}"


def user_link(user) -> str:
    if not user:
        return "Unknown"

    name = esc(
        " ".join(
            item
            for item in [user.first_name, user.last_name]
            if item
        )
        or user.username
        or "User"
    )

    return f'<a href="tg://user?id={user.id}">{name}</a>'
