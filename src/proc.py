from tqdm import tqdm
from riotwatcher import LolWatcher, ApiError
import json
import os

import const


watcher = LolWatcher(const.api_key)


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
            os.mkdir(path)
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


def request_data(set_name: str, mode: str, output: str, function, params, opt_params=None):
    if opt_params is None:
        opt_params = {}

    params_sets = get_params(params)
    proc_bar = tqdm(params_sets,
                    bar_format="{desc} {percentage:3.0f}%|{bar}|{n_fmt}/{total_fmt}",
                    desc="Requesting " + set_name)

    stat = {
        "found": 0,
        "skipped": 0,
        "not found": 0
    }

    for params_set in proc_bar:
        path = os.path.join(output, *params_set[:-1]).replace("\\", "/")
        if not os.path.exists(path):
            os.makedirs(path)

        path += "/" + params_set[-1] + ".json"
        if os.path.exists(path) and mode != "overwrite":
            stat["skipped"] += 1
            continue

        try:
            response = function(*params_set, **opt_params)
            write_json(response, path)
            stat["found"] += 1
        except ApiError as e:
            stat["not found"] += 1
            with open("log.log", "a") as file:
                file.write(str(e) + "\n")
                file.write("-" * 100 + "\n")

    print("Requesting {} completed".format(set_name))
    print("Found:", stat["found"])
    print("Skipped:", stat["skipped"])
    print("Not found:", stat["not found"])
    print()


def flatten(struct):
    flat = []
    values = [i for i in struct.values()]
    if isinstance(values[0], dict):
        for i in values:
            flat += flatten(i)
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


def process(summoners_mode, summoners_output,
            details_mode, details_output,
            games_ids_mode, games_ids_output,
            games_mode, games_output):
    if os.path.exists("log.log"):
        os.remove("log.log")

    if summoners_mode != "skip":
        request_data("summoners", summoners_mode, summoners_output, watcher.league.entries,
                     {const.region: {const.queue: {tier: [division
                                                          for division in const.divisions]
                                                   for tier in const.tiers}}})

    if details_mode != "skip":
        summoners = read_struct(summoners_output)
        summoners = flatten(summoners)
        request_data("summoners details", details_mode, details_output, watcher.summoner.by_name,
                     {const.region: [i["summonerName"] for i in summoners]})

    if games_ids_mode != "skip":
        details = read_struct(details_output)
        details = flatten(details)
        request_data("games ids", games_ids_mode, games_ids_output, watcher.match.matchlist_by_puuid,
                     {const.region: [i["puuid"] for i in details]}, {"type": "ranked"})

    if games_mode != "skip":
        games_ids = read_struct(games_ids_output)
        games_ids = flatten(games_ids)
        games_ids = deduplicate(games_ids)
        request_data("games data", games_mode, games_output, watcher.match.by_id,
                     {const.region: [i for i in games_ids]})
