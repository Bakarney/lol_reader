from tqdm import tqdm
from riotwatcher import LolWatcher, ApiError
import json
import os
import shutil

import const


class ChiefWatcher:
    def __init__(self, *watchers: LolWatcher, **kwargs):
        super().__init__(**kwargs)
        self.watcher_pool = watchers
        self.queue = -1

    def get_watcher(self) -> LolWatcher:
        self.queue += 1
        if self.queue >= len(self.watcher_pool):
            self.queue = 0
        return self.watcher_pool[self.queue]

    def entries_by_elo(self, *args, **opt_params):
        watcher = self.get_watcher()
        return watcher.league.entries(*args, **opt_params)

    def account_by_name(self, *args, **opt_params):
        watcher = self.get_watcher()
        return watcher.summoner.by_name(*args, **opt_params)

    def matchlist_by_puuid(self, *args, **opt_params):
        watcher = self.get_watcher()
        return watcher.match.matchlist_by_puuid(*args, **opt_params)

    def match_by_id(self, *args, **opt_params):
        watcher = self.get_watcher()
        return watcher.match.by_id(*args, **opt_params)

    def entry_by_name(self, *args, **opt_params):
        watcher = self.get_watcher()
        summoner_id = watcher.summoner.by_name(*args, **opt_params)["id"]
        response = watcher.league.by_summoner(args[0], summoner_id)
        return response


def read_struct(path: str) -> dict or list:
    data = {}
    if os.path.isdir(path):
        for i in os.listdir(path):
            new_path = os.path.join(path, i).replace("\\", "/")
            if os.path.isdir(new_path):
                data[i] = read_struct(os.path.join(path, i).replace("\\", "/"))
            else:
                data[i] = json.load(open(new_path, "r"))
    return data


def write_json(data: list or dict, file: str):
    if "/" in file:
        path = "/".join(file.split("/")[:-1])
        if not os.path.exists(path):
            os.makedirs(path)
    with open(file, "w") as f:
        json.dump(data, f)


def get_params(params, prev_params=None):
    if prev_params is None:
        prev_params = []
    if isinstance(params, dict):
        params_set = []
        for k, v in params.items():
            res = get_params(v, prev_params + [k])
            for i in res:
                params_set.append(i)
    else:
        params_set = [prev_params + [j] for j in params]
    return params_set


def format_stat(stat: dict):
    return ", ".join([k + ": " + str(v) for k, v in stat.items()])


def request_data(set_name: str, mode: str, output: str, function, params, opt_params=None):
    if opt_params is None:
        opt_params = {}

    stat = {
        "found": 0,
        "skipped": 0,
        "not found": 0
    }

    params_sets = get_params(params)
    proc_bar = tqdm(params_sets,
                    bar_format="{desc}: {percentage:3.0f}%|{bar}|{n_fmt}/{total_fmt}{postfix}",
                    desc="Requesting " + set_name,
                    postfix=format_stat(stat))

    for params_set in proc_bar:
        path = os.path.join(output, *params_set[:-1]).replace("\\", "/")
        if not os.path.exists(path):
            os.makedirs(path)

        path += "/" + params_set[-1] + ".json"
        if os.path.exists(path) and mode != "overwrite":
            stat["skipped"] += 1
            proc_bar.set_postfix_str(format_stat(stat))
            continue

        try:
            response = function(*params_set, **opt_params)
            write_json(response, path)
            stat["found"] += 1
            proc_bar.set_postfix_str(format_stat(stat))
        except ApiError as e:
            stat["not found"] += 1
            proc_bar.set_postfix_str(format_stat(stat))
            with open("log.log", "a", encoding="utf-8") as file:
                file.write(str(e) + "\n")
                file.write("Params: " + str(params_set) + ", " + str(opt_params) + "\n")
                file.write("-" * 100 + "\n")

    print("Requesting {} completed".format(set_name))
    print("Found:", stat["found"])
    print("Skipped:", stat["skipped"])
    print("Not found:", stat["not found"])
    print()


def unpack(struct):
    flat = []
    values = [i for i in struct.values()]
    if isinstance(values[0], dict):
        for i in values:
            flat += unpack(i)
    elif isinstance(values[0], list):
        for i in values:
            flat += i
    else:
        flat.append(struct)
    return flat


def deduplicate(data: list):
    deduped = []
    for i in data:
        if i not in deduped:
            deduped.append(i)
    return deduped


def process(entries_mode, entries_output,
            summoners_mode, summoners_output,
            games_ids_mode, games_ids_output,
            games_mode, games_output,
            extended_summoners_mode, extended_summoners_output):
    chief = ChiefWatcher(*[LolWatcher(i) for i in const.api_keys])

    if os.path.exists("log.log"):
        os.remove("log.log")

    if entries_mode != "skip":
        request_data("entries", entries_mode, entries_output, chief.entries_by_elo,
                     {const.region: {const.queue: {tier: [division for division in const.divisions]
                                                   for tier in const.tiers}}})

    if summoners_mode != "skip":
        summoners = read_struct(entries_output)
        summoners = unpack(summoners)
        request_data("summoners", summoners_mode, summoners_output, chief.account_by_name,
                     {const.region: [i["summonerName"] for i in summoners]})

    if games_ids_mode != "skip":
        details = read_struct(summoners_output)
        details = unpack(details)
        request_data("games ids", games_ids_mode, games_ids_output, chief.matchlist_by_puuid,
                     {const.region: [i["puuid"] for i in details]}, {"type": "ranked"})

    if games_mode != "skip":
        games_ids = read_struct(games_ids_output)
        games_ids = unpack(games_ids)
        games_ids = deduplicate(games_ids)
        request_data("games data", games_mode, games_output, chief.match_by_id,
                     {const.region: games_ids[:10000]})

    if extended_summoners_mode != "skip":
        if extended_summoners_mode == "overwrite" and os.path.exists(extended_summoners_output):
            shutil.rmtree(extended_summoners_output)

        games_data = read_struct(games_output)
        participants = [j["summonerName"] for i in games_data[const.region].values()
                        for j in i["info"]["participants"]]
        participants = deduplicate(participants)
        request_data("extended summoners", extended_summoners_mode, extended_summoners_output, chief.entry_by_name,
                     {const.region: participants})
