import discord


class Page:
    def __init__(
        self, title, msg, count, page_num, total_pages=None, next=None, prev=None
    ):
        self.title = title
        self.msg = msg
        self.count = count
        self.page_num = page_num
        self.total_pages = total_pages
        self.next = next
        self.prev = prev

    def getEmbed(self):

        self.embed = discord.Embed(
            title=self.title,
            description=self.msg,
            color=discord.Color.blue(),
        )

        self.embed.set_footer(
            text=f"Page {self.page_num}{f' of {self.total_pages}' if self.total_pages else ''}"
        )

        return self.embed

    def hasNext(self):
        return self.next is not None

    def hasPrev(self):
        return self.prev is not None
