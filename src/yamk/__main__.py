from yamk.command.make import MakeCommand
from yamk.lib.cli import parse_args


def main() -> None:
    args = parse_args()
    MakeCommand(
        bare=args.bare,
        cookbook=args.cookbook,
        cookbook_type=args.cookbook_type,
        dry_run=args.dry_run,
        echo_override=args.echo_override,
        extra=args.extra,
        force_make=args.force_make,
        print_timing_report=args.print_timing_report,
        retries=args.retries,
        shell=args.shell,
        target=args.target,
        up_to_date=args.up_to_date,
        variables=args.variables,
        verbosity=args.verbosity,
    ).make()
