# core/engine.py

import random
from data.game_data import PLATFORMS, CONTENT_TYPES, NEWS_EVENTS
from sound.sound import play


class GameState:
    """
    Represents the state of the game, including the current day, energy,
    """
    def __init__(self, total_days):
        self.total_days = total_days
        self.day = 1
        self.energy = 4
        self.followers = 0
        self.ad_revenue = 0
        self.platform = None
        self.news = []
        self.used_news = set()


    def start_day(self):
        """
        Start a new day in the game. This method resets the energy and
        :return:
        """
        self.energy = 4
        self._maybe_add_news()
        self._expire_old_news()


    def _maybe_add_news(self):
        """
        Check if we need to add new news events. If there are less than 2
        :return:
        """
        if len(self.news) >= 2:
            return
        unused = [n for n in NEWS_EVENTS if n['headline'] not in self.used_news]
        if not unused:
            return
        boost_pool = [n for n in unused if n.get("type") != "detriment"]
        detriment_pool = [n for n in unused if n.get("type") == "detriment"]
        choices = random.sample(boost_pool, min(6, len(boost_pool))) + \
                  random.sample(detriment_pool, min(4, len(detriment_pool)))
        random.shuffle(choices)
        if choices:
            news = choices[0]
            news['start_day'] = self.day
            self.news.append(news)
            self.used_news.add(news['headline'])
            play("news_in")


    def _expire_old_news(self):
        """
        Check if any news events have expired. If so, remove them from the
        :return:
        """
        expired = [n for n in self.news if self.day - n['start_day'] >= n['duration']]
        if expired:
            for n in expired:
                play("news_out")
        self.news = [n for n in self.news if self.day - n['start_day'] < n['duration']]


    def next_day(self):
        """
        Move to the next day in the game. This method increments the day
        :return:
        """
        self.day += 1
        self.start_day()


    def is_game_over(self):
        """
        Check if the game is over.
        :return:
        """
        return self.day > self.total_days


    def set_platform(self, platform):
        """
        Set the current platform for the game. This method is used when selecting a platform
        :param platform:
        :return:
        """
        self.platform = platform


    def post_content(self, content_type):
        """
        Post content to the selected platform. This method checks if the player has enough energy
        :param content_type:
        :return:
        """
        if self.energy < CONTENT_TYPES[content_type]['energy']:
            return "Not enough energy."
        self.energy -= CONTENT_TYPES[content_type]['energy']
        base = CONTENT_TYPES[content_type]['base_followers']
        multiplier = self._calculate_multiplier(content_type)
        gained = int(base * multiplier)
        self.followers += gained
        # Apply follower penalty from detrimental events
        for n in self.news:
            if n.get("follower_loss_percent"):
                loss = int(self.followers * n["follower_loss_percent"])
                self.followers -= loss
                return (
                    f"You gained {gained} followers.\n"
                    f"You lost {loss} due to a controversy."
                )
        revenue = self._calculate_revenue(content_type, multiplier)
        self.ad_revenue += revenue
        return f"You gained {gained} followers and earned ${revenue:.2f}"


    def _calculate_multiplier(self, content_type):
        """
        Calculate the multiplier for the content type based on the current news events.
        :param content_type:
        :return:
        """
        mult = 1.0
        for n in self.news:
            if (n['content_type'] is None or n['content_type'] == content_type) and \
               (n['platform'] is None or n['platform'] == self.platform):
                mult *= n.get('multiplier', 1.0)
        return mult


    def _calculate_revenue(self, content_type, multiplier):
        """
        Calculate the ad revenue based on the current news events.
        :param content_type:
        :param multiplier:
        :return:
        """
        for n in self.news:
            if n.get("block_revenue") and (n['content_type'] == content_type or n['platform'] == self.platform):
                return 0.0
        return round(0.01 * self.followers * multiplier, 2)