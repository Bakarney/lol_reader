import argparse
import proc


if __name__ == '__main__':
    modes = ["overwrite", "append", "skip"]
    default_mode = "append"

    parser = argparse.ArgumentParser()
    parser.add_argument("--summoners_mode", "-sm", choices=modes, default=default_mode)
    parser.add_argument("--summoners_output", "-so", default="../results/summoners")
    parser.add_argument("--details_mode", "-dm", choices=modes, default=default_mode)
    parser.add_argument("--details_output", "-do", default="../results/details")
    parser.add_argument("--games_ids_mode", "-im", choices=modes, default=default_mode)
    parser.add_argument("--games_ids_output", "-io", default="../results/game_ids")
    parser.add_argument("--games_mode", "-gm", choices=modes, default=default_mode)
    parser.add_argument("--games_output", "-go", default="../results/games")

    args = parser.parse_args()
    summoners_mode = args.summoners_mode
    summoners_output = args.summoners_output
    details_mode = args.details_mode
    details_output = args.details_output
    games_ids_mode = args.games_ids_mode
    games_ids_output = args.games_ids_output
    games_mode = args.games_mode
    games_output = args.games_output

    print()
    print("Summoners_mode:", summoners_mode)
    print("Summoners_output:", summoners_output)
    print("Details_mode:", details_mode)
    print("Details_output:", details_output)
    print("Games_ids_mode", games_ids_mode)
    print("Games_ids_output", games_ids_output)
    print("Games_mode", games_mode)
    print("Games_output", games_output)
    print()

    proc.process(summoners_mode, summoners_output,
                 details_mode, details_output,
                 games_ids_mode, games_ids_output,
                 games_mode, games_output)
