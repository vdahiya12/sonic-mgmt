def add_cont_warm_reboot_args(parser):
    '''
    Adding arguments required for continuous warm-reboot test case
    '''
    parser.addoption(
        "--continuous_reboot_count",
        action="store",
        type=int,
        default=10,
        help="Number of iterations of warm-reboot",
    )

    parser.addoption(
        "--continuous_reboot_delay",
        action="store",
        type=int,
        default=300,
        help="Delay period in seconds between subsequent reboots",
    )

    parser.addoption(
        "--enable_continuous_io",
        action="store",
        type=bool,
        default=False,
        help="Enable continuous IO",
    )
