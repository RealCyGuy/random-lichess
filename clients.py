import berserk


class Bots(berserk.clients.Bots):
    def decline_challenge(self, challenge_id, reason="generic"):
        """Decline an incoming challenge.

        :param str challenge_id: ID of a challenge
        :param str reason: reason for declining
        :return: success
        :rtype: bool
        """
        path = f"api/challenge/{challenge_id}/decline"
        payload = {
            "reason": reason
        }
        return self._r.post(path, json=payload)["ok"]


class Client(berserk.Client):
    def __init__(self, session=None, base_url=None, pgn_as_default=False):
        super().__init__(session, base_url, pgn_as_default)
        self.bots = Bots(session, base_url)
