import argparse
import proc


if __name__ == '__main__':
    modes = ["overwrite", "append", "skip"]
    default_mode = "append"

    parser = argparse.ArgumentParser()
    parser.add_argument("--entries_mode", "-em", choices=modes, default=default_mode)
    parser.add_argument("--entries_output", "-eo", default="../results/entries")
    parser.add_argument("--summoners_mode", "-sm", choices=modes, default=default_mode)
    parser.add_argument("--summoners_output", "-so", default="../results/summoners")
    parser.add_argument("--games_ids_mode", "-gim", choices=modes, default=default_mode)
    parser.add_argument("--games_ids_output", "-gio", default="../results/game_ids")
    parser.add_argument("--games_mode", "-gm", choices=modes, default=default_mode)
    parser.add_argument("--games_output", "-go", default="../results/games")
    parser.add_argument("--extended_summoners_mode", "-esm", choices=modes, default=default_mode)
    parser.add_argument("--extended_summoners_output", "-eso", default="../results/extended_summoners")

    args = parser.parse_args()
    entries_mode = args.entries_mode
    entries_output = args.entries_output
    summoners_mode = args.summoners_mode
    summoners_output = args.summoners_output
    games_ids_mode = args.games_ids_mode
    games_ids_output = args.games_ids_output
    games_mode = args.games_mode
    games_output = args.games_output
    extended_summoners_mode = args.extended_summoners_mode
    extended_summoners_output = args.extended_summoners_output

    print()
    print("Entries_mode:", entries_mode)
    print("Entries_output:", entries_output)
    print("Summoners_mode:", summoners_mode)
    print("Summoners_output:", summoners_output)
    print("Games_ids_mode", games_ids_mode)
    print("Games_ids_output", games_ids_output)
    print("Games_mode", games_mode)
    print("Games_output", games_output)
    print("Extended_summoners_mode", extended_summoners_mode)
    print("Extended_summoners_output", extended_summoners_output)
    print()

    proc.process(entries_mode, entries_output,
                 summoners_mode, summoners_output,
                 games_ids_mode, games_ids_output,
                 games_mode, games_output,
                 extended_summoners_mode, extended_summoners_output)
