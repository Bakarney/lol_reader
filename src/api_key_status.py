import riotwatcher

import const


if __name__ == '__main__':
    watchers = [riotwatcher.LolWatcher(key) for key in const.api_keys]
    for i, watcher in enumerate(watchers):
        try:
            response = watcher.league.entries("na1", "RANKED_SOLO_5x5", "GOLD", "I")
            print(str(i) + " - Active")
        except riotwatcher.ApiError as e:
            print(str(i) + " - Inactive")
