import logging
from random import randrange

from discord.ext import commands

logger = logging.getLogger(__name__)


class Abuse(commands.Cog):
    """
    All about me!
    """

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener("on_message")
    async def respond_to_abuse(self, message):
        replies = [
            "get a dog up ya, cunt",
            "Can I help you? Do you want a time out?",
            "No u",
            "How about Nooooooooo!",
            "Thats a horrible thing to say about your mother",
            "I know you are, but what am I",
            "I'm sorry, did you say something? I don't speak moron",
            "Command accepted! Now commencing with your time out",
            "You kiss your mother with that mouth?!?",
            "Thats what she said",
            "You're so ugly, you scared the crap out of the toilet.",
            "It's better to let someone think you are an Idiot than to open your mouth and prove it.",
            "Your birth certificate is an apology letter from the condom factory.",
            "The only way you'll ever get laid is if you crawl up a chicken's ass and wait.",
            "You're so fake, Barbie is jealous.",
            "I’m jealous of people that don’t know you!",
            "Brains aren't everything. In your case they're nothing.",
            "I don't know what makes you so stupid, but it really works.",
            "I can explain it to you, but I can’t understand it for you.",
            "Roses are red violets are blue, God made me pretty, what happened to you?",
            "Calling you an idiot would be an insult to all the stupid people.",
            "You, sir, are an oxygen thief!",
            "I'd slap you, but that would be animal abuse.",
            "They say opposites attract. I hope you meet someone who is good-looking, intelligent, and cultured.",
            "Stop trying to be a smart ass, you're just an ass.",
            "I'm busy now. Can I ignore you some other time?",
            "Why don't you slip into something more comfortable... like a coma.",
            "To make you laugh on Saturday, I need to you joke on Wednesday.",
            "Pardon me, but you've obviously mistaken me for someone who gives a damn.",
            "https://media.tenor.com/x8v1oNUOmg4AAAAC/rickroll-roll.gif"
        ]
        rand = randrange(0, len(replies) - 1)
        if message.mention_everyone or message.author.id == self.bot.user.id:
            return
        try:
            if self.bot.user.mentioned_in(message):
                if message.author.id == 318309023478972417:
                    await message.reply("https://media.tenor.com/x8v1oNUOmg4AAAAC/rickroll-roll.gif")
                else:
                    await message.reply(replies[rand])
        except Exception:
            pass


def setup(bot):
    bot.add_cog(Abuse(bot))
